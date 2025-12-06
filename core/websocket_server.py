"""
WebSocket server for Multi-Agent Chatroom.

This module provides a WebSocket server that allows human users
to connect and participate in the AI chatroom in real-time.
"""

import asyncio
import json
import logging
import signal
from datetime import datetime
from typing import Set, Dict, Any
import uuid

import websockets
from websockets.server import WebSocketServerProtocol

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import WEBSOCKET_HOST, WEBSOCKET_PORT, LOG_LEVEL, LOG_FORMAT
from core.chatroom import Chatroom, get_chatroom
from core.models import Message

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class WebSocketServer:
    """
    WebSocket server for real-time chat participation.
    
    Allows human users to:
    - Connect and receive live message updates
    - Send messages that agents will respond to
    - View chat history on connection
    - See other connected users
    """
    
    def __init__(self, host: str = WEBSOCKET_HOST, port: int = WEBSOCKET_PORT):
        """
        Initialize the WebSocket server.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self._clients: Dict[WebSocketServerProtocol, Dict[str, Any]] = {}
        self._chatroom: Chatroom = None
        self._server = None
        self._running = False
    
    async def initialize(self):
        """Initialize the server and chatroom."""
        self._chatroom = await get_chatroom()
        self._chatroom.on_message(self._broadcast_to_clients)
        logger.info("WebSocket server initialized")
    
    async def _broadcast_to_clients(self, message: Message):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast
        """
        if not self._clients:
            return
        
        data = json.dumps({
            "type": "message",
            "data": message.to_dict()
        })
        
        disconnected = []
        for client in self._clients:
            try:
                await client.send(data)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client)
        
        # Clean up disconnected clients
        for client in disconnected:
            await self._handle_disconnect(client)
    
    async def _handle_connect(
        self,
        websocket: WebSocketServerProtocol,
        username: str
    ):
        """
        Handle a new client connection.
        
        Args:
            websocket: The WebSocket connection
            username: Display name of the connecting user
        """
        user_id = str(uuid.uuid4())
        
        self._clients[websocket] = {
            "user_id": user_id,
            "username": username,
            "connected_at": datetime.now().isoformat()
        }
        
        self._chatroom.state.connected_humans.append(user_id)
        
        # Send welcome message with recent history
        history = self._chatroom.state.get_recent_messages(20)
        welcome_data = {
            "type": "welcome",
            "data": {
                "user_id": user_id,
                "username": username,
                "history": [msg.to_dict() for msg in history],
                "status": self._chatroom.get_status()
            }
        }
        await websocket.send(json.dumps(welcome_data))
        
        # Announce to chatroom
        await self._chatroom.add_human_message(
            content=f"*{username} has connected to the chat*",
            username="System",
            user_id="system"
        )
        
        logger.info(f"Client connected: {username} ({user_id})")
    
    async def _handle_disconnect(self, websocket: WebSocketServerProtocol):
        """
        Handle a client disconnection.
        
        Args:
            websocket: The disconnecting WebSocket
        """
        if websocket in self._clients:
            client_info = self._clients[websocket]
            username = client_info["username"]
            user_id = client_info["user_id"]
            
            del self._clients[websocket]
            
            if user_id in self._chatroom.state.connected_humans:
                self._chatroom.state.connected_humans.remove(user_id)
            
            # Announce departure
            await self._chatroom.add_human_message(
                content=f"*{username} has disconnected*",
                username="System",
                user_id="system"
            )
            
            logger.info(f"Client disconnected: {username}")
    
    async def _handle_message(
        self,
        websocket: WebSocketServerProtocol,
        raw_message: str
    ):
        """
        Handle an incoming message from a client.
        
        Args:
            websocket: The client's WebSocket
            raw_message: Raw JSON message string
        """
        try:
            data = json.loads(raw_message)
            msg_type = data.get("type", "chat")
            
            if msg_type == "chat":
                client_info = self._clients.get(websocket, {})
                username = client_info.get("username", "Anonymous")
                user_id = client_info.get("user_id", "unknown")
                content = data.get("content", "")
                
                if content.strip():
                    await self._chatroom.add_human_message(
                        content=content,
                        username=username,
                        user_id=user_id
                    )
                    
                    # Trigger agent responses
                    asyncio.create_task(
                        self._chatroom.trigger_response_to_human()
                    )
            
            elif msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
            
            elif msg_type == "status":
                status = self._chatroom.get_status()
                await websocket.send(json.dumps({
                    "type": "status",
                    "data": status
                }))
            
            elif msg_type == "get_tasks":
                from core.task_manager import get_task_manager
                tm = get_task_manager()
                tasks = [t.to_dict() for t in tm.get_all_tasks()]
                await websocket.send(json.dumps({
                    "type": "tasks",
                    "data": tasks
                }))
            
            elif msg_type == "get_devplan":
                # Read master_plan.md from scratch/shared
                devplan_content = ""
                devplan_path = Path(__file__).parent.parent / "scratch" / "shared" / "master_plan.md"
                if devplan_path.exists():
                    try:
                        with open(devplan_path, 'r', encoding='utf-8') as f:
                            devplan_content = f.read()
                    except Exception:
                        devplan_content = "[Error reading master_plan.md]"
                else:
                    devplan_content = "No master plan yet. The Architect will create one during planning phase."
                
                await websocket.send(json.dumps({
                    "type": "devplan",
                    "data": devplan_content
                }))
            
            elif msg_type == "get_files":
                # Get file tree from scratch/shared
                files_tree = ""
                shared_path = Path(__file__).parent.parent / "scratch" / "shared"
                if shared_path.exists():
                    def build_tree(dir_path, prefix=""):
                        lines = []
                        try:
                            items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                            for i, item in enumerate(items):
                                is_last = i == len(items) - 1
                                connector = "└── " if is_last else "├── "
                                if item.is_dir():
                                    lines.append(f"{prefix}{connector}{item.name}/")
                                    extension = "    " if is_last else "│   "
                                    lines.extend(build_tree(item, prefix + extension))
                                else:
                                    lines.append(f"{prefix}{connector}{item.name}")
                        except Exception:
                            pass
                        return lines
                    
                    tree_lines = build_tree(shared_path)
                    files_tree = "shared/\n" + "\n".join(tree_lines) if tree_lines else "shared/ (empty)"
                else:
                    files_tree = "No shared folder yet."
                
                await websocket.send(json.dumps({
                    "type": "files",
                    "data": files_tree
                }))
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received: {raw_message[:100]}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _connection_handler(
        self,
        websocket: WebSocketServerProtocol,
        path: str = None
    ):
        """
        Handle a WebSocket connection lifecycle.
        
        Args:
            websocket: The WebSocket connection
            path: Request path (unused)
        """
        # Wait for initial identification message
        try:
            init_message = await asyncio.wait_for(
                websocket.recv(),
                timeout=10.0
            )
            init_data = json.loads(init_message)
            username = init_data.get("username", "Anonymous")
        except (asyncio.TimeoutError, json.JSONDecodeError):
            username = "Anonymous"
        
        await self._handle_connect(websocket, username)
        
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self._handle_disconnect(websocket)
    
    async def start(self):
        """Start the WebSocket server."""
        await self.initialize()
        
        self._running = True
        self._server = await websockets.serve(
            self._connection_handler,
            self.host,
            self.port
        )
        
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
        
        # Keep running until stopped
        try:
            await asyncio.Future()  # Run forever
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop the WebSocket server."""
        self._running = False
        
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        # Close all client connections
        for client in list(self._clients.keys()):
            try:
                await client.close()
            except:
                pass
        
        # Shutdown chatroom
        if self._chatroom:
            await self._chatroom.shutdown()
        
        logger.info("WebSocket server stopped")


async def main():
    """Main entry point for the WebSocket server."""
    server = WebSocketServer()
    
    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    
    def shutdown_handler():
        asyncio.create_task(server.stop())
    
    try:
        # Note: signal handlers work differently on Windows
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, shutdown_handler)
            except NotImplementedError:
                # Windows doesn't support add_signal_handler
                pass
    except:
        pass
    
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()


if __name__ == "__main__":
    print("Starting Multi-Agent Chatroom WebSocket Server...")
    print("Connect using the web client or any WebSocket client")
    print("Press Ctrl+C to stop")
    print()
    
    asyncio.run(main())
