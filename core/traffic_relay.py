"""
Traffic Control Relay Server for Multi-Agent Swarm.

This module provides a WebSocket server that relays swarm state
to the Agent Traffic Control visualization dashboard.

Run alongside the main swarm or integrate via import.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

import websockets
from websockets.server import WebSocketServerProtocol

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.token_tracker import get_token_tracker
from core.models import AgentStatus

logger = logging.getLogger(__name__)


@dataclass
class TrafficAgent:
    """Agent state for traffic control visualization."""
    agent_id: str
    name: str
    role: str
    status: str  # 'idle', 'thinking', 'working', 'offline'
    current_task_id: Optional[str] = None


@dataclass
class TrafficTask:
    """Task state for traffic control visualization."""
    id: str
    description: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    assigned_to: Optional[str] = None
    created_at: str = ""
    completed_at: Optional[str] = None


@dataclass
class TokenStats:
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    call_count: int = 0
    by_agent: Dict[str, Dict[str, int]] = None
    
    def __post_init__(self):
        if self.by_agent is None:
            self.by_agent = {}


class TrafficControlRelay:
    """
    WebSocket relay server for Agent Traffic Control dashboard.
    
    Exposes swarm state in a format compatible with the traffic control
    frontend visualization.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8766):
        """
        Initialize the relay server.
        
        Args:
            host: Host to bind to
            port: Port to listen on (different from main WS server)
        """
        self.host = host
        self.port = port
        self._clients: Set[WebSocketServerProtocol] = set()
        self._chatroom = None
        self._server = None
        self._running = False
        self._broadcast_task = None
        
        # Cache state for efficient broadcasting
        self._agents: Dict[str, TrafficAgent] = {}
        self._tasks: Dict[str, TrafficTask] = {}
    
    def set_chatroom(self, chatroom):
        """Connect to the main chatroom for state access."""
        self._chatroom = chatroom
        logger.info("Traffic Control Relay connected to chatroom")
    
    def _get_agent_role(self, agent) -> str:
        """Determine the role of an agent from its class name."""
        class_name = agent.__class__.__name__.lower()
        role_mapping = {
            'architect': 'architect',
            'backenddev': 'backend_dev',
            'frontenddev': 'frontend_dev',
            'qaengineer': 'qa_engineer',
            'devopsengineer': 'devops_engineer',
            'projectmanager': 'project_manager',
            'techwriter': 'tech_writer',
        }
        return role_mapping.get(class_name, 'backend_dev')
    
    def _get_swarm_state(self) -> Dict[str, Any]:
        """Build current swarm state for traffic control."""
        # Try to get chatroom from singleton if not set
        chatroom = self._chatroom
        if not chatroom:
            try:
                # Access the global _chatroom directly (get_chatroom is async)
                import core.chatroom as chatroom_module
                chatroom = chatroom_module._chatroom
            except:
                pass
        
        # Get agents from chatroom
        agents = []
        if chatroom:
            for agent_id, agent in chatroom._agents.items():
                status = 'idle'
                if hasattr(agent, 'status'):
                    # AgentStatus only has IDLE and WORKING
                    if agent.status == AgentStatus.WORKING:
                        status = 'working'
                    elif agent.status == AgentStatus.IDLE:
                        status = 'idle'
                    else:
                        # Fallback: use the status value directly
                        status = agent.status.value if hasattr(agent.status, 'value') else str(agent.status)
                
                agents.append({
                    'agent_id': agent_id,
                    'name': agent.name,
                    'role': self._get_agent_role(agent),
                    'status': status,
                    'current_task_id': getattr(agent, 'current_task_id', None)
                })
        
        # Get tasks from task manager
        tasks = []
        try:
            from core.task_manager import get_task_manager
            tm = get_task_manager()
            for task in tm.get_all_tasks():
                tasks.append({
                    'id': task.id,
                    'description': task.description,
                    'status': task.status.value if hasattr(task.status, 'value') else str(task.status),
                    'assigned_to': task.assigned_to,
                    'created_at': task.created_at,
                    'completed_at': getattr(task, 'completed_at', None)
                })
        except Exception as e:
            logger.debug(f"Could not get tasks: {e}")
        
        # Get token stats
        tracker = get_token_tracker()
        stats = tracker.get_stats()
        
        # Get recent messages for activity context
        messages = []
        if chatroom:
            recent = chatroom.state.get_recent_messages(10)
            for msg in recent:
                messages.append({
                    'sender_name': msg.sender_name,
                    'sender_id': msg.sender_id,
                    'content': msg.content[:200],  # Truncate for efficiency
                    'message_type': msg.message_type.value,
                    'role': msg.role.value,
                    'metadata': msg.metadata,
                    'timestamp': msg.timestamp.isoformat()
                })
        
        return {
            'agents': agents,
            'tasks': tasks,
            'messages': messages,
            'token_stats': {
                'prompt_tokens': stats['prompt_tokens'],
                'completion_tokens': stats['completion_tokens'],
                'total_tokens': stats['total_tokens'],
                'call_count': stats['call_count'],
                'by_agent': stats['by_agent']
            }
        }
    
    async def _broadcast_state(self):
        """Broadcast current state to all connected clients."""
        if not self._clients:
            return
        
        state = self._get_swarm_state()
        
        data = json.dumps({
            'type': 'state',
            'state': state,
            'timestamp': datetime.now().isoformat()
        })
        
        disconnected = []
        for client in self._clients:
            try:
                await client.send(data)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client)
        
        for client in disconnected:
            self._clients.discard(client)
    
    async def _broadcast_loop(self):
        """Periodically broadcast state updates."""
        while self._running:
            try:
                await self._broadcast_state()
                await asyncio.sleep(1.0)  # 1Hz update rate - smoother and less CPU
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                await asyncio.sleep(2)
    
    async def _handle_message(self, websocket: WebSocketServerProtocol, raw_message: str):
        """Handle incoming messages from traffic control clients."""
        try:
            data = json.loads(raw_message)
            msg_type = data.get('type', '')
            
            if msg_type == 'get_state':
                # Send current state
                state = self._get_swarm_state()
                await websocket.send(json.dumps({
                    'type': 'state',
                    'state': state,
                    'timestamp': datetime.now().isoformat()
                }))
            
            elif msg_type == 'ping':
                await websocket.send(json.dumps({'type': 'pong'}))
            
            # Could add more commands here:
            # - pause/resume swarm
            # - focus on specific agent
            # - etc.
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON: {raw_message[:100]}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _connection_handler(self, websocket: WebSocketServerProtocol, path: str = None):
        """Handle a WebSocket connection lifecycle."""
        self._clients.add(websocket)
        logger.info(f"Traffic Control client connected ({len(self._clients)} total)")
        
        # Send initial state
        try:
            # Get and send initial state
            try:
                state = self._get_swarm_state()
            except Exception as state_err:
                logger.error(f"_get_swarm_state error: {state_err}")
                # Send empty state so client doesn't hang
                state = {'agents': [], 'tasks': [], 'messages': [], 'token_stats': {
                    'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0, 'call_count': 0, 'by_agent': {}
                }}
            
            await websocket.send(json.dumps({
                'type': 'state',
                'state': state,
                'timestamp': datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending initial state: {e}", exc_info=True)
        
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Connection handler error: {e}")
        finally:
            self._clients.discard(websocket)
            logger.info(f"Traffic Control client disconnected ({len(self._clients)} remaining)")
    
    async def start(self):
        """Start the relay server."""
        self._running = True
        try:
            self._server = await websockets.serve(
                self._connection_handler,
                self.host,
                self.port
            )
        except OSError as e:
            if "address already in use" in str(e).lower() or e.errno == 10048:
                # Port already in use - try to connect to check if relay is running
                logger.warning(f"Port {self.port} already in use, relay may already be running")
                self._running = False
                return
            raise
        
        # Start broadcast loop
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        
        logger.info(f"Traffic Control Relay started on ws://{self.host}:{self.port}")
    
    async def stop(self):
        """Stop the relay server."""
        self._running = False
        
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
        
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        # Close all client connections
        for client in list(self._clients):
            try:
                await client.close()
            except:
                pass
        self._clients.clear()
        
        logger.info("Traffic Control Relay stopped")


# Global instance
_relay: Optional[TrafficControlRelay] = None


def get_traffic_relay() -> TrafficControlRelay:
    """Get or create the Traffic Control relay instance."""
    global _relay
    if _relay is None:
        _relay = TrafficControlRelay()
    return _relay


async def start_traffic_relay(chatroom=None, host: str = "localhost", port: int = 8766):
    """
    Start the Traffic Control relay server.
    
    Args:
        chatroom: The chatroom instance to monitor
        host: Host to bind to
        port: Port to listen on
    """
    relay = get_traffic_relay()
    relay.host = host
    relay.port = port
    
    if chatroom:
        relay.set_chatroom(chatroom)
    
    await relay.start()
    return relay


if __name__ == "__main__":
    # Standalone test mode
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        relay = await start_traffic_relay()
        print(f"Traffic Control Relay running on ws://localhost:8766")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await relay.stop()
    
    asyncio.run(main())
