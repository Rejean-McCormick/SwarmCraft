from pydantic import BaseModel
from typing import List, Optional, Dict

class TaskDefinition(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    priority: Optional[int] = None

class SubTask(BaseModel):
    id: str
    parent_task_id: Optional[str] = None
    description: str
    required_skills: List[str] = []
    status: str
    assigned_to: Optional[str] = None

class TaskRecord(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: Optional[int] = None
    status: str
    subtasks: List[SubTask] = []

class BotInfo(BaseModel):
    id: str
    type: str
    version: Optional[str] = None
    endpoint: Optional[str] = None

class BotRegistration(BaseModel):
    bot: BotInfo

class BotMessage(BaseModel):
    from_bot: str
    to_bot: str
    task_id: str
    payload: Dict
    timestamp: Optional[str] = None

class TaskResult(BaseModel):
    task_id: str
    subtask_id: str
    status: str
    payload: Optional[Dict] = None

class Health(BaseModel):
    status: str
    service: str

