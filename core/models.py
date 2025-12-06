"""
Data models for the Multi-Agent Chatroom.

This module defines the core data structures used throughout the application,
including messages, agent configurations, and memory structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class MessageRole(Enum):
    """Role of the message sender."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    HUMAN = "human"  # For human participants via websocket/discord


class MessageType(Enum):
    """Type of message for routing and display."""
    CHAT = "chat"
    SYSTEM_NOTICE = "system_notice"
    JOIN = "join"
    LEAVE = "leave"
    MEMORY_UPDATE = "memory_update"


@dataclass
class Message:
    """
    Represents a single message in the chatroom.
    
    Attributes:
        id: Unique identifier for the message
        role: Role of the sender (system, user, assistant, human)
        content: The message text
        sender_name: Display name of the sender
        sender_id: Unique identifier of the sender (agent or human)
        timestamp: When the message was created
        message_type: Type of message for UI/routing
        metadata: Additional metadata (e.g., model used, tokens)
    """
    content: str
    sender_name: str
    role: MessageRole = MessageRole.ASSISTANT
    sender_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: MessageType = MessageType.CHAT
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "sender_name": self.sender_name,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type.value,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create a Message from a dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            role=MessageRole(data.get("role", "assistant")),
            content=data["content"],
            sender_name=data["sender_name"],
            sender_id=data.get("sender_id", str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            message_type=MessageType(data.get("message_type", "chat")),
            metadata=data.get("metadata", {})
        )

    def to_api_format(self) -> Dict[str, str]:
        """Convert to format expected by Z.ai API."""
        role = "assistant" if self.role in [MessageRole.ASSISTANT] else "user"
        if self.role == MessageRole.SYSTEM:
            role = "system"
        return {
            "role": role,
            "content": f"[{self.sender_name}]: {self.content}" if role != "system" else self.content
        }


@dataclass
class AgentConfig:
    """
    Configuration for an AI agent.
    
    Attributes:
        name: Display name of the agent
        agent_id: Unique identifier
        model: Z.ai model to use
        system_prompt: Full system prompt defining personality
        temperature: Creativity level (0.0-1.0)
        max_tokens: Maximum response length
        speak_probability: Likelihood of responding to messages
    """
    name: str
    system_prompt: str
    model: str = "glm-4-flash"
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    temperature: float = 0.8
    max_tokens: int = 500
    speak_probability: float = 0.6
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "speak_probability": self.speak_probability
        }


@dataclass
class MemoryEntry:
    """
    A single memory entry for long-term storage.
    
    Attributes:
        id: Unique identifier
        agent_id: Which agent owns this memory
        content: The memory content (fact, summary, etc.)
        memory_type: Type of memory (fact, summary, observation)
        importance: Importance score (0.0-1.0)
        timestamp: When the memory was created
        source_messages: IDs of messages that generated this memory
    """
    content: str
    agent_id: str
    memory_type: str = "fact"  # fact, summary, observation
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    importance: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    source_messages: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "source_messages": self.source_messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create a MemoryEntry from a dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            agent_id=data["agent_id"],
            content=data["content"],
            memory_type=data.get("memory_type", "fact"),
            importance=data.get("importance", 0.5),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            source_messages=data.get("source_messages", [])
        )


class AgentStatus(str, Enum):
    """Status of an agent in the swarm."""
    IDLE = "idle"         # Waiting for a task
    WORKING = "working"   # Actively working on a task


class TaskStatus(str, Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """A unit of work assigned to an agent."""
    id: str
    description: str
    created_at: str  # ISO format
    assigned_to: Optional[str] = None  # Agent ID
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        # Handle enum conversion
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TaskStatus(data['status'])
        return cls(**data)


@dataclass
class ChatroomState:
    """
    Current state of the chatroom.
    
    Attributes:
        messages: Global message history
        active_agents: List of active agent IDs
        connected_humans: List of connected human user IDs
        is_running: Whether the chatroom is active
        round_number: Current conversation round
    """
    messages: List[Message] = field(default_factory=list)
    active_agents: List[str] = field(default_factory=list)
    connected_humans: List[str] = field(default_factory=list)
    is_running: bool = False
    round_number: int = 0
    
    def add_message(self, message: Message):
        """Add a message to the history."""
        self.messages.append(message)
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get the most recent N messages."""
        return self.messages[-count:] if self.messages else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "messages": [m.to_dict() for m in self.messages],
            "active_agents": self.active_agents,
            "connected_humans": self.connected_humans,
            "is_running": self.is_running,
            "round_number": self.round_number
        }
