from typing import Callable
import caro
import random

class MiniMax(caro.AI):
    def __init__(
            self,
            name:str,
            depth: int,
            search_radius: int,
            random_move: int,
            evaluate_function: Callable[[caro.BoardState, str], float | int]
    ):
        self.depth = depth if depth >= 1 else 1
        self.search_radius = search_radius if search_radius >= 1 else 1
        self.random_move = random_move if random_move >= 0 else 0
        self.evaluate_function = evaluate_function
        super().__init__(name)

    def find_valid_moves(self, state: caro.BoardState) -> list[tuple[int, int]]:
        if len(state.get_empty_positions()) == caro.BOARD_SIZE ** 2:
            return state.get_empty_positions()

        all_moves = set()
        in_range = set()
        radius = [_ for _ in range(-self.search_radius, self.search_radius + 1)]
        for row in range(caro.BOARD_SIZE):
            for col in range(caro.BOARD_SIZE):
                if state.cells[row][col] == caro.EMPTY_CELL:
                    all_moves.add((row, col))
                    continue
                for dr in radius:
                    for dc in radius:
                        p = (row + dr, col + dc)
                        if (0 <= p[0] < caro.BOARD_SIZE and 0 <= p[1] < caro.BOARD_SIZE) \
                                and state.cells[p[0]][p[1]] == caro.EMPTY_CELL:
                            in_range.add(p)

        out_range = all_moves - in_range
        moves_1 = list(in_range)
        moves_2 = random.sample(list(out_range), min(self.random_move, len(out_range)))
        return moves_1 + moves_2

    def minimax(
            self,
            state: caro.BoardState,
            current_turn: str,
            depth_limit: int,
            alpha: int | float = float('-inf'),
            beta: int | float = float('inf')
    ) -> tuple[int | float, int]:
        # print("call", depth_limit)
        """
        :param state:
        :param current_turn:
        :param depth_limit:
        :param alpha:
        :param beta:
        :return: tuple(best eval, depth limit)
        """
        if depth_limit == 0 or state.status() != caro.NOT_FINISH:
            return self.evaluate_function(state, current_turn), depth_limit

        # x turn => find max eval
        if current_turn == caro.X_PIECE:
            best_eval = float('-inf')
            best_depth = 0
            for move in self.find_valid_moves(state):
                state.put(current_turn, move)
                current_eval, current_depth = self.minimax(state, caro.O_PIECE, depth_limit - 1, alpha, beta)
                state.put(caro.EMPTY_CELL, move)
                if (best_eval < current_eval) or (best_eval == current_eval and best_depth < current_depth):
                    best_eval = current_eval
                    best_depth = current_depth
                alpha = max(alpha, best_eval)

                if beta <= alpha:
                    break
            return best_eval, best_depth

        # o turn =< find min eval
        else:
            best_eval = float('inf')
            best_depth = 0
            for move in self.find_valid_moves(state):
                state.put(current_turn, move)
                current_eval, current_depth = self.minimax(state, caro.X_PIECE, depth_limit - 1, alpha, beta)
                state.put(caro.EMPTY_CELL, move)
                if (best_eval > current_eval) or (best_eval == current_eval and best_depth < current_depth):
                    best_eval = current_eval
                    best_depth = current_depth
                beta = min(beta, best_eval)

                if beta <= alpha:
                    break
            return best_eval, best_depth

    def decide_move(self, state: caro.BoardState, current_turn: str) -> tuple[int, int]:

        moves = self.find_valid_moves(state)
        random.shuffle(moves)
        best_move = moves[0]
        best_eval = float('-inf') if current_turn == caro.X_PIECE else float("inf")
        best_depth = 0
        opponent = caro.O_PIECE if current_turn == caro.X_PIECE else caro.X_PIECE

        for move in moves:
            state.put(current_turn, move)
            current_eval, current_depth = self.minimax(state, opponent, self.depth - 1)
            state.put(caro.EMPTY_CELL, move)

            # x turn => find max eval
            if current_turn == caro.X_PIECE:
                if (best_eval < current_eval) or (best_eval == current_eval and best_depth < current_depth):
                    best_eval = current_eval
                    best_depth = current_depth
                    best_move = move
            # o turn => find min eval
            else:
                if (best_eval > current_eval) or (best_eval == current_eval and best_depth < current_depth):
                    best_eval = current_eval
                    best_depth = current_depth
                    best_move = move
        return best_move

# test
if __name__ == '__main__':
    from app import App
    app = App(font_name='Roboto-Regular.ttf', unit_size=15)
    agent = MiniMax("minimax", depth=1, search_radius=1, random_move=0, evaluate_function=lambda e, p:0)
    def test(state):
        for m in agent.find_valid_moves(state):
            app.board.put(" ", m, background=(0, 255, 255))
    app.testing_mode(function=test, message="Test search radius")