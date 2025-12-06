from pydantic import BaseModel
from typing import List, Optional

class TaskDefinition(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    priority: Optional[int] = None
    subtasks: Optional[List[str]] = None

class SubTask(BaseModel):
    id: str
    parent_task_id: Optional[str] = None
    description: str
    required_skills: List[str]
    status: str

class BotInfo(BaseModel):
    id: str
    type: str
    version: Optional[str] = None
    endpoint: Optional[str] = None

class TaskStatus(BaseModel):
    status: str

class BotMessage(BaseModel):
    from_bot: str
    to_bot: str
    task_id: str
    payload: dict
    timestamp: Optional[str] = None

class AuditLog(BaseModel):
    id: str
    task_id: str
    event: str
    payload: dict
    redacted_fields: List[str] = []
    timestamp: Optional[str] = None
