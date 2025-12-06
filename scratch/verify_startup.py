"""
Verification script for Startup & Orchestration Refinement.
Tests:
1. Solo Architect start.
2. Dynamic spawning with unique names.
3. Model configuration usage.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chatroom import Chatroom
from agents import create_agent
from config.settings import ARCHITECT_MODEL, SWARM_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_startup():
    print("\n=== Verifying Startup & Orchestration ===\n")
    
    # 1. Verify Solo Start Logic (Simulated)
    print("--- Testing Solo Start ---")
    chatroom = Chatroom()
    architect = create_agent("architect", model=ARCHITECT_MODEL)
    await chatroom.initialize([architect])
    
    active_agents = chatroom.state.active_agents
    print(f"Active Agents: {active_agents}")
    assert len(active_agents) == 1
    assert "Sarah Lin" in chatroom._agents[active_agents[0]].name
    print("✓ Solo Architect start confirmed")
    
    # 2. Verify Dynamic Spawning & Naming
    print("\n--- Testing Dynamic Spawning ---")
    
    # Spawn first backend dev
    dev1 = await chatroom.spawn_agent("backend_dev")
    print(f"Spawned: {dev1.name} (Model: {dev1.model})")
    assert dev1.name == "Marcus Thorne"  # First one has no suffix? Or should it?
    # Wait, my logic was: if count > 0, add suffix.
    # So first one is "Marcus Thorne", second is "Marcus Thorne 2".
    
    # Spawn second backend dev
    dev2 = await chatroom.spawn_agent("backend_dev")
    print(f"Spawned: {dev2.name} (Model: {dev2.model})")
    assert dev2.name == "Marcus Thorne 2"
    
    # Spawn third backend dev
    dev3 = await chatroom.spawn_agent("backend_dev")
    print(f"Spawned: {dev3.name} (Model: {dev3.model})")
    assert dev3.name == "Marcus Thorne 3"
    
    print("✓ Unique naming confirmed")
    
    # 3. Verify Model Usage
    print("\n--- Testing Model Configuration ---")
    print(f"Architect Model: {architect.model} (Expected: {ARCHITECT_MODEL})")
    print(f"Swarm Model: {dev1.model} (Expected: {SWARM_MODEL})")
    
    assert architect.model == ARCHITECT_MODEL
    assert dev1.model == SWARM_MODEL
    print("✓ Model configuration confirmed")
    
    print("\n=== Verification Successful ===")

if __name__ == "__main__":
    asyncio.run(verify_startup())
