from backend.domain.player import Player

'''
Room is the manager.

Room must:
1. Store players
2. Add player
3. Remove player
4. Move player
5. Generate snapshot
6. (Optional later) detect proximity
'''

class Room:
    def __init__(self, room_id: str, max_players: int, size_x: int, size_y: int, threshold: float):
        self.room_id = room_id
        self.max_players = max_players
        self.size_x = size_x
        self.size_y = size_y
        self.threshold = threshold
        # store id with obj, O(1) lookups
        self.players: dict[str, Player] = {} 

        
    def add_player(self, player: Player):
        if len(self.players) >= self.max_players:
            raise Exception("Room is Full!")

        self.players[player.id] = player
        
    def remove_player(self, player_id : str):
        del self.players[player_id]
        
    def move_player(self, player_id : str, new_x: float, new_y : float ):
        player = self.players.get(player_id)
        if not player:
            return
        
        if 0 <= new_x <= self.size_x and 0 <= new_y <= self.size_y:
            player.move(new_x, new_y)
            
    def generate_snapshot(self):
        return [
            {
                "id": player.id,
                "x": player.x,
                "y": player.y
            } for player in self.players.values()
        ]