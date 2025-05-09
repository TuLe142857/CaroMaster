import caro

def play(agent_x:caro.AI, agent_o:caro.AI, first_turn:str)->caro.GameRecord:
    pass

def match(agent_x:caro.AI, agent_o:caro.AI, number_of_game:int)->list[caro.GameRecord]:
    pass

def tournament(agents:list[caro.AI], n_game:int=50)->list[caro.GameRecord]:
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

def leader_board(game_records:list[caro.GameRecord]):
    pass