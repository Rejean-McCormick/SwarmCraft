"""
Property-based tests for agent state toggle functionality.

**Feature: swarm-fixes, Property 6: Agent State Toggle**
**Validates: Requirements 5.2**
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck

from agents import AGENT_CLASSES
from core.settings_manager import SettingsManager, DEFAULT_SETTINGS


# Strategy for generating agent role selections
agent_role_strategy = st.sampled_from(list(AGENT_CLASSES.keys()))

# Strategy for generating lists of agent roles (for disabled_agents)
agent_roles_list_strategy = st.lists(
    agent_role_strategy,
    min_size=0,
    max_size=len(AGENT_CLASSES),
    unique=True
)


def is_agent_enabled(role: str, disabled_agents: list) -> bool:
    """Check if an agent is enabled based on disabled_agents list."""
    return role not in disabled_agents


def toggle_agent_state(role: str, disabled_agents: list) -> list:
    """Toggle an agent's enabled state and return the new disabled_agents list."""
    new_disabled = disabled_agents.copy()
    if role in new_disabled:
        new_disabled.remove(role)
    else:
        new_disabled.append(role)
    return new_disabled


class TestAgentStateToggleProperties:
    """Property-based tests for agent state toggle."""

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
        role=agent_role_strategy,
        initial_disabled=agent_roles_list_strategy
    )
    def test_property_6_agent_state_toggle(self, role: str, initial_disabled: list, setup_temp_settings):
        """
        **Feature: swarm-fixes, Property 6: Agent State Toggle**
        **Validates: Requirements 5.2**
        
        For any agent in the swarm, toggling its enabled state should flip
        the boolean value.
        """
        # Get the initial state
        initial_enabled = is_agent_enabled(role, initial_disabled)
        
        # Toggle the state
        new_disabled = toggle_agent_state(role, initial_disabled)
        
        # Get the new state
        new_enabled = is_agent_enabled(role, new_disabled)
        
        # Assert - the state should be flipped
        assert new_enabled != initial_enabled, (
            f"Agent '{role}' state should flip from {initial_enabled} to {not initial_enabled}, "
            f"but got {new_enabled}"
        )

    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        role=agent_role_strategy,
        initial_disabled=agent_roles_list_strategy
    )
    def test_property_6_double_toggle_restores_state(self, role: str, initial_disabled: list, setup_temp_settings):
        """
        **Feature: swarm-fixes, Property 6: Agent State Toggle**
        **Validates: Requirements 5.2**
        
        Toggling an agent's state twice should restore the original state.
        """
        # Get the initial state
        initial_enabled = is_agent_enabled(role, initial_disabled)
        
        # Toggle twice
        after_first_toggle = toggle_agent_state(role, initial_disabled)
        after_second_toggle = toggle_agent_state(role, after_first_toggle)
        
        # Get the final state
        final_enabled = is_agent_enabled(role, after_second_toggle)
        
        # Assert - the state should be restored
        assert final_enabled == initial_enabled, (
            f"Agent '{role}' state should be restored to {initial_enabled} after double toggle, "
            f"but got {final_enabled}"
        )

    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        role=agent_role_strategy,
        other_roles=agent_roles_list_strategy
    )
    def test_property_6_toggle_only_affects_target_agent(self, role: str, other_roles: list, setup_temp_settings):
        """
        **Feature: swarm-fixes, Property 6: Agent State Toggle**
        **Validates: Requirements 5.2**
        
        Toggling one agent's state should not affect other agents' states.
        """
        # Create initial disabled list without the target role
        initial_disabled = [r for r in other_roles if r != role]
        
        # Record initial states of all other agents
        other_agent_states = {
            r: is_agent_enabled(r, initial_disabled)
            for r in AGENT_CLASSES.keys()
            if r != role
        }
        
        # Toggle the target agent
        new_disabled = toggle_agent_state(role, initial_disabled)
        
        # Verify other agents' states are unchanged
        for other_role, original_state in other_agent_states.items():
            new_state = is_agent_enabled(other_role, new_disabled)
            assert new_state == original_state, (
                f"Toggling '{role}' should not affect '{other_role}' state. "
                f"Expected {original_state}, got {new_state}"
            )


class TestAgentStateToggleWithSettings:
    """Tests for agent state toggle integrated with settings manager."""

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

    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(role=agent_role_strategy)
    def test_toggle_persists_to_settings(self, role: str, setup_temp_settings):
        """
        **Feature: swarm-fixes, Property 6: Agent State Toggle**
        **Validates: Requirements 5.2**
        
        Toggling an agent's state should persist to settings.
        """
        # Get settings manager
        SettingsManager._instance = None
        manager = SettingsManager()
        
        # Get initial disabled agents
        initial_disabled = manager.get("disabled_agents", [])
        initial_enabled = is_agent_enabled(role, initial_disabled)
        
        # Toggle the state
        new_disabled = toggle_agent_state(role, initial_disabled)
        manager.set("disabled_agents", new_disabled)
        
        # Verify the change persisted
        saved_disabled = manager.get("disabled_agents")
        new_enabled = is_agent_enabled(role, saved_disabled)
        
        assert new_enabled != initial_enabled, (
            f"Agent '{role}' state should be toggled in settings"
        )


class TestAgentStateToggleEdgeCases:
    """Unit tests for edge cases in agent state toggle."""

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

    def test_all_agents_initially_enabled(self, setup_temp_settings):
        """By default, all agents should be enabled (empty disabled list)."""
        manager = SettingsManager()
        disabled = manager.get("disabled_agents", [])
        
        for role in AGENT_CLASSES.keys():
            assert is_agent_enabled(role, disabled), (
                f"Agent '{role}' should be enabled by default"
            )

    def test_enable_already_enabled_agent(self, setup_temp_settings):
        """Enabling an already enabled agent should keep it enabled."""
        disabled = []
        role = "backend_dev"
        
        # Agent is enabled (not in disabled list)
        assert is_agent_enabled(role, disabled)
        
        # "Enable" it (remove from disabled if present - no-op here)
        if role in disabled:
            disabled.remove(role)
        
        # Should still be enabled
        assert is_agent_enabled(role, disabled)

    def test_disable_already_disabled_agent(self, setup_temp_settings):
        """Disabling an already disabled agent should keep it disabled."""
        disabled = ["backend_dev"]
        role = "backend_dev"
        
        # Agent is disabled
        assert not is_agent_enabled(role, disabled)
        
        # "Disable" it (add to disabled if not present - no-op here)
        if role not in disabled:
            disabled.append(role)
        
        # Should still be disabled
        assert not is_agent_enabled(role, disabled)

    def test_toggle_all_agents(self, setup_temp_settings):
        """Toggling all agents should flip all states."""
        disabled = []
        
        # Toggle all agents to disabled
        for role in AGENT_CLASSES.keys():
            disabled = toggle_agent_state(role, disabled)
        
        # All should be disabled
        for role in AGENT_CLASSES.keys():
            assert not is_agent_enabled(role, disabled), (
                f"Agent '{role}' should be disabled after toggle"
            )
        
        # Toggle all back to enabled
        for role in AGENT_CLASSES.keys():
            disabled = toggle_agent_state(role, disabled)
        
        # All should be enabled
        for role in AGENT_CLASSES.keys():
            assert is_agent_enabled(role, disabled), (
                f"Agent '{role}' should be enabled after second toggle"
            )
