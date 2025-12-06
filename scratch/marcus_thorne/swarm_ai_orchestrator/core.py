from typing import Dict, List
from swarm_ai_orchestrator.api_models import TaskDefinition, SubTask, TaskResult

class InMemoryStore:
    def __init__(self):
        self.tasks: Dict[str, TaskDefinition] = {}
        self.subtasks: Dict[str, SubTask] = {}
        self.task_status: Dict[str, str] = {}
        self.subtask_status: Dict[str, str] = {}
        self.results: Dict[str, TaskResult] = {}
        self.bots: Dict[str, dict] = {}
        self.audit_logs: List[dict] = []

    def add_task(self, task: TaskDefinition) -> str:
        task_id = task.id
        self.tasks[task_id] = task
        self.task_status[task_id] = "CREATED"
        return task_id

    def set_task_status(self, task_id: str, status: str):
        self.task_status[task_id] = status

    def add_subtask(self, subtask: SubTask):
        self.subtasks[subtask.id] = subtask
        self.subtask_status[subtask.id] = "CREATED"

    def set_subtask_status(self, subtask_id: str, status: str):
        self.subtask_status[subtask_id] = status

    def add_result(self, result: TaskResult):
        self.results[result.task_id] = result

    def register_bot(self, bot_id: str, info: dict):
        self.bots[bot_id] = info

    def log_audit(self, entry: dict):
        self.audit_logs.append(entry)
