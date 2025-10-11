DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

class State:
    def __init__(self, player, boxes):
        self.player = player
        self.boxes = frozenset(boxes) 
    
    def __eq__(self, other):
        return self.player == other.player and self.boxes == other.boxes
    
    def __hash__(self):
        return hash((self.player, self.boxes))