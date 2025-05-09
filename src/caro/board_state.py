from .constants import *

class BoardState:
    @staticmethod
    def from_moves(moves: list[tuple[int, int] | list[int]], first_turn: str):
        if not (first_turn == O_PIECE or first_turn == X_PIECE):
            raise RuntimeError("Invalid first turn")
        piece = [first_turn, O_PIECE if first_turn == X_PIECE else X_PIECE]
        state = BoardState()
        for i in range(len(moves)):
            state.put(piece[i % 2], moves[i])
        return state

    def __init__(self):
        """
        cells[row][column]
        """
        self.cells = [[EMPTY_CELL for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def get(self, position:tuple[int, int]|list[int])->str:
        """

        :param position: tuple[row, column]
        """
        return self.cells[position[0]][position[1]]

    def put(self, piece:str, position:tuple[int, int]|list[int]):
        """

        :param piece: X_PIECE or O_PIECE
        :param position: tuple[row, column]
        """
        if not (piece == X_PIECE or piece == O_PIECE or piece == EMPTY_CELL):
            raise RuntimeError("Invalid piece value")
        self.cells[position[0]][position[1]] = piece

    def __str__(self)->str:
        lines = ['|' + '|'.join(row) + '|' for row in self.cells ]
        return '\n'.join(lines)

    def clone(self)->'BoardState':
        new_state = BoardState()
        new_state.cells = [[x for x in row] for row in self.cells]
        return new_state

    def get_empty_positions(self)->list[tuple[int, int]]:
        """

        :return: list( tuple[row, column] )
        """
        l = []
        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                if self.cells[row][column] == EMPTY_CELL:
                    l.append((row, column))
        return l

    def clear(self):
        """
        set all cells = EMPTY_CELL
        """
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self.cells[r][c] = EMPTY_CELL

    def check_win_at_position(self, position:tuple[int, int])->bool:
        """

        :param position: tuple[row, column]
        :return: true if (X or O win the game)
        """
        if self.cells[position[0]][position[1]] == EMPTY_CELL:
            return False
        piece = self.cells[position[0]][position[1]]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for d in directions:
            count = 1
            d_ = (-d[0], -d[1])

            # d
            pos = [position[0], position[1]]
            while count < WIN_LENGTH:
                pos[0] += d[0]
                pos[1] += d[1]
                if not (0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE):
                    break
                if self.cells[pos[0]][pos[1]] != piece:
                    break
                count += 1

            # d_
            pos = [position[0], position[1]]
            while count < WIN_LENGTH:
                pos[0] += d_[0]
                pos[1] += d_[1]
                if not (0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE):
                    break
                if self.cells[pos[0]][pos[1]] != piece:
                    break
                count += 1

            if count == WIN_LENGTH:
                return True
        return False

    def status(self)->int:
        """

        :return: constants X_WIN, O_WIN, DRAW, NOT_FINISH
        """

        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                if self.check_win_at_position((row, column)):
                    return X_WIN if self.cells[row][column] == X_PIECE else O_WIN

        if len(self.get_empty_positions()) == 0:
            return DRAW
        return NOT_FINISH

    def get_winning_sequence(self) -> list[tuple[int, int]]:
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.cells[row][col]
                if piece == EMPTY_CELL:
                    continue
                for d in directions:
                    seq = [(row, col)]
                    r, c = row, col
                    for _ in range(WIN_LENGTH - 1):
                        r += d[0]
                        c += d[1]
                        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                            break
                        if self.cells[r][c] != piece:
                            break
                        seq.append((r, c))
                    if len(seq) == WIN_LENGTH:
                        return seq
        return []