from backend.domain.world import World
from backend.events.event_types import JOIN, MOVE, LEAVE, WORLD_STATE, SWITCH_ROOM


'''
Example
{
  "type": "MOVE",
  "payload": {
    "x": 100,
    "y": 200
  }
}
'''


class Event:
    def __init__(self, event_type: str, user_id: str, payload : dict):
        self.type = event_type
        self.user_id = user_id
        self.payload = payload
        
    
class EventDispatcher:
    def __init__(self, world: World):
        self.world = world
        
    def _build_world_state(self, room_id: str):
        snapshot = self.world.get_room_snapshot(room_id)
        return {
            "type": WORLD_STATE,
            "payload": {
                "players": snapshot
            }
        }
    
    def handle_event(self, event: Event):
        if event.type == JOIN:
            room_id = event.payload.get("room_id", "default")
            self.world.add_player(event.user_id, room_id=room_id)
            print("World mapping after JOIN:", self.world.player_room)
            
            return {
            "type": "JOIN_SUCCESS",
            "payload": {
                "players": self.world.get_room_snapshot(room_id),
                "your_id" : event.user_id
            }
        }

        if event.type == MOVE:
            # get new x and y from the payload
            x = event.payload.get("x")
            y = event.payload.get("y")
            
            if x is None or y is None:
                return None

            self.world.move_player(event.user_id, x, y)
            
            room_id = self.world.player_room[event.user_id]
            return self._build_world_state(room_id)
        
        if event.type == SWITCH_ROOM:
            new_room = event.payload.get("room_id")
            if not new_room:
                return None
            old_room = self.world.player_room.get(event.user_id)
            
            if old_room == new_room:
                return None
            # REMOVE player from old room
            self.world.remove_player(event.user_id)
            
            # Create room if needed (rn hardcoded)
            if new_room not in self.world.rooms:
                self.world.create_room(new_room, 10, 800, 600, 100)
                
            # Add to new room
            self.world.add_player(event.user_id, room_id=new_room)
            
            return {
            "type": "ROOM_SWITCH_SUCCESS",
            "payload": {
            "room_id": new_room,
            "players": self.world.get_room_snapshot(new_room)
            }
        }





        if event.type == LEAVE:
            self.world.remove_player(event.user_id)
            
            room_id = self.world.player_room[event.user_id]
            return self._build_world_state(room_id)
        
        return None
        
def main():
    world = World()
    dispatcher = EventDispatcher(world)
    
    join_event = Event("JOIN", "p1", {})
    print(dispatcher.handle_event(join_event))

    move_event = Event("MOVE", "p1", {"x": 100, "y": 200})
    print(dispatcher.handle_event(move_event))


if __name__ == "__main__":
    main()

            
