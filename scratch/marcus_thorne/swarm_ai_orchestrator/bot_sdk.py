from typing import Any, Dict

class BaseBot:
    def __init__(self, bot_id: str, bot_type: str):
        self.bot_id = bot_id
        self.bot_type = bot_type

    def poll_for_task(self, store):
        raise NotImplementedError

    def submit_result(self, store, task_id, result):
        raise NotImplementedError

class PlannerBot(BaseBot):
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "PlannerBot")

class ExecutorBot(BaseBot):
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "ExecutorBot")

class EvaluatorBot(BaseBot):
    def __init__(self, bot_id: str):
        super().__init__(bot_id, "EvaluatorBot")
