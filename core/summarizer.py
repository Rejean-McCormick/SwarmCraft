"""
Summarizer module for Multi-Agent Chatroom.

This module handles creating summaries of conversations for long-term memory.
It uses the Z.ai API to generate concise summaries and extract key facts.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Optional, Tuple
import logging
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import (
    LLM_API_KEY,
    LLM_API_BASE_URL,
    DEFAULT_MODEL,
    SUMMARIZE_EVERY_N_MESSAGES,
    MAX_RESPONSE_TOKENS
)
from core.models import Message, MemoryEntry

logger = logging.getLogger(__name__)


# Prompts for summarization
SUMMARY_SYSTEM_PROMPT = """You are a conversation summarizer. Your task is to create concise, 
informative summaries of chat conversations. Focus on:

1. Key topics discussed
2. Important decisions or conclusions
3. Notable interactions between participants
4. Any action items or plans mentioned

Keep summaries under 200 words. Be objective and capture the essence of the conversation."""

FACT_EXTRACTION_PROMPT = """You are a fact extractor. Analyze the following conversation and extract 
key facts that would be useful to remember. For each fact, provide:

1. The fact itself (one sentence)
2. Importance score (0.0-1.0 based on relevance and usefulness)

Format your response as JSON:
{
    "facts": [
        {"content": "fact text", "importance": 0.7},
        {"content": "another fact", "importance": 0.5}
    ]
}

