from __future__ import annotations

from typing import Any, Dict
from ..orchestrator.core import Task, BotInterface


class MockBot(BotInterface):
    @property
    def name(self) -> str:  # pragma: no cover
        return self.__class__.__name__

    def run_task(self, task: Task) -> Dict[str, Any]:
        # Simple mock: echo payload and declare success
        return {"success": True, "data": {"echo": task.payload}}
