"""
Verification script for Tool Enhancements.
Tests:
1. File creation (write_file).
2. File listing (list_files).
3. File moving (move_file).
4. File deletion (delete_file).
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent_tools import AgentToolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_tools():
    print("\n=== Verifying Tool Enhancements ===\n")
    
    # Setup
    executor = AgentToolExecutor("test_agent", "Test Agent")
    
    # 1. Create a file
    print("--- Testing write_file ---")
    res = await executor.execute_tool("write_file", {
        "path": "test_move.txt",
        "content": "Hello, World!"
    })
    print(f"Write Result: {res}")
    assert res["success"] is True
    
    # 2. List files
    print("\n--- Testing list_files ---")
    res = await executor.execute_tool("list_files", {"path": "."})
    print(f"List Result: {res}")
    items = res["result"]["items"]
    assert any(i["name"] == "test_move.txt" for i in items)
    
    # 3. Move file
    print("\n--- Testing move_file ---")
    res = await executor.execute_tool("move_file", {
        "source": "test_move.txt",
        "destination": "moved_test.txt"
    })
    print(f"Move Result: {res}")
    assert res["success"] is True
    
    # Verify move
    res = await executor.execute_tool("list_files", {"path": "."})
    items = res["result"]["items"]
    assert not any(i["name"] == "test_move.txt" for i in items)
    assert any(i["name"] == "moved_test.txt" for i in items)
    print("✓ File moved successfully")
    
    # 4. Delete file
    print("\n--- Testing delete_file ---")
    res = await executor.execute_tool("delete_file", {"path": "moved_test.txt"})
    print(f"Delete Result: {res}")
    assert res["success"] is True
    
    print("\n=== Verification Successful ===")

if __name__ == "__main__":
    asyncio.run(verify_tools())