Extract 3-5 most important facts. Focus on information about participants, 
topics discussed, preferences expressed, and decisions made."""


class Summarizer:
    """
    Generates summaries and extracts facts from conversations using Z.ai API.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the summarizer.
        
        Args:
            model: LLM model to use for summarization
        """
        self.model = model
        self.api_key = LLM_API_KEY
        self.api_url = LLM_API_BASE_URL
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _call_api(self, messages: List[dict]) -> Optional[str]:
        """
        Call the Z.ai API.
        
        Args:
            messages: List of message dicts in API format
            
        Returns:
            The response content or None on error
        """
        if not self.api_key:
            logger.warning("No API key configured for summarizer")
            return None
        
        session = await self._get_session()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,  # Lower temperature for more consistent summaries
            "max_tokens": MAX_RESPONSE_TOKENS
        }
        
        try:
            async with session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=600)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text}")
                    return None
                
                data = await response.json()
                return data["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None
    
    def _format_messages_for_summary(self, messages: List[Message]) -> str:
        """
        Format messages into a readable conversation transcript.
        
        Args:
            messages: List of Message objects
            
        Returns:
            Formatted conversation string
        """
        lines = []
        for msg in messages:
            timestamp = msg.timestamp.strftime("%H:%M")
            lines.append(f"[{timestamp}] {msg.sender_name}: {msg.content}")
        return "\n".join(lines)
    
    async def summarize_conversation(
        self,
        messages: List[Message],
        agent_id: str
    ) -> Optional[MemoryEntry]:
        """
        Create a summary of a conversation segment.
        
        Args:
            messages: List of messages to summarize
            agent_id: ID of the agent creating this memory
            
        Returns:
            MemoryEntry containing the summary, or None on failure
        """
        if len(messages) < 3:
            logger.debug("Not enough messages to summarize")
            return None
        
        conversation_text = self._format_messages_for_summary(messages)
        
        api_messages = [
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": f"Please summarize this conversation:\n\n{conversation_text}"}
        ]
        
        summary = await self._call_api(api_messages)
        
        if not summary:
            return None
        
        return MemoryEntry(
            agent_id=agent_id,
            content=summary,
            memory_type="summary",
            importance=0.8,
            source_messages=[msg.id for msg in messages]
        )
    
    async def extract_facts(
        self,
        messages: List[Message],
        agent_id: str
    ) -> List[MemoryEntry]:
        """
        Extract key facts from a conversation.
        
        Args:
            messages: List of messages to analyze
            agent_id: ID of the agent creating these memories
            
        Returns:
            List of MemoryEntry objects containing facts
        """
        if len(messages) < 2:
            return []
        
        conversation_text = self._format_messages_for_summary(messages)
        
        api_messages = [
            {"role": "system", "content": FACT_EXTRACTION_PROMPT},
            {"role": "user", "content": f"Extract facts from this conversation:\n\n{conversation_text}"}
        ]
        
        response = await self._call_api(api_messages)
        
        if not response:
            return []
        
        try:
            # Try to parse JSON from response
            # Handle potential markdown code blocks
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            data = json.loads(response)
            facts = data.get("facts", [])
            
            memory_entries = []
            for fact in facts:
                if isinstance(fact, dict) and "content" in fact:
                    memory_entries.append(MemoryEntry(
                        agent_id=agent_id,
                        content=fact["content"],
                        memory_type="fact",
                        importance=float(fact.get("importance", 0.5)),
                        source_messages=[msg.id for msg in messages]
                    ))
            
            return memory_entries
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse fact extraction response: {e}")
            # Fallback: treat the entire response as a single fact
            return [MemoryEntry(
                agent_id=agent_id,
                content=response[:500],  # Truncate if too long
                memory_type="fact",
                importance=0.5,
                source_messages=[msg.id for msg in messages]
            )]
    
    async def process_conversation_batch(
        self,
        messages: List[Message],
        agent_id: str
    ) -> Tuple[Optional[MemoryEntry], List[MemoryEntry]]:
        """
        Process a batch of messages: create summary and extract facts.
        
        Args:
            messages: List of messages to process
            agent_id: ID of the agent
            
        Returns:
            Tuple of (summary MemoryEntry or None, list of fact MemoryEntries)
        """
        # Run summarization and fact extraction concurrently
        summary_task = self.summarize_conversation(messages, agent_id)
        facts_task = self.extract_facts(messages, agent_id)
        
        summary, facts = await asyncio.gather(summary_task, facts_task)
        
        return summary, facts


class ConversationMemoryManager:
    """
    Manages the memory lifecycle for an agent's conversations.
    
    Handles:
    - Tracking message counts for summarization triggers
    - Coordinating between summarizer and memory store
    - Retrieving relevant memories for context
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize the memory manager.
        
        Args:
            agent_id: ID of the agent this manager belongs to
        """
        self.agent_id = agent_id
        self.summarizer = Summarizer()
        self._message_count = 0
        self._unsummarized_messages: List[Message] = []
    
    async def process_new_message(
        self,
        message: Message,
        memory_store
    ) -> None:
        """
        Process a new message for potential memory storage.
        
        Args:
            message: The new message
            memory_store: MemoryStore instance
        """
        self._unsummarized_messages.append(message)
        self._message_count += 1
        
        # Check if we should create a summary
        if self._message_count >= SUMMARIZE_EVERY_N_MESSAGES:
            await self._create_memories(memory_store)
            self._message_count = 0
            self._unsummarized_messages = []
    
    async def _create_memories(self, memory_store) -> None:
        """
        Create and store memories from accumulated messages.
        
        Args:
            memory_store: MemoryStore instance
        """
        if len(self._unsummarized_messages) < 3:
            return
        
        summary, facts = await self.summarizer.process_conversation_batch(
            self._unsummarized_messages,
            self.agent_id
        )
        
        if summary:
            await memory_store.store_memory(summary)
            logger.info(f"Stored summary for agent {self.agent_id}")
        
        for fact in facts:
            await memory_store.store_memory(fact)
        
        if facts:
            logger.info(f"Stored {len(facts)} facts for agent {self.agent_id}")
    
    async def get_context_memories(
        self,
        memory_store,
        query: Optional[str] = None
    ) -> str:
        """
        Get relevant memories formatted for the agent's context.
        
        Args:
            memory_store: MemoryStore instance
            query: Optional query for memory search
            
        Returns:
            Formatted memory string for inclusion in prompts
        """
        memories = []
        
        # Get recent summaries
        summaries = await memory_store.get_recent_summaries(self.agent_id, limit=2)
        if summaries:
            memories.append("## Recent Conversation Summaries:")
            for s in summaries:
                memories.append(f"- {s.content}")
        
        # Get important facts
        facts = await memory_store.get_facts(self.agent_id, limit=5)
        if facts:
            memories.append("\n## Important Facts:")
            for f in facts:
                memories.append(f"- {f.content}")
        
        # Search for query-specific memories if provided
        if query:
            search_results = await memory_store.search_memories(
                self.agent_id, 
                query, 
                limit=3
            )
            if search_results:
                memories.append(f"\n## Related to '{query}':")
                for r in search_results:
                    memories.append(f"- {r.content}")
        
        return "\n".join(memories) if memories else ""
    
    async def close(self):
        """Clean up resources."""
        await self.summarizer.close()
