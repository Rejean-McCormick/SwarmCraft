"""
Property-based tests for token tracking in the core module.

**Feature: swarm-fixes, Property 4: Token Counter Accumulation**
**Validates: Requirements 4.2, 4.3**
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from hypothesis import given, strategies as st, settings

from core.token_tracker import TokenTracker, get_token_tracker


class TestTokenTrackerProperties:
    """Property-based tests for token tracking."""

    @pytest.fixture(autouse=True)
    def reset_tracker(self):
        """Reset the singleton tracker before each test."""
        tracker = get_token_tracker()
        tracker.reset()
        yield
        tracker.reset()

    @settings(max_examples=100)
    @given(
        st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=100000),
                st.integers(min_value=0, max_value=100000)
            ),
            min_size=1,
            max_size=50
        )
    )
    def test_property_4_token_counter_accumulation(self, token_pairs):
        """
        **Feature: swarm-fixes, Property 4: Token Counter Accumulation**
        **Validates: Requirements 4.2, 4.3**
        
        For any sequence of API calls with known token counts, the TokenTracker
        total should equal the sum of all individual prompt and completion tokens.
        """
        tracker = get_token_tracker()
        tracker.reset()
        
        expected_prompt = 0
        expected_completion = 0
        
        # Add all token usages
        for prompt, completion in token_pairs:
            tracker.add_usage(prompt, completion)
            expected_prompt += prompt
            expected_completion += completion
        
        stats = tracker.get_stats()
        
        # Assert - prompt tokens should equal sum of all prompt tokens
        assert stats["prompt_tokens"] == expected_prompt, (
            f"Expected prompt_tokens={expected_prompt}, got {stats['prompt_tokens']}"
        )
        
        # Assert - completion tokens should equal sum of all completion tokens
        assert stats["completion_tokens"] == expected_completion, (
            f"Expected completion_tokens={expected_completion}, got {stats['completion_tokens']}"
        )
        
        # Assert - total should equal sum of prompt and completion
        assert stats["total_tokens"] == expected_prompt + expected_completion, (
            f"Expected total_tokens={expected_prompt + expected_completion}, "
            f"got {stats['total_tokens']}"
        )
        
        # Assert - call count should equal number of add_usage calls
        assert stats["call_count"] == len(token_pairs), (
            f"Expected call_count={len(token_pairs)}, got {stats['call_count']}"
        )


class TestTokenTrackerEdgeCases:
    """Unit tests for edge cases in token tracking."""

    @pytest.fixture(autouse=True)
    def reset_tracker(self):
        """Reset the singleton tracker before each test."""
        tracker = get_token_tracker()
        tracker.reset()
        yield
        tracker.reset()

    def test_singleton_pattern(self):
        """TokenTracker should be a singleton."""
        tracker1 = get_token_tracker()
        tracker2 = get_token_tracker()
        tracker3 = TokenTracker()
        
        assert tracker1 is tracker2
        assert tracker2 is tracker3

    def test_initial_state(self):
        """New tracker should start with zero counts."""
        tracker = get_token_tracker()
        tracker.reset()
        stats = tracker.get_stats()
        
        assert stats["prompt_tokens"] == 0
        assert stats["completion_tokens"] == 0
        assert stats["total_tokens"] == 0
        assert stats["call_count"] == 0

    def test_reset_clears_all_counters(self):
        """Reset should clear all counters."""
        tracker = get_token_tracker()
        tracker.add_usage(100, 50)
        tracker.add_usage(200, 100)
        
        tracker.reset()
        stats = tracker.get_stats()
        
        assert stats["prompt_tokens"] == 0
        assert stats["completion_tokens"] == 0
        assert stats["total_tokens"] == 0
        assert stats["call_count"] == 0

    def test_zero_token_usage(self):
        """Adding zero tokens should still increment call count."""
        tracker = get_token_tracker()
        tracker.add_usage(0, 0)
        
        stats = tracker.get_stats()
        assert stats["call_count"] == 1
        assert stats["total_tokens"] == 0
