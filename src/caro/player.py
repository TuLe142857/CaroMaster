from .board_state import BoardState

class Player:
    def __init__(self, name:str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Human(Player):
    def __init__(self, name:str):
        super().__init__(name)

class AI(Player):
    def __init__(self, name:str):
        super().__init__(name)

    def decide_move(self, state:BoardState, current_turn:str)->tuple[int, int]:
        pass