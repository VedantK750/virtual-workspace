from backend.domain.world import World
from backend.events.event_types import JOIN, MOVE, LEAVE, WORLD_STATE


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
    
    def handle_event(self, event: Event):
        if event.type == JOIN:
            self.world.add_player(event.user_id)
            
            snapshot = self.world.get_room_snapshot("default")

            return {
            "type": WORLD_STATE,
            "payload": {
                "players": snapshot
            }
        }

        if event.type == MOVE:
            # get new x and y from the payload
            x = event.payload.get("x")
            y = event.payload.get("y")
            
            if x is None or y is None:
                return None

            self.world.move_player(event.user_id, x, y)
            
            snapshot = self.world.get_room_snapshot("default")   
            
            return {
            "type": WORLD_STATE,
            "payload": {
                "players": snapshot
            }
        }



        if event.type == LEAVE:
            self.world.remove_player(event.user_id)
            snapshot = self.world.get_room_snapshot("default")

            return {
            "type": WORLD_STATE,
            "payload": {"players": snapshot}
            }
        
def main():
    world = World()
    dispatcher = EventDispatcher(world)
    
    join_event = Event("JOIN", "p1", {})
    print(dispatcher.handle_event(join_event))

    move_event = Event("MOVE", "p1", {"x": 100, "y": 200})
    print(dispatcher.handle_event(move_event))


if __name__ == "__main__":
    main()

            
