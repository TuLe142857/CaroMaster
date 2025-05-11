import os
import time
import pygame
from app import App
from minimax import MiniMax
from evaluate import evaluate
import caro
import tournament

# game record default directory
DEFAULT_GAME_RECORD_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game_records'))
if not os.path.exists(DEFAULT_GAME_RECORD_DIRECTORY):
    os.makedirs(DEFAULT_GAME_RECORD_DIRECTORY)

def get_game_record_path(filename):
    return os.path.join(DEFAULT_GAME_RECORD_DIRECTORY, filename)

def analyze(game_records:list[caro.GameRecord]):

    statistics, matches = tournament.analyze_game_record(game_records)

    # sort by score
    statistics.sort(key=lambda x: x['win'] + x['draw']*0.5, reverse=True)

    # rank board
    print("RANK BOARD(by score)")
    print("-" * 102)
    print(f"|{'Name':<50}{'Score':<10}{'win/draw/loss':<20}{'avg thinking time':<20}|")
    print("-" * 102)
    for s in statistics:
        _name = s['name']
        _score = s['win'] + s['draw']*0.5
        _win_draw_loss = f'{s['win']}/{s['draw']}/{s['loss']}'
        _avg_t = s['avg thinking time']
        print(f"|{_name:<50}{_score:<10}{_win_draw_loss:<20}{_avg_t:<20.06f}|")
    print("-" * 102)
    print('\n\n')

    # show matches
    while True:
        agent_name = input("Enter an agent name to see its matchups (or 'exit' to quit): ")
        if agent_name == 'exit':
            break
        if agent_name not in matches:
            print(f"Agent '{agent_name}' not found. Please try again.")
            continue
        print(f"\nHead-to-head results for agent '{agent_name}' against other agents:")
        print("-" * 92)
        print(f"|{'Opponent':<50}{'win/draw/loss':<20}{'Average moves/game':<20}|")
        print("-" * 92)
        for opponent, result in matches[agent_name].items():
            _wdl = f'{result['win']}/{result['draw']}/{result['loss']}'
            _avg_m = result['avg moves per game']
            print(f"|{opponent:<50}{_wdl:<20}{_avg_m:<20.02f}|")
        print("-" * 92)

def menu():

    print(f'''
        1. Play vs AI
           - Play a game against an AI agent using a graphical interface (built with Pygame).

        2. Run Tournament
           - Let a list of AI agents play a round-robin tournament.
           - Game records will be saved to the default directory: '{DEFAULT_GAME_RECORD_DIRECTORY}'.
           - Summary results will be printed to the terminal.

        3. Analyze Game Records
            - Load and analyze tournament results from game records saved in a file.
              (File selected from the default directory: '{DEFAULT_GAME_RECORD_DIRECTORY}')
            - Statistics will be printed to the terminal.
            
        4. Exit
    ''')
    while True:
        try:
            c = int(input(">> Your choice: "))
            if 1 <= c <= 4:
                return c
            else:
                print("Invalid choice! Please enter 1, 2, 3 or 4.")
        except ValueError:
            print("Invalid input! Please enter a number (1, 2, 3 or 4).")


if __name__ == '__main__':
    '''
    -------------------------
            AGENTS LIST
    -------------------------
    '''
    agents = []
    depth_range = [1, 2]
    search_radius_range = [1, 2]
    random_move_range = [0, 5]
    for d in depth_range:
        for sr in search_radius_range:
            for rm in random_move_range:
                agents.append(
                    MiniMax(
                        name=f"minimax_depth{d}_search_radius{sr}_random_move{rm}",
                        evaluate_function=evaluate,
                        depth=d, search_radius=sr,
                        random_move=rm)
                )

    '''
    -------------------------
        MAIN LOOP
    -------------------------
    '''
    while True:
        choice = menu()

        # play vs AI
        if choice == 1:
            app = App(font_name='Roboto-Regular.ttf', unit_size=15)
            app.play_n_game(
                player_x=caro.Human("You"),
                player_o=MiniMax(name="AI", evaluate_function=evaluate, depth=2, search_radius=1, random_move=10),
                number_of_game=2,
                first_turn=caro.X_PIECE
            )
            pygame.display.quit()

        # run tournament
        elif choice == 2:
            print("Number of games each agent will play with every other agent:")
            n = int(input(">> n = "))

            # make tournament
            game_records = tournament.tournament(agents, n)

            # save result to file
            path = get_game_record_path(f'tournament_{int(time.time())}.json')
            caro.GameRecord.save_to_file(path, game_records)
            print(f"Game record was saved to '{path}'")

            # analyze
            print('\n')
            analyze(game_records)

        # analyze
        elif choice == 3:
            print(f"A file will be selected from the default directory: '{DEFAULT_GAME_RECORD_DIRECTORY}'")
            file_name = input(">> File name: ")
            game_records = caro.GameRecord.load_from_file(get_game_record_path(file_name))

            print('\n\n')
            analyze(game_records)

        # exit
        elif choice == 4:
            break