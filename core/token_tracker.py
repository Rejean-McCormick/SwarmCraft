"""
Token Tracker module for Multi-Agent Swarm.

This module provides a singleton class to track token usage across all agents
during API calls. It accumulates prompt tokens, completion tokens, and total
tokens for monitoring API consumption.
"""

from typing import Dict


class TokenTracker:
    """
    Singleton to track token usage across all agents.
    
    Tracks:
    - prompt_tokens: Tokens used in prompts/inputs
    - completion_tokens: Tokens generated in responses
    - total_tokens: Sum of prompt and completion tokens
    - call_count: Number of API calls made
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if self._initialized:
            return
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.call_count = 0
        self.by_agent: Dict[str, Dict[str, int]] = {}  # Per-agent tracking
        self._initialized = True
    
    def add_usage(self, prompt: int, completion: int, agent_name: str = None, task: str = None) -> None:
        """
        Record token usage from an API call.
        
        Args:
            prompt: Number of prompt tokens used
            completion: Number of completion tokens generated
            agent_name: Optional name of the agent making the call
            task: Optional description of what the agent was doing
        """
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += prompt + completion
        self.call_count += 1
        
        # Track per-agent usage
        if agent_name:
            if agent_name not in self.by_agent:
                self.by_agent[agent_name] = {"prompt": 0, "completion": 0, "calls": 0, "last_task": ""}
            self.by_agent[agent_name]["prompt"] += prompt
            self.by_agent[agent_name]["completion"] += completion
            self.by_agent[agent_name]["calls"] += 1
            if task:
                self.by_agent[agent_name]["last_task"] = task[:50]
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get current token statistics.
        
        Returns:
            Dictionary with prompt_tokens, completion_tokens, 
            total_tokens, call_count, and by_agent breakdown
        """
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "call_count": self.call_count,
            "by_agent": self.by_agent.copy()
        }
    
    def reset(self) -> None:
        """Reset counters for new session."""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.call_count = 0
        self.by_agent = {}


def get_token_tracker() -> TokenTracker:
    """
    Factory function to get the TokenTracker singleton.
    
    Returns:
        The TokenTracker singleton instance
    """
    return TokenTracker()
