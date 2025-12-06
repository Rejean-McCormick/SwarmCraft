"""
Property-based tests for role resolution in the agents module.

**Feature: swarm-fixes, Property 1: Role Resolution Consistency**
**Feature: swarm-fixes, Property 2: Role Resolution Backwards Compatibility**
**Validates: Requirements 1.1, 1.2**
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from hypothesis import given, strategies as st, settings

from agents import (
    AGENT_CLASSES,
    DISPLAY_NAME_TO_ROLE,
    resolve_role,
)


class TestRoleResolutionProperties:
    """Property-based tests for role resolution."""

    @settings(max_examples=100)
    @given(st.sampled_from(list(DISPLAY_NAME_TO_ROLE.keys())))
    def test_property_1_role_resolution_consistency(self, display_name: str):
        """
        **Feature: swarm-fixes, Property 1: Role Resolution Consistency**
        **Validates: Requirements 1.1, 1.2**
        
        For any valid display name in DISPLAY_NAME_TO_ROLE, calling resolve_role
        should return the corresponding role key that exists in AGENT_CLASSES.
        """
        # Act
        role_key = resolve_role(display_name)
        
        # Assert - the returned role key must exist in AGENT_CLASSES
        assert role_key in AGENT_CLASSES, (
            f"resolve_role('{display_name}') returned '{role_key}' "
            f"which is not in AGENT_CLASSES"
        )
        
        # Assert - the returned role key must match the expected mapping
        expected_role = DISPLAY_NAME_TO_ROLE[display_name.lower().strip()]
        assert role_key == expected_role, (
            f"resolve_role('{display_name}') returned '{role_key}' "
            f"but expected '{expected_role}'"
        )

    @settings(max_examples=100)
    @given(st.sampled_from(list(AGENT_CLASSES.keys())))
    def test_property_2_role_resolution_backwards_compatibility(self, role_key: str):
        """
        **Feature: swarm-fixes, Property 2: Role Resolution Backwards Compatibility**
        **Validates: Requirements 1.2**
        
        For any valid role key in AGENT_CLASSES, calling resolve_role should
        return that same role key (case-insensitive).
        """
        # Act
        resolved = resolve_role(role_key)
        
        # Assert - should return the same role key
        assert resolved == role_key.lower(), (
            f"resolve_role('{role_key}') returned '{resolved}' "
            f"but expected '{role_key.lower()}'"
        )

    @settings(max_examples=100)
    @given(st.sampled_from(list(AGENT_CLASSES.keys())))
    def test_property_2_case_insensitive(self, role_key: str):
        """
        **Feature: swarm-fixes, Property 2: Role Resolution Backwards Compatibility**
        **Validates: Requirements 1.2**
        
        Role resolution should be case-insensitive for role keys.
        """
        # Test various case variations
        variations = [
            role_key.lower(),
            role_key.upper(),
            role_key.capitalize(),
        ]
        
        for variant in variations:
            resolved = resolve_role(variant)
            assert resolved == role_key.lower(), (
                f"resolve_role('{variant}') returned '{resolved}' "
                f"but expected '{role_key.lower()}'"
            )


class TestRoleResolutionEdgeCases:
    """Unit tests for edge cases in role resolution."""

    def test_invalid_role_raises_value_error(self):
        """Unknown role names should raise ValueError with helpful message."""
        with pytest.raises(ValueError) as exc_info:
            resolve_role("unknown_agent")
        
        error_msg = str(exc_info.value)
        assert "Unknown role" in error_msg
        assert "unknown_agent" in error_msg
        # Should list valid options
        assert "backend_dev" in error_msg or "Valid role keys" in error_msg

    def test_whitespace_handling(self):
        """Role resolution should handle leading/trailing whitespace."""
        # Test with whitespace around display name
        result = resolve_role("  codey mcbackend  ")
        assert result == "backend_dev"
        
        # Test with whitespace around role key
        result = resolve_role("  backend_dev  ")
        assert result == "backend_dev"

    def test_all_display_names_resolve(self):
        """All display names in the mapping should resolve correctly."""
        for display_name, expected_role in DISPLAY_NAME_TO_ROLE.items():
            result = resolve_role(display_name)
            assert result == expected_role, (
                f"Display name '{display_name}' resolved to '{result}' "
                f"but expected '{expected_role}'"
            )

    def test_all_role_keys_resolve(self):
        """All role keys should resolve to themselves."""
        for role_key in AGENT_CLASSES.keys():
            result = resolve_role(role_key)
            assert result == role_key, (
                f"Role key '{role_key}' resolved to '{result}' "
                f"but expected '{role_key}'"
            )
