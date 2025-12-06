from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Deque, Dict, List, Optional
from collections import deque


class TaskStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class Task:
    id: str
    bot_type: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class EventBus:
    def __init__(self) -> None:
        self.subscribers: Dict[str, List[Callable[[str, Any], None]]] = {}

    def subscribe(self, topic: str, callback: Callable[[str, Any], None]) -> None:
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    def publish(self, topic: str, payload: Any) -> None:
        for cb in self.subscribers.get(topic, []):
            try:
                cb(topic, payload)
            except Exception:
                # Silently ignore subscriber errors to not disrupt orchestration
                pass


class BotInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def run_task(self, task: Task) -> Dict[str, Any]:
        ...


def _redact_value(val: Any) -> Any:
    # Simple redaction for sensitive keys inside dicts/lists
    if isinstance(val, dict):
        new = {}
        for k, v in val.items():
            if any(red_key in k.lower() for red_key in ("secret", "password", "token", "key")):
                new[k] = "***REDACTED***"
            else:
                new[k] = _redact_value(v)
        return new
    elif isinstance(val, list):
        return [_redact_value(v) for v in val]
    else:
        return val


class Orchestrator:
    def __init__(self) -> None:
        self.queue: Deque[Task] = deque()
        self.tasks: Dict[str, Task] = {}
        self.bots: Dict[str, BotInterface] = {}
        self.event_bus: EventBus = EventBus()

    def register_bot(self, bot_type: str, bot: BotInterface) -> None:
        self.bots[bot_type] = bot

    def submit_task(self, bot_type: str, payload: Dict[str, Any], task_id: Optional[str] = None) -> Task:
        # Idempotent submission: if a task with same id exists, return existing
        if task_id is not None and task_id in self.tasks:
            return self.tasks[task_id]

        tid = task_id or str(uuid.uuid4())
        t = Task(id=tid, bot_type=bot_type, payload=payload)
        self.tasks[tid] = t
        self.queue.append(t)
        t.updated_at = time.time()
        self.event_bus.publish("task_submitted", t)
        return t

    def process_next(self) -> Optional[Task]:
        if not self.queue:
            return None
        t = self.queue.popleft()
        t.status = TaskStatus.IN_PROGRESS
        t.updated_at = time.time()

        bot = self.bots.get(t.bot_type)
        if bot is None:
            t.status = TaskStatus.FAILED
            t.error = f"No bot registered for type '{t.bot_type}'"
            t.updated_at = time.time()
            self.event_bus.publish("task_failed", t)
            return t

        try:
            res = bot.run_task(t)
            # Normalize response
            if isinstance(res, dict) and res.get("success"):
                data = res.get("data")
                if data is None:
                    data = {}
                t.result = _redact_value(data)
                t.status = TaskStatus.DONE
            else:
                t.status = TaskStatus.FAILED
                t.error = res.get("error") if isinstance(res, dict) else "Unknown error"
        except Exception as e:
            t.status = TaskStatus.FAILED
            t.error = str(e)
        finally:
            t.updated_at = time.time()
            self.event_bus.publish("task_updated", t)
        return t

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)


__all__ = ["Orchestrator", "EventBus", "TaskStatus", "Task", "BotInterface"]
