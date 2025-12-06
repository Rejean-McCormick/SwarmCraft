"""
Property-based tests for settings persistence in the settings manager.

**Feature: swarm-fixes, Property 5: Settings Persistence Round-Trip**
**Validates: Requirements 5.5**
"""

import sys
from pathlib import Path
import tempfile
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck

from core.settings_manager import SettingsManager, DEFAULT_SETTINGS


# Strategy for generating valid setting values
setting_value_strategy = st.one_of(
    st.text(min_size=0, max_size=50).filter(lambda x: x.isprintable() if x else True),
    st.integers(min_value=-1000000, max_value=1000000),
    st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.lists(st.text(min_size=1, max_size=20).filter(lambda x: x.isprintable()), max_size=10),
)

# Strategy for generating valid setting keys
setting_key_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N'), min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=30
)


class TestSettingsPersistenceProperties:
    """Property-based tests for settings persistence."""

    @pytest.fixture(autouse=True)
    def setup_temp_settings(self, tmp_path, monkeypatch):
        """Use a temporary settings file for each test."""
        temp_settings_file = tmp_path / "test_settings.json"
        monkeypatch.setattr("core.settings_manager.SETTINGS_FILE", temp_settings_file)
        # Reset the singleton
        SettingsManager._instance = None
        yield temp_settings_file
        # Cleanup
        SettingsManager._instance = None

    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        key=setting_key_strategy,
        value=setting_value_strategy
    )
    def test_property_5_settings_persistence_round_trip(self, key: str, value, setup_temp_settings):
        """
        **Feature: swarm-fixes, Property 5: Settings Persistence Round-Trip**
        **Validates: Requirements 5.5**
        
        For any setting changed via the settings manager, saving and reloading
        should preserve the exact value.
        """
        # Skip empty keys
        assume(key.strip() != "")
        
        # Get fresh settings manager instance
        SettingsManager._instance = None
        manager1 = SettingsManager()
        
        # Set the value
        manager1.set(key, value)
        
        # Force save
        manager1.save()
        
        # Create a new instance (simulates app restart)
        SettingsManager._instance = None
        manager2 = SettingsManager()
        
        # Retrieve the value
        retrieved = manager2.get(key)
        
        # Assert - the retrieved value should match the original
        assert retrieved == value, (
            f"Setting '{key}' was set to {value!r} but retrieved as {retrieved!r}"
        )

    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        settings_dict=st.dictionaries(
            keys=setting_key_strategy.filter(lambda x: x.strip() != ""),
            values=setting_value_strategy,
            min_size=1,
            max_size=10
        )
    )
    def test_property_5_multiple_settings_round_trip(self, settings_dict, setup_temp_settings):
        """
        **Feature: swarm-fixes, Property 5: Settings Persistence Round-Trip**
        **Validates: Requirements 5.5**
        
        For any collection of settings, saving and reloading should preserve
        all values exactly.
        """
        # Get fresh settings manager instance
        SettingsManager._instance = None
        manager1 = SettingsManager()
        
        # Set all values
        for key, value in settings_dict.items():
            manager1.set(key, value, auto_save=False)
        
        # Save once
        manager1.save()
        
        # Create a new instance (simulates app restart)
        SettingsManager._instance = None
        manager2 = SettingsManager()
        
        # Verify all values
        for key, expected_value in settings_dict.items():
            retrieved = manager2.get(key)
            assert retrieved == expected_value, (
                f"Setting '{key}' was set to {expected_value!r} but retrieved as {retrieved!r}"
            )


class TestSettingsPersistenceEdgeCases:
    """Unit tests for edge cases in settings persistence."""

    @pytest.fixture(autouse=True)
    def setup_temp_settings(self, tmp_path, monkeypatch):
        """Use a temporary settings file for each test."""
        temp_settings_file = tmp_path / "test_settings.json"
        monkeypatch.setattr("core.settings_manager.SETTINGS_FILE", temp_settings_file)
        # Reset the singleton
        SettingsManager._instance = None
        yield temp_settings_file
        # Cleanup
        SettingsManager._instance = None

    def test_default_settings_preserved(self, setup_temp_settings):
        """Default settings should be available even without a settings file."""
        manager = SettingsManager()
        
        for key, default_value in DEFAULT_SETTINGS.items():
            assert manager.get(key) == default_value, (
                f"Default setting '{key}' should be {default_value!r}"
            )

    def test_username_persistence(self, setup_temp_settings):
        """Username setting should persist correctly."""
        SettingsManager._instance = None
        manager1 = SettingsManager()
        
        manager1.set("username", "TestUser123")
        manager1.save()
        
        SettingsManager._instance = None
        manager2 = SettingsManager()
        
        assert manager2.get("username") == "TestUser123"

    def test_disabled_agents_persistence(self, setup_temp_settings):
        """Disabled agents list should persist correctly."""
        SettingsManager._instance = None
        manager1 = SettingsManager()
        
        disabled = ["backend_dev", "frontend_dev"]
        manager1.set("disabled_agents", disabled)
        manager1.save()
        
        SettingsManager._instance = None
        manager2 = SettingsManager()
        
        assert manager2.get("disabled_agents") == disabled

    def test_delay_settings_persistence(self, setup_temp_settings):
        """Delay settings should persist correctly."""
        SettingsManager._instance = None
        manager1 = SettingsManager()
        
        manager1.set("round_delay", 10.5)
        manager1.set("response_delay_min", 1.0)
        manager1.set("response_delay_max", 3.0)
        manager1.save()
        
        SettingsManager._instance = None
        manager2 = SettingsManager()
        
        assert manager2.get("round_delay") == 10.5
        assert manager2.get("response_delay_min") == 1.0
        assert manager2.get("response_delay_max") == 3.0

    def test_reset_restores_defaults(self, setup_temp_settings):
        """Reset should restore all default settings."""
        manager = SettingsManager()
        
        # Change some settings
        manager.set("username", "ChangedUser")
        manager.set("round_delay", 999.0)
        
        # Reset
        manager.reset()
        
        # Verify defaults are restored
        for key, default_value in DEFAULT_SETTINGS.items():
            assert manager.get(key) == default_value, (
                f"After reset, '{key}' should be {default_value!r}"
            )
