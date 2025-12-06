# Implementation Phases: Multi-Agent AI Chatroom

This document breaks down the project into atomic, executable phases following Circular Development methodology.

---

## Phase 1: Foundation Setup

### 1.1 Create Project Structure
```bash
mkdir multi_agent_chat
cd multi_agent_chat
mkdir agents core integrations web config
```

### 1.2 Create Requirements
Create `requirements.txt`:
```
aiohttp>=3.9.0
python-dotenv>=1.0.0
websockets>=12.0
disnake>=2.9.0
aiosqlite>=0.19.0
asyncio-throttle>=1.0.2
```

### 1.3 Create Configuration Module
Create `config/settings.py`:
- Z.ai API configuration
- Memory settings
- WebSocket configuration
- Discord configuration
- Helper functions

### 1.4 Create Data Models
Create `core/models.py`:
- `Message` dataclass
- `AgentConfig` dataclass
- `MemoryEntry` dataclass
- `ChatroomState` dataclass
- Enum types (MessageRole, MessageType)

**Checkpoint**: Run `python -c "from core.models import Message"` - should import without errors

---

## Phase 2: Memory System

### 2.1 Create Memory Store
Create `core/memory_store.py`:
- SQLite async database setup
- CRUD operations for memories
- Search and retrieval functions
- Statistics and management

### 2.2 Create Summarizer
Create `core/summarizer.py`:
- API integration for summarization
- Fact extraction logic
- `ConversationMemoryManager` class
- Memory lifecycle handling

**Checkpoint**: Write a test that stores and retrieves a memory entry

---

## Phase 3: Agent Framework

### 3.1 Create Base Agent
Create `agents/base_agent.py`:
- Abstract `BaseAgent` class
- Short-term memory management
- API call handling
- Response generation
- Memory integration

### 3.2 Create Professor Byte Agent
Create `agents/professor_byte.py`:
- Full system prompt
- Configuration
- Persona description

### 3.3 Create HexMage Agent
Create `agents/hexmage.py`:
- Chaotic persona prompt
- High temperature settings
- Quick response style

### 3.4 Create Synthia Agent
Create `agents/synthia.py`:
- Poetic persona prompt
- Creative temperature settings
- Metaphorical style

### 3.5 Create Bureaucrat-9000 Agent
Create `agents/bureaucrat9000.py`:
- Bureaucratic persona prompt
- Form-obsessed style
- Lower temperature for consistency

### 3.6 Create Lumen Agent
Create `agents/lumen.py`:
- Empathetic persona prompt
- Mediator behaviors
- Emotional intelligence focus

### 3.7 Create Krait Agent
Create `agents/krait.py`:
- Cryptic persona prompt
- Cyberpunk aesthetics
- Lower verbosity

### 3.8 Create Agent Package
Create `agents/__init__.py`:
- Export all agents
- Factory functions
- Default agent list

**Checkpoint**: `from agents import create_all_default_agents` should return 6 agents

---

## Phase 4: Chatroom Core

### 4.1 Create Chatroom Orchestrator
Create `core/chatroom.py`:
- Agent management
- Message routing
- Conversation rounds
- History persistence
- Broadcast system

### 4.2 Create Main Entry Point
Create `main.py`:
- CLI interface
- Configuration validation
- Conversation loop
- Graceful shutdown

**Checkpoint**: `python main.py` should start (may fail on API key, but structure works)

---

## Phase 5: WebSocket Integration

### 5.1 Create WebSocket Server
Create `core/websocket_server.py`:
- Connection handling
- Message routing
- Broadcasting
- Status updates

### 5.2 Create Web Client
Create `web/client.html`:
- Modern dark theme UI
- WebSocket connection
- Message display
- Input handling

**Checkpoint**: Server should start and accept connections

---

## Phase 6: Discord Integration

### 6.1 Create Discord Bot
Create `integrations/discord_bot.py`:
- Slash command setup
- Channel connection management
- Message relaying
- Status commands

**Checkpoint**: Bot should connect (with valid token)

---

## Phase 7: Documentation

### 7.1 Create README
Create `README.md`:
- Installation instructions
- Usage guide
- Configuration reference
- Extension guide

### 7.2 Create Development Plan
Create `devplan.md`:
- Architecture overview
- Data flow diagrams
- Component specifications

### 7.3 Create Phases Document
Create `phases.md`:
- This document

### 7.4 Create Handoff Document
Create `handoff.md`:
- Project state summary
- Next steps
- Known issues

---

## Phase 8: Testing & Validation

### 8.1 Validate Imports
```bash
python -c "from agents import create_all_default_agents; print(len(create_all_default_agents()))"
# Should print: 6
```

### 8.2 Validate Configuration
```bash
python -c "from config.settings import validate_config; print(validate_config())"
# Should print tuple with validation status
```

### 8.3 Test Memory Store
```bash
python -c "
import asyncio
from core.memory_store import MemoryStore
from core.models import MemoryEntry

async def test():
    store = MemoryStore()
    await store.initialize()
    entry = MemoryEntry(content='test', agent_id='test_agent')
    await store.store_memory(entry)
    memories = await store.get_memories('test_agent')
    print(f'Stored and retrieved: {len(memories)} memories')

asyncio.run(test())
"
```

### 8.4 Full Integration Test
1. Set `ZAI_API_KEY` in `.env`
2. Run `python main.py`
3. Observe agent conversation
4. Verify messages appear correctly

---

## Completion Checklist

- [ ] All files created
- [ ] Dependencies installable
- [ ] Configuration loads correctly
- [ ] Agents instantiate without errors
- [ ] Memory store initializes
- [ ] Main script runs (with API key)
- [ ] WebSocket server starts
- [ ] Web client connects
- [ ] Discord bot connects (with token)
- [ ] Documentation complete

---

## Phase 9: Dynamic Orchestration (Complete)

### 9.1 Strict Protocol
- Implemented `AgentStatus` (IDLE/WORKING)
- Implemented `TaskStatus` (PENDING/IN_PROGRESS/COMPLETED)
- Workers are silent unless assigned a task

### 9.2 Central Task Registry
- Created `TaskManager` singleton
- Tracks all tasks and results

### 9.3 Startup Refinement
- Solo Architect Start
- Green Light Protocol
- Dynamic Spawning with unique names

### 9.4 Tool Enhancements
- Added `move_file` tool
- Added `spawn_worker`, `assign_task`, `get_swarm_state` tools

---

## Phase 10: Future Work

- [ ] Vector Memory Search
- [ ] Multi-Room Support
- [ ] Advanced Analytics

