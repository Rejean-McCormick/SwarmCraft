"""
Memory Store for Multi-Agent Chatroom.

This module handles persistent long-term memory storage for agents using SQLite.
Each agent maintains their own memory space for facts, summaries, and observations.
"""

import asyncio
import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_memory_db_path, ensure_data_directory
from core.models import MemoryEntry

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Persistent memory storage for AI agents.
    
    Uses SQLite for durable storage of agent memories including:
    - Facts learned from conversations
    - Periodic summaries of interactions
    - Observations about other participants
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the memory store.
        
        Args:
            db_path: Path to SQLite database. Defaults to configured path.
        """
        # Use dynamic path function if no explicit path provided
        self.db_path = db_path or get_memory_db_path()
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the database schema."""
        if self._initialized:
            return
            
        async with self._lock:
            if self._initialized:
                return
                
            ensure_data_directory()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        memory_type TEXT NOT NULL,
                        importance REAL DEFAULT 0.5,
                        timestamp TEXT NOT NULL,
                        source_messages TEXT,
                        embedding TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memories_agent 
                    ON memories(agent_id)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memories_type 
                    ON memories(agent_id, memory_type)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memories_importance 
                    ON memories(agent_id, importance DESC)
                """)
                
                await db.commit()
            
            self._initialized = True
            logger.info(f"Memory store initialized at {self.db_path}")
    
    async def store_memory(self, memory: MemoryEntry) -> bool:
        """
        Store a new memory entry.
        
        Args:
            memory: The MemoryEntry to store
            
        Returns:
            True if successful, False otherwise
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO memories 
                    (id, agent_id, content, memory_type, importance, timestamp, source_messages)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.agent_id,
                    memory.content,
                    memory.memory_type,
                    memory.importance,
                    memory.timestamp.isoformat(),
                    json.dumps(memory.source_messages)
                ))
                await db.commit()
            
            logger.debug(f"Stored memory {memory.id} for agent {memory.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    async def get_memories(
        self,
        agent_id: str,
        memory_type: Optional[str] = None,
        limit: int = 20,
        min_importance: float = 0.0
    ) -> List[MemoryEntry]:
        """
        Retrieve memories for an agent.
        
        Args:
            agent_id: ID of the agent
            memory_type: Optional filter by memory type
            limit: Maximum number of memories to return
            min_importance: Minimum importance threshold
            
        Returns:
            List of MemoryEntry objects
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                if memory_type:
                    cursor = await db.execute("""
                        SELECT * FROM memories 
                        WHERE agent_id = ? AND memory_type = ? AND importance >= ?
                        ORDER BY importance DESC, timestamp DESC
                        LIMIT ?
                    """, (agent_id, memory_type, min_importance, limit))
                else:
                    cursor = await db.execute("""
                        SELECT * FROM memories 
                        WHERE agent_id = ? AND importance >= ?
                        ORDER BY importance DESC, timestamp DESC
                        LIMIT ?
                    """, (agent_id, min_importance, limit))
                
                rows = await cursor.fetchall()
                
                memories = []
                for row in rows:
                    memories.append(MemoryEntry(
                        id=row['id'],
                        agent_id=row['agent_id'],
                        content=row['content'],
                        memory_type=row['memory_type'],
                        importance=row['importance'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        source_messages=json.loads(row['source_messages']) if row['source_messages'] else []
                    ))
                
                return memories
                
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    async def get_recent_summaries(self, agent_id: str, limit: int = 3) -> List[MemoryEntry]:
        """
        Get the most recent conversation summaries for an agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of summaries
            
        Returns:
            List of summary MemoryEntry objects
        """
        return await self.get_memories(
            agent_id=agent_id,
            memory_type="summary",
            limit=limit
        )
    
    async def get_facts(self, agent_id: str, limit: int = 10) -> List[MemoryEntry]:
        """
        Get important facts for an agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of facts
            
        Returns:
            List of fact MemoryEntry objects
        """
        return await self.get_memories(
            agent_id=agent_id,
            memory_type="fact",
            limit=limit,
            min_importance=0.3
        )
    
    async def search_memories(
        self,
        agent_id: str,
        query: str,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """
        Search memories by content (simple text matching).
        
        For production use, integrate with a vector database for semantic search.
        
        Args:
            agent_id: ID of the agent
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching MemoryEntry objects
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute("""
                    SELECT * FROM memories 
                    WHERE agent_id = ? AND content LIKE ?
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                """, (agent_id, f"%{query}%", limit))
                
                rows = await cursor.fetchall()
                
                memories = []
                for row in rows:
                    memories.append(MemoryEntry(
                        id=row['id'],
                        agent_id=row['agent_id'],
                        content=row['content'],
                        memory_type=row['memory_type'],
                        importance=row['importance'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        source_messages=json.loads(row['source_messages']) if row['source_messages'] else []
                    ))
                
                return memories
                
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    async def delete_agent_memories(self, agent_id: str) -> bool:
        """
        Delete all memories for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            True if successful
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM memories WHERE agent_id = ?",
                    (agent_id,)
                )
                await db.commit()
            
            logger.info(f"Deleted all memories for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memories: {e}")
            return False
    
    async def get_memory_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get statistics about an agent's memories.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary with memory statistics
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN memory_type = 'fact' THEN 1 ELSE 0 END) as facts,
                        SUM(CASE WHEN memory_type = 'summary' THEN 1 ELSE 0 END) as summaries,
                        SUM(CASE WHEN memory_type = 'observation' THEN 1 ELSE 0 END) as observations,
                        AVG(importance) as avg_importance
                    FROM memories 
                    WHERE agent_id = ?
                """, (agent_id,))
                
                row = await cursor.fetchone()
                
                return {
                    "total": row[0] or 0,
                    "facts": row[1] or 0,
                    "summaries": row[2] or 0,
                    "observations": row[3] or 0,
                    "avg_importance": row[4] or 0.0
                }
                
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"total": 0, "facts": 0, "summaries": 0, "observations": 0, "avg_importance": 0.0}


# Global memory store instance
_memory_store: Optional[MemoryStore] = None


async def get_memory_store() -> MemoryStore:
    """Get the global memory store instance."""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
        await _memory_store.initialize()
    return _memory_store
