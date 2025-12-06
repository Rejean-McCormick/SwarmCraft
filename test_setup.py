"""
Quick test script to verify the multi-agent setup works.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    
    try:
        from agents import (
            Architect, BackendDev, FrontendDev, QAEngineer,
            DevOpsEngineer, ProjectManager, TechWriter,
            AGENT_CLASSES, create_agent
        )
        print("  ✓ All agents imported")
    except ImportError as e:
        print(f"  ✗ Agent import failed: {e}")
        return False
    
    try:
        from core.chatroom import Chatroom
        from core.task_manager import TaskManager
        from core.agent_tools import AgentToolExecutor, TOOL_DEFINITIONS
        from core.settings_manager import get_settings
        from core.models import Message, AgentConfig, Task
        print("  ✓ All core modules imported")
    except ImportError as e:
        print(f"  ✗ Core import failed: {e}")
        return False
    
    return True


def test_agents():
    """Test agent creation."""
    print("\nTesting agent creation...")
    
    from agents import AGENT_CLASSES, create_agent
    
    for role, cls in AGENT_CLASSES.items():
        try:
            agent = create_agent(role)
            print(f"  ✓ {agent.name} ({role})")
        except Exception as e:
            print(f"  ✗ {role}: {e}")
            return False
    
    return True


def test_tools():
    """Test tool definitions."""
    print("\nTesting tools...")
    
    from core.agent_tools import TOOL_DEFINITIONS
    
    tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    expected_tools = [
        "read_file", "write_file", "append_file", "edit_file",
        "list_files", "delete_file", "move_file", "create_folder",
        "search_code", "run_command", "scaffold_project", "get_project_structure",
        "spawn_worker", "assign_task", "get_swarm_state"
    ]
    
    for tool in expected_tools:
        if tool in tool_names:
            print(f"  ✓ {tool}")
        else:
            print(f"  ✗ {tool} (missing)")
            return False
    
    return True


def test_settings():
    """Test settings manager."""
    print("\nTesting settings...")
    
    from core.settings_manager import get_settings
    
    settings = get_settings()
    print(f"  ✓ Settings loaded: {len(settings.get_all())} keys")
    
    return True


def test_project_manager():
    """Test project manager."""
    print("\nTesting project manager...")
    
    try:
        from core.project_manager import get_project_manager, Project, get_current_project
        print("  ✓ Project manager imported")
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False
    
    try:
        pm = get_project_manager()
        print("  ✓ Project manager singleton created")
    except Exception as e:
        print(f"  ✗ Singleton failed: {e}")
        return False
    
    try:
        projects = pm.list_projects()
        print(f"  ✓ Listed {len(projects)} existing projects")
    except Exception as e:
        print(f"  ✗ List projects failed: {e}")
        return False
    
    try:
        from config.settings import get_memory_db_path, get_chat_history_path, get_scratch_dir
        print("  ✓ Dynamic path functions imported")
    except ImportError as e:
        print(f"  ✗ Dynamic path import failed: {e}")
        return False
    
    return True


def main():
    print("=" * 50)
    print("Multi-Agent Swarm - Setup Test")
    print("=" * 50)
    
    all_passed = True
    all_passed &= test_imports()
    all_passed &= test_agents()
    all_passed &= test_tools()
    all_passed &= test_settings()
    all_passed &= test_project_manager()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! Ready to run.")
        print("\nStart with: python main.py")
    else:
        print("✗ Some tests failed. Check errors above.")
    print("=" * 50)


if __name__ == "__main__":
    main()
