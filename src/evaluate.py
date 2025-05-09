import caro

def evaluate(state:caro.BoardState, current_turn:str):
    if not (current_turn == caro.X_PIECE or current_turn == caro.O_PIECE):
        raise RuntimeError("Invalid current turn")
    x, o = evaluate_for_x_o(state, current_turn)
    return x-o

def evaluate_for_x_o(state:caro.BoardState, current_turn:str):
    if not (current_turn == caro.X_PIECE or current_turn == caro.O_PIECE):
        raise RuntimeError("Invalid current turn")

    status = state.status()
    if status == caro.X_WIN:
        return float('inf'), 0
    elif status == caro.O_WIN:
        return 0, float('inf')
    elif status == caro.DRAW:
        return 0, 0

    eval_x = 0
    eval_o = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for d in directions:
        x, o = calc_eval_by_direction(state, current_turn, d)
        eval_x += x
        eval_o += o
    return eval_x, eval_o

def calc_eval_by_direction(state:caro.BoardState, current_turn:str, direction:tuple[int, int])->tuple[int|float, int|float]:
    if not (current_turn == caro.X_PIECE or current_turn == caro.O_PIECE):
        raise RuntimeError("Invalid current turn")

    explored = set()
    eval_x = 0
    eval_o = 0
    for row in range(caro.BOARD_SIZE):
        for column in range(caro.BOARD_SIZE):
            if ((row, column) in explored) or (state.get((row, column)) == caro.EMPTY_CELL):
                continue
            chain = find_chain(state, (row, column), direction)
            for pos in chain['chain']:
                explored.add(pos)
            if state.get((row, column)) == caro.X_PIECE:
                eval_x += calculation_chain(len(chain['before']), len(chain['chain']), len(chain['after']), current_turn==caro.X_PIECE)
            else:
                eval_o += calculation_chain(len(chain['before']), len(chain['chain']), len(chain['after']), current_turn==caro.O_PIECE)
    return eval_x, eval_o

def calculation_chain(before:int, chain:int, after:int, is_current_turn:bool)->int|float:
    if (before + chain + after) < caro.WIN_LENGTH:
        return 0

    # 1 left 1 win
    if chain == caro.WIN_LENGTH -1:
        if (before + chain) >= caro.WIN_LENGTH and (after+chain) >= caro.WIN_LENGTH:
            return 10**9 if is_current_turn else 10**8
        else:
            return 10 **9 if is_current_turn else 10*5

    # 2 left to win
    elif chain == caro.WIN_LENGTH - 2:
        if (before + chain) >= caro.WIN_LENGTH and (after+chain) >= caro.WIN_LENGTH:
            return 10**7 if is_current_turn else 10**6
        else:
            return 10**4 if is_current_turn else 10**3

    # other
    if (before + chain) >= caro.WIN_LENGTH and (after + chain) >= caro.WIN_LENGTH:
        return 100*chain
    else:
        return 50 * chain

def find_chain(state:caro.BoardState, position:tuple[int, int], direction:tuple[int, int])->dict[str, list[tuple[int, int]]]:
    result =  {"before":[], "chain":[position], "after":[]}
    piece = state.get(position)

    d = direction
    d_ = (-d[0], -d[1])

    # di theo huong d
    end = position # diem ket thuc
    r, c = position
    r += d[0]
    c += d[1]
    while (0 <= r < caro.BOARD_SIZE and 0 <= c < caro.BOARD_SIZE) and state.get((r, c)) == piece:
        result['chain'].append((r, c))
        end = (r, c)
        r += d[0]
        c += d[1]

    # di theo huong d_
    r, c = position
    start = position # diem bat dau
    r += d_[0]
    c += d_[1]
    while (0 <= r < caro.BOARD_SIZE and 0 <= c < caro.BOARD_SIZE) and state.get((r, c)) == piece:
        result['chain'].append((r, c))
        start = (r, c)
        r += d_[0]
        c += d_[1]

    # before: di tu start , di theo d_
    r, c = start
    r += d_[0]
    c += d_[1]
    while (0 <= r < caro.BOARD_SIZE and 0 <= c < caro.BOARD_SIZE) and (state.get((r, c)) == piece or state.get((r, c)) == caro.EMPTY_CELL):
        result['before'].append((r, c))
        r += d_[0]
        c += d_[1]
        if len(result['before']) == caro.WIN_LENGTH:
            break

    # after: di tu end, di theo d
    r, c = end
    r += d[0]
    c += d[1]
    while (0 <= r < caro.BOARD_SIZE and 0 <= c < caro.BOARD_SIZE) and (state.get((r, c)) == piece or state.get((r, c)) == caro.EMPTY_CELL):
        result['after'].append((r, c))
        r += d[0]
        c += d[1]
        if len(result['after']) == caro.WIN_LENGTH:
            break

    return result

# test
if __name__ == '__main__':
    from app import App
    app = App(font_name='Roboto-Regular.ttf', unit_size=15)

    def test(state):
        print("if current turn is x:")
        print("\teval x, eval o = ", evaluate_for_x_o(state, caro.X_PIECE))
        print("\tEval:",  evaluate(state, caro.X_PIECE))

        print("if current turn is o:")
        print("\teval x, eval o = ", evaluate_for_x_o(state, caro.O_PIECE))
        print("\tEval:", evaluate(state, caro.X_PIECE))
        print("-"*50, "\n")
    app.testing_mode(function=test, message="Test evaluate function")