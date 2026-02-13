'''
Player does NOT 
1. Assign room
2. Check Threshold
3. Know about other players in the room
4. Broadcast updates

IT IS A DUMB entity!
'''

class Player:
    def __init__(self,id : str, x: float, y : float, room_id : str):
        self.id = id
        self.x = x
        self.y = y
        self.room_id = room_id        
        
    def get_pos(self):
        return self.x, self.y
    
    def move(self, new_x: float, new_y = float):
        self.x = new_x
        self.y = new_y
        
