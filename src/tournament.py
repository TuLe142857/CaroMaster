from typing import Any
import warnings
import caro

def play(agent_x:caro.AI, agent_o:caro.AI, first_turn:str)->caro.GameRecord:
    # check
    if not (isinstance(agent_x, caro.AI) and isinstance(agent_o, caro.AI)):
        raise RuntimeError("Agent must extend caro.AI")
    if not (first_turn == caro.X_PIECE or first_turn == caro.O_PIECE):
        raise RuntimeError("Invalid first turn")

    player = {caro.X_PIECE:agent_x, caro.O_PIECE:agent_o}
    current_turn = first_turn
    board_state = caro.BoardState()
    game_record = caro.GameRecord(player_x_name=agent_x.name, player_o_name=agent_o.name, first_turn=first_turn)
    while board_state.status() == caro.NOT_FINISH:
        move = player[current_turn].decide_move(board_state.clone(), current_turn)
        board_state.put(current_turn, move)
        game_record.add_move(move)

        # change turn
        current_turn = caro.X_PIECE if current_turn == caro.O_PIECE else caro.O_PIECE

    return game_record

def match(agent_x:caro.AI, agent_o:caro.AI, number_of_game:int)->list[caro.GameRecord]:
    # check
    if not (isinstance(agent_x, caro.AI) and isinstance(agent_o, caro.AI)):
        raise RuntimeError("Agent must extend caro.AI")
    if number_of_game <= 0:
        raise RuntimeError("Number of game must > 0")

    game_records = []
    first_turn = caro.X_PIECE
    print(f"{agent_x.name} vs {agent_o.name}")
    for i in range(number_of_game):
        print(f"\tgame {i+1}/{number_of_game}:", end=" ")
        record = play(agent_x, agent_o, first_turn=first_turn)
        game_records.append(record)

        # change first turn after each game
        first_turn = caro.X_PIECE if first_turn == caro.O_PIECE else caro.O_PIECE

        result = record.result()
        str_result = f"{agent_x.name} win" if result == caro.X_WIN else f"{agent_o.name} win" if result == caro.O_WIN else "draw"
        print(f"{str_result} after {len(record.moves)} moves")

    return game_records

def tournament(agents:list[caro.AI], n_game:int=5)->list[caro.GameRecord]:
    """
     Run a round-robin tournament where each agent plays against every other agent.
    :param agents: list of agent
    :param n_game: Number of games played between each pair of agents.
    :return: list[game record]
    """
    # Ensure all agent names are unique
    for i in range(len(agents)):
        if not isinstance(agents[i], caro.AI):
            raise RuntimeError("All agents must extend class caro.AI")
        for j in range(i+1, len(agents)):
            if agents[i].name == agents[j].name:
                raise RuntimeError("Duplicate agent name")

    game_records = []
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            game_records += match(agents[i], agents[j], n_game)
    return game_records

def analyze_game_record(game_records:list[caro.GameRecord]):
    # check
    for r in game_records:
        if r.player_x == r.player_o:
            raise RuntimeError(f"Invalid game record: Agent '{r.player_x}' cannot play against itself")
    agent_names = set()
    for r in game_records:
        agent_names.add(r.player_x)
        agent_names.add(r.player_o)
    agent_names = list(agent_names)

    name_to_id = {agent_names[i]:i for i in range(len(agent_names))}
    statistics = []
    move_count = [0 for _ in range(len(agent_names))] # use for calculate avg thinking time
    for n in agent_names:
        statistics.append({
            "name": n,
            "win":  0,
            "loss": 0,
            "draw": 0,
            "avg thinking time": 0
        })

    matches = dict()
    for i in range(len(agent_names)):
        matches[agent_names[i]] = dict()
        for j in range(len(agent_names)):
            if i == j:
                continue
            matches[agent_names[i]][agent_names[j]] = {
                "win": 0,
                "loss": 0,
                "draw": 0,
                "avg moves per game": 0
            }

    def update_matches(agent1:str, agent2:str, result, n_moves):
        # result agent1 vs agent2: win 1, draw 0, loss -1
        n_game =  matches[agent1][agent2]['win'] + matches[agent1][agent2]['draw'] +matches[agent1][agent2]['loss']
        old_avg  = matches[agent1][agent2]['avg moves per game']
        matches[agent1][agent2]['avg moves per game'] = ((old_avg * n_game) + n_moves)/(n_game + 1)
        if result == 1:
            matches[agent1][agent2]['win'] += 1
        elif result == -1:
            matches[agent1][agent2]['loss'] += 1
        elif result == 0:
            matches[agent1][agent2]['draw'] += 1

    def update_statistics(name, result, n_moves, total_thinking_time):
        score_id = name_to_id[name]

        # update avg time
        old_n = move_count[score_id]
        new_n = old_n + n_moves
        old_avg = statistics[score_id]['avg thinking time']
        statistics[score_id]['avg thinking time'] = ((old_avg*old_n)+total_thinking_time)/new_n
        move_count[score_id] = new_n

        # update result
        if result == 1:
            statistics[score_id]['win'] += 1
        elif result == -1:
            statistics[score_id]['loss'] += 1
        elif result == 0:
            statistics[score_id]['draw'] += 1

    for r in game_records:
        game_result = r.result()

        n_move_0 = len(r.moves)//2
        if (len(r.moves) %2) == 1:
            n_move_0 += 1
        n_move_1 = len(r.moves)//2
        total_time_0 = sum([r.move_timestamps[i] - r.move_timestamps[i-1] for i in range(2, len(r.moves), 2)])
        total_time_1 = sum([r.move_timestamps[i] - r.move_timestamps[i-1] for i in range(1, len(r.moves), 2)])

        if r.first_turn == caro.X_PIECE:
            x_n = n_move_0
            o_n = n_move_1

            x_t = total_time_0
            o_t = total_time_1
        else:
            x_n = n_move_1
            o_n = n_move_0

            x_t = total_time_1
            o_t = total_time_0

        if game_result == caro.X_WIN:
            # update matches
            update_matches(r.player_x, r.player_o, 1, len(r.moves))
            update_matches(r.player_o, r.player_x, -1, len(r.moves))

            # update statistics
            update_statistics(r.player_x, 1, x_n, x_t)
            update_statistics(r.player_o, -1, o_n, o_t)
        elif game_result == caro.O_WIN:
            # update matches
            update_matches(r.player_x, r.player_o, -1, len(r.moves))
            update_matches(r.player_o, r.player_x, 1, len(r.moves))

            # update statistics
            update_statistics(r.player_x, -1, x_n, x_t)
            update_statistics(r.player_o, 1, o_n, o_t)
        elif game_result == caro.DRAW:
            # update matches
            update_matches(r.player_x, r.player_o, 0, len(r.moves))
            update_matches(r.player_o, r.player_x, 0, len(r.moves))

            # update statistics
            update_statistics(r.player_x, 0, x_n, x_t)
            update_statistics(r.player_o, 0, o_n, o_t)
        elif game_result == caro.NOT_FINISH:
            warnings.warn("There is an unfinished game in game records. This game will be ignored.")

    return  statistics, matches