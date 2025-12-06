import pytest

from swarm_orchestrator.orchestrator.core import Orchestrator, TaskStatus
from swarm_orchestrator.bots.PlannerBot import PlannerBot
from swarm_orchestrator.bots.ArchitectBot import ArchitectBot


def test_task_processing_and_redaction():
    orchestrator = Orchestrator()

    planner = PlannerBot()
    architect = ArchitectBot()
    orchestrator.register_bot("planner", planner)
    orchestrator.register_bot("architect", architect)

    payload = {"action": "build_plan", "secret_token": "s3cr3t"}
    t = orchestrator.submit_task("planner", payload, task_id="task-1")

    processed = orchestrator.process_next()
    assert processed is not None
    assert processed.id == "task-1"
    assert processed.status == TaskStatus.DONE
    assert processed.result is not None
    assert isinstance(processed.result, dict)
    echoed = processed.result.get("echo")
    assert isinstance(echoed, dict)
    assert echoed.get("secret_token") == "***REDACTED***"


def test_missing_bot_registration_fails():
    orchestrator = Orchestrator()
    planner = PlannerBot()
    orchestrator.register_bot("planner", planner)

    t = orchestrator.submit_task("nonexistent", {"a": 1}, task_id="t2")
    processed = orchestrator.process_next()
    assert processed is not None
    assert processed.status.name == "FAILED"
    assert "No bot registered" in (processed.error or "")
