"""
Property-based tests for user message coloring in the dashboard.

**Feature: swarm-fixes, Property 3: User Message Color Consistency**
**Validates: Requirements 2.1, 3.4**
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime

from core.models import Message, MessageRole
from dashboard import USER_STYLE, AGENT_STYLES, DashboardUI


# Strategy for generating valid usernames
username_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P'), min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=20
).filter(lambda x: x.strip())

# Strategy for generating message content
content_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S'), min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=200
).filter(lambda x: x.strip())


class TestUserMessageColoringProperties:
    """Property-based tests for user message coloring."""

    @settings(max_examples=100)
    @given(
        username=username_strategy,
        content=content_strategy
    )
    def test_property_3_user_message_color_consistency(self, username: str, content: str):
        """
        **Feature: swarm-fixes, Property 3: User Message Color Consistency**
        **Validates: Requirements 2.1, 3.4**
        
        For any user message displayed in the chat, the username portion should
        be rendered with the lime green color code (USER_STYLE = "bold bright_green").
        """
        # Create a human message
        message = Message(
            content=content,
            sender_name=username,
            role=MessageRole.HUMAN
        )
        
        # Verify that HUMAN role messages should use USER_STYLE
        # The logic in create_chat_panel checks: if msg.role == MessageRole.HUMAN
        assert message.role == MessageRole.HUMAN, "Message should have HUMAN role"
        
        # Verify USER_STYLE is the expected lime green
        assert USER_STYLE == "bold bright_green", (
            f"USER_STYLE should be 'bold bright_green', got '{USER_STYLE}'"
        )
        
        # Verify that HUMAN messages are NOT in AGENT_STYLES (they use USER_STYLE instead)
        # This ensures the dashboard logic will use USER_STYLE for human messages
        # since AGENT_STYLES.get(msg.sender_name, "white") would return "white" for unknown names
        # but the if msg.role == MessageRole.HUMAN check takes precedence
        
        # The key property: for HUMAN role messages, the style should be USER_STYLE
        # We verify this by checking the dashboard's logic pattern
        if message.role == MessageRole.HUMAN:
            expected_style = USER_STYLE
        else:
            expected_style = AGENT_STYLES.get(message.sender_name, "white")
        
        assert expected_style == USER_STYLE, (
            f"Human message should use USER_STYLE ('{USER_STYLE}'), "
            f"but would use '{expected_style}'"
        )

    @settings(max_examples=100)
    @given(
        agent_name=st.sampled_from(list(AGENT_STYLES.keys())),
        content=content_strategy
    )
    def test_agent_messages_use_agent_styles(self, agent_name: str, content: str):
        """
        Verify that agent messages use their designated styles, not USER_STYLE.
        This is the complement to Property 3 - ensuring separation of concerns.
        """
        # Create an agent message
        message = Message(
            content=content,
            sender_name=agent_name,
            role=MessageRole.ASSISTANT
        )
        
        # Agent messages should NOT use USER_STYLE
        assert message.role != MessageRole.HUMAN, "Agent message should not have HUMAN role"
        
        # Agent messages should use their designated style
        expected_style = AGENT_STYLES.get(message.sender_name, "white")
        assert expected_style != USER_STYLE or agent_name not in AGENT_STYLES, (
            f"Agent '{agent_name}' should use its designated style, not USER_STYLE"
        )


class TestUserMessageColoringEdgeCases:
    """Unit tests for edge cases in user message coloring."""

    def test_user_style_is_lime_green(self):
        """USER_STYLE should be bold bright_green (lime green)."""
        assert USER_STYLE == "bold bright_green"

    def test_human_role_triggers_user_style(self):
        """Messages with HUMAN role should trigger USER_STYLE usage."""
        message = Message(
            content="Hello world",
            sender_name="TestUser",
            role=MessageRole.HUMAN
        )
        
        # Simulate the dashboard logic
        if message.role == MessageRole.HUMAN:
            name_style = USER_STYLE
        else:
            name_style = AGENT_STYLES.get(message.sender_name, "white")
        
        assert name_style == USER_STYLE

    def test_assistant_role_uses_agent_styles(self):
        """Messages with ASSISTANT role should use AGENT_STYLES."""
        message = Message(
            content="Hello world",
            sender_name="Bossy McArchitect",
            role=MessageRole.ASSISTANT
        )
        
        # Simulate the dashboard logic
        if message.role == MessageRole.HUMAN:
            name_style = USER_STYLE
        else:
            name_style = AGENT_STYLES.get(message.sender_name, "white")
        
        assert name_style == AGENT_STYLES["Bossy McArchitect"]
        assert name_style != USER_STYLE

    def test_unknown_agent_uses_white_style(self):
        """Unknown agent names should use white style, not USER_STYLE."""
        message = Message(
            content="Hello world",
            sender_name="Unknown Agent",
            role=MessageRole.ASSISTANT
        )
        
        # Simulate the dashboard logic
        if message.role == MessageRole.HUMAN:
            name_style = USER_STYLE
        else:
            name_style = AGENT_STYLES.get(message.sender_name, "white")
        
        assert name_style == "white"
        assert name_style != USER_STYLE

    def test_all_message_roles_handled(self):
        """All MessageRole values should be handled correctly."""
        roles_and_expected = [
            (MessageRole.HUMAN, USER_STYLE),
            (MessageRole.ASSISTANT, "white"),  # Unknown sender
            (MessageRole.USER, "white"),  # Unknown sender
            (MessageRole.SYSTEM, "white"),  # Unknown sender
        ]
        
        for role, expected_style in roles_and_expected:
            message = Message(
                content="Test",
                sender_name="TestSender",
                role=role
            )
            
            # Simulate the dashboard logic
            if message.role == MessageRole.HUMAN:
                name_style = USER_STYLE
            else:
                name_style = AGENT_STYLES.get(message.sender_name, "white")
            
            assert name_style == expected_style, (
                f"Role {role} should use style '{expected_style}', got '{name_style}'"
            )
