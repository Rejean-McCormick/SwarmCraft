"""
Start the Agent Traffic Control visualization dashboard.

This script starts:
1. The Python traffic relay server (ws://localhost:8766)
2. The Next.js visualization dashboard (http://localhost:3000)

Run this alongside main.py to visualize your swarm activity.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
TRAFFIC_CONTROL_DIR = PROJECT_ROOT / "agenttrafficcontrol"


async def start_traffic_relay():
    """Start the Python traffic relay server."""
    print("Starting Traffic Relay server...")
    from core.traffic_relay import start_traffic_relay as _start_relay
    relay = await _start_relay()
    return relay


def start_nextjs_server():
    """Start the Next.js dev server."""
    print("Starting Next.js dashboard...")
    
    # Check if npm is available
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    
    # Start npm run dev in background
    process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(TRAFFIC_CONTROL_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
    )
    
    return process


async def main():
    """Main entry point."""
    print("=" * 60)
    print("  AGENT TRAFFIC CONTROL - SWARM VISUALIZATION")
    print("=" * 60)
    print()
    
    # Start Next.js
    nextjs_proc = start_nextjs_server()
    
    # Wait a moment for Next.js to start
    await asyncio.sleep(3)
    
    # Start traffic relay
    relay = await start_traffic_relay()
    
    print()
    print("=" * 60)
    print("  Dashboard running at: http://localhost:3000")
    print("  Traffic relay at: ws://localhost:8766")
    print("=" * 60)
    print()
    print("Run your swarm with: python main.py")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        await relay.stop()
        nextjs_proc.terminate()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
