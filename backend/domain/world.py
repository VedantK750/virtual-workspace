from backend.domain.room import Room
from backend.domain.player import Player
'''
World is responsible for:

1. Creating rooms
2. Assigning players to rooms
3. Routing moves to correct room
4. Removing players globally

Room should not know about other rooms.
Player should not know about world.
'''

'''
Minimal responsibilities:

Maintain rooms dict
Create default room
Add player to room
Remove player
Route move request
Get snapshot for a room
'''

class World:
    def __init__(self):
        self.rooms: dict[str, Room] = {}
        self.player_room: dict[str, str] = {}
        self.create_room("default")
        
    def create_room(self, room_id: str, max_players : int = 50, size_x : int = 1000, size_y : int = 1000, threshold : int = 50):
        # create and store Room object
        self.rooms[room_id] = Room(room_id,max_players,size_x,size_y,threshold)

    def add_player(self, player_id: str, room_id="default", x=0, y=0):
        # create Player object
        # add to correct Room
        room = self.rooms.get(room_id)
        if not room:
            raise Exception("Room does not exist")
        player=Player(player_id,x,y,room_id)
        room.add_player(player)
        
        self.player_room[player_id] = room_id   # ← STORE MAPPING

    def remove_player(self, player_id: str):
        # remove from room
        # use the player_room map to get the room_id
        room_id = self.player_room.pop(player_id, None)
        if not room_id:
            raise Exception("Player does not exist!")
        room = self.rooms.get(room_id)
        if room:
            room.remove_player(player_id)

    def move_player(self, player_id: str, x: float, y: float):
        # route move to correct room
        # use the player_room map to get the room_id
        room_id = self.player_room.get(player_id)
        if not room_id:
            raise Exception("Player does not exist!")
        room = self.rooms.get(room_id)
        if not room:
            raise Exception("Room does not exist!")
        
        room.move_player(player_id, x, y)

    def get_room_snapshot(self, room_id: str):
        # return room.get_snapshot()
        return self.rooms[room_id].generate_snapshot()
    
    def debug_player_room(self):
        return self.player_room
    
    
    
    
def main():
    world = World()

    world.add_player("p1")
    world.add_player("p2")

    world.move_player("p1", 100, 200)

    print(world.get_room_snapshot("default"))
    print(world.debug_player_room())

if __name__ == "__main__":
    main()