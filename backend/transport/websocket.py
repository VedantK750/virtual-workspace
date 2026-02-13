from fastapi import WebSocket, WebSocketDisconnect
import json
import uuid

from backend.events.dispatcher import EventDispatcher, Event
from backend.events.event_types import JOIN, WORLD_STATE
from backend.domain.world import World

class ConnectionManager:
    def __init__(self):
        # map to store active ws connections
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_to(self, user_id: str, message:str):
        '''
        Send a message to one specific client
        Private message
        Error response (“Invalid move”)
        Confirmation
        Whisper chat
        Only notify the mover
        '''
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)
            
    async def broadcast(self, message: dict):
        '''
        Send message to all connected clients.
        World state changes
        Player joins
        Player moves
        Player leaves
        '''
        for ws in self.active_connections.values():
            await ws.send_json(message)

manager = ConnectionManager()
world = World()
dispatcher = EventDispatcher(world)


async def websocket_endpoint(websocket: WebSocket):
    user_id = str(uuid.uuid4())
    await manager.connect(websocket, user_id)
    
    join_event = Event(JOIN, user_id, {})
    # JSON response after JOIN by the dispatcher
    response = dispatcher.handle_event(join_event)
    
    if response:
        # player JOINED so broadcast
        await manager.send_to(user_id,response)
        
        snapshot = world.get_room_snapshot("default")
        
        await manager.broadcast({
            "type": "WORLD_STATE",
            "payload": {
                "players": snapshot
            }
        })
    
    try:
        while True:
            data = await websocket.receive_text()
            json_data = json.loads(data)

            # creating an Event obj
            event = Event(
                event_type=json_data["type"],
                user_id=user_id,
                payload=json_data.get("payload", {})
            )
            
            response = dispatcher.handle_event(event)
            
            if response:
                await manager.broadcast(response)

    except WebSocketDisconnect:
        # Abrupt Disconnect
        manager.disconnect(user_id)
        response = dispatcher.handle_event(Event("LEAVE", user_id, {}))
        #server state must always be pushed to clients after mutation. 
        if response:
            await manager.broadcast(response)

        


    
    