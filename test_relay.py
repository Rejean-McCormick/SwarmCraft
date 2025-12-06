import asyncio
import websockets
import json

async def test():
    print("Connecting to relay...")
    async with websockets.connect('ws://localhost:8766') as ws:
        print("Connected! Waiting for data...")
        try:
            # Get first message
            data = await asyncio.wait_for(ws.recv(), timeout=10)
            print(f"Received {len(data)} bytes")
            parsed = json.loads(data)
            print('Type:', parsed.get('type'))
            
            if parsed.get('type') == 'test':
                print('Test message:', parsed.get('message'))
                # Wait for next message
                data2 = await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"Second message: {len(data2)} bytes")
                parsed = json.loads(data2)
                print('Type:', parsed.get('type'))
            
            if parsed.get('type') == 'error':
                print('ERROR from relay:', parsed.get('message'))
                # Wait for state after error
                data3 = await asyncio.wait_for(ws.recv(), timeout=5)
                parsed = json.loads(data3)
                print('After error type:', parsed.get('type'))
            
            if parsed.get('type') == 'state':
                print('Agents:', len(parsed.get('state', {}).get('agents', [])))
                print('Tasks:', len(parsed.get('state', {}).get('tasks', [])))
                if parsed.get('state', {}).get('agents'):
                    for a in parsed['state']['agents'][:5]:
                        print(f"  Agent: {a.get('name')} - status={a.get('status')}")
                else:
                    print("  No agents found!")
        except asyncio.TimeoutError:
            print("TIMEOUT - no data received from relay!")

asyncio.run(test())
