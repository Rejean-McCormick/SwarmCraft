from typing import Dict, List, Optional
from swarm_ai_orchestrator.api_models import TaskDefinition, SubTask, TaskResult, BotInfo

class InMemoryStore:
    def __init__(self):
        self.tasks: Dict[str, TaskDefinition] = {}
        self.task_status: Dict[str, str] = {}
        self.subtasks: Dict[str, SubTask] = {}
        self.subtask_status: Dict[str, str] = {}
        self.results: Dict[str, TaskResult] = {}
        self.bots: Dict[str, BotInfo] = {}
        self.audit_logs: List[Dict] = []

    def add_task(self, task: TaskDefinition) -> str:
        self.tasks[task.id] = task
        self.task_status[task.id] = "CREATED"
        return task.id

    def get_task(self, task_id: str) -> Optional[TaskDefinition]:
        return self.tasks.get(task_id)

    def set_task_status(self, task_id: str, status: str):
        self.task_status[task_id] = status

    def get_task_status(self, task_id: str) -> Optional[str]:
        return self.task_status.get(task_id)

    def add_subtask(self, subtask: SubTask):
        self.subtasks[subtask.id] = subtask
        self.subtask_status[subtask.id] = "CREATED"

    def set_subtask_status(self, subtask_id: str, status: str):
        self.subtask_status[subtask_id] = status

    def get_subtask_status(self, subtask_id: str) -> Optional[str]:
        return self.subtask_status.get(subtask_id)

    def add_result(self, result: TaskResult):
        self.results[result.subtask_id] = result

    def register_bot(self, bot_id: str, info: dict):
        self.bots[bot_id] = BotInfo(**info)

    def log_audit(self, entry: dict):
        self.audit_logs.append(entry)
