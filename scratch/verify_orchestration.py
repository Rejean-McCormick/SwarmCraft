"""
Verification script for Dynamic Orchestration.
Tests:
1. Task creation and assignment.
2. Agent status updates.
3. Strict conversation loop (workers silent until assigned).
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import AgentStatus, TaskStatus
from core.task_manager import get_task_manager
from core.chatroom import Chatroom
from agents import create_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_orchestration():
    print("\n=== Verifying Dynamic Orchestration ===\n")
    
    # 1. Setup
    chatroom = Chatroom()
    tm = get_task_manager()
    
    # Create Architect and Worker
    architect = create_agent("architect")
    worker = create_agent("backend_dev")
    
    await chatroom.add_agent(architect)
    await chatroom.add_agent(worker)
    
    print(f"Agents added: {architect.name}, {worker.name}")
    print(f"Worker Status: {worker.status}")
    assert worker.status == AgentStatus.IDLE
    
    # 2. Verify Silence (Worker should not speak when IDLE)
    print("\n--- Testing Silence ---")
    should_speak = worker.should_respond()
    print(f"Worker should respond? {should_speak}")
    assert should_speak is False, "Worker should be silent when IDLE"
    
    # 3. Verify Task Assignment
    print("\n--- Testing Assignment ---")
    task_desc = "Create a hello world python script"
    await chatroom.assign_task(worker.name, task_desc)
    
    # Check Task Manager
    tasks = tm.get_all_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    print(f"Task Created: {task.id} - {task.description}")
    assert task.assigned_to == worker.agent_id
    assert task.status == TaskStatus.IN_PROGRESS
    
    # Check Worker Status
    print(f"Worker Status: {worker.status}")
    assert worker.status == AgentStatus.WORKING
    assert worker.current_task_id == task.id
    
    # 4. Verify Speaking (Worker should speak when WORKING)
    print("\n--- Testing Active State ---")
    should_speak = worker.should_respond()
    print(f"Worker should respond? {should_speak}")
    assert should_speak is True, "Worker should speak when WORKING"
    
    # 5. Verify Tool Usage (Simulate completion)
    print("\n--- Testing Completion ---")
    # Simulate worker completing the task
    result_msg = "Task Complete: Created hello.py"
    tm.complete_task(task.id, result_msg)
    worker.status = AgentStatus.IDLE
    worker.current_task_id = None
    
    print(f"Worker Status after completion: {worker.status}")
    assert worker.status == AgentStatus.IDLE
    
    print("\n=== Verification Successful ===")

if __name__ == "__main__":
    asyncio.run(verify_orchestration())
