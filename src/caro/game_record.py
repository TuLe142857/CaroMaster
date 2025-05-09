from .constants import *
from .board_state import BoardState
from typing import  Any
import json
import time

class GameRecord:
    def __init__(
            self,
            first_turn:str,
            player_x_name:str,
            player_o_name:str
    ):
        if first_turn != O_PIECE and first_turn != X_PIECE:
            raise RuntimeError("Invalid first turn value")

        self.player_x = player_x_name
        self.player_o = player_o_name
        self.first_turn = first_turn
        self.moves = []
        self.move_timestamps = []

    @staticmethod
    def from_dict(data: dict[str, Any])->'GameRecord':
        r = GameRecord(
            player_x_name=data['player x'],
            player_o_name=data['player o'],
            first_turn=data['first turn']
        )
        r.moves = [tuple(move) for move in data['moves']]
        r.move_timestamps = data['move timestamps']
        return r

    @staticmethod
    def load_from_file(path) -> list['GameRecord']:
        with open(path, 'r') as file:
            data = json.load(file)
            records = [GameRecord.from_dict(x) for x in data]
            return records

    @staticmethod
    def save_to_file(path, records: list['GameRecord']|Any):
        """
        If `records` is a single GameRecord instance, it will be automatically
        converted into a list containing that instance.
        :param path:
        :param records: list[GameRecord] or GameRecord
        """
        if isinstance(records, GameRecord):
            records = [records]
        with open(path, 'w') as file:
            data = [x.to_dict() for x in records]
            json.dump(data, file, indent=4)


    def add_move(
            self,
            position: tuple[int, int] | list[int],
            timestamp: float | None = None
    ):
        """

        :param position: tuple[row, column]
        :param timestamp: If timestamp is None => timestamp = now
        """
        if position in self.moves:
            raise RuntimeError("This position is not empty!")
        self.moves.append(position)
        self.move_timestamps.append(timestamp if timestamp is not None else time.time())

    def remove_last_move(self):
        if len(self.moves) == 0:
            return
        self.moves.pop()
        self.move_timestamps.pop()

    def result(self):
        """
        :return: X_WIN, O_WIN, DRAW, NOT_FINISH
        """
        return BoardState.from_moves(self.moves, self.first_turn).status()

    def to_dict(self)->dict[str, Any]:
        return  {
            'player x': self.player_x,
            'player o': self.player_o,
            'first turn': self.first_turn,
            'moves': self.moves,
            'move timestamps': self.move_timestamps
        }

    def __str__(self):
        s = f'Game record between {self.player_x}(X) vs {self.player_o}(O)\n'
        s += f'First turn: {self.first_turn}\n'
        piece = [self.first_turn, X_PIECE if self.first_turn == O_PIECE else O_PIECE]

        s += "Move - TimeStamp:\n"
        for i in range(len(self.moves)):
            s += f'{i}. {piece[i%2]} - {self.moves[i]} at {self.move_timestamps[i]}\n'

        board_state = BoardState.from_moves(self.moves, self.first_turn)
        status = board_state.status()
        if status == DRAW:
            s += "Result: DRAW!\n"
        elif status == X_WIN:
            s += f"Result: {self.player_x}(X) WIN!\n"
        elif status == O_WIN:
            s += f"Result: {self.player_o}(O) WIN !\n"
        else:
            s += "Result: GAME NOT FINISH\n"
        return s

    def __repr__(self):
        return  self.__str__()