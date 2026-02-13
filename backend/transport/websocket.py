from fastapi import WebSocket, WebSocketDisconnect
import json
import uuid

from backend.events.dispatcher import EventDispatcher, Event
from backend.events.event_types import JOIN, WORLD_STATE, LEAVE
from backend.domain.world import World

class ConnectionManager:
    def __init__(self):
        # map to store active ws connections
        # user_id → websocket
        self.active_connections: dict[str, WebSocket] = {}
        # room_id → set(user_ids)
        self.room_connections: dict[str, set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, room_id:str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        # Add user to room mapping
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
            
        self.room_connections[room_id].add(user_id)


    def disconnect(self, user_id: str,room_id: str):
        self.active_connections.pop(user_id, None)
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(user_id)
            
            # if no users in room, del the room (i.e. the set is empty)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict):
        user_ids = self.room_connections.get(room_id, set())
        for uid in user_ids:
            ws = self.active_connections.get(uid)
            if ws:
                await ws.send_json(message)


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
    room_id = websocket.query_params.get("room", "default")
    if room_id not in world.rooms:
        world.create_room(room_id, max_players=10, size_x=800, size_y=600, threshold=100)

    await manager.connect(websocket, user_id, room_id)
    
    join_event = Event(JOIN, user_id, {"room_id": room_id})
    # JSON response after JOIN by the dispatcher
    response = dispatcher.handle_event(join_event)
    
    if response:
        # player JOINED so broadcast
        await manager.send_to(user_id,response)
        
        snapshot = world.get_room_snapshot(room_id)
        
        await manager.broadcast_to_room(room_id,{
            "type": WORLD_STATE,
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
                room_id = world.player_room[user_id]
                await manager.broadcast_to_room(room_id, response)


    except WebSocketDisconnect:
        # Abrupt Disconnect
        manager.disconnect(user_id, room_id)
        response = dispatcher.handle_event(Event(LEAVE, user_id, {}))
        #server state must always be pushed to clients after mutation. 
        if response:
            await manager.broadcast_to_room(room_id, response)

        


    
    