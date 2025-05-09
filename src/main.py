import os
import time
from  datetime import datetime

import caro
from app import App
from minimax import MiniMax
from evaluate import evaluate

DEFAULT_GAME_RECORD_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game_records'))
if not os.path.exists(DEFAULT_GAME_RECORD_DIRECTORY):
    os.makedirs(DEFAULT_GAME_RECORD_DIRECTORY)

def get_game_record_path(filename):
    return os.path.join(DEFAULT_GAME_RECORD_DIRECTORY, filename)

if __name__ == '__main__':

    '''
    ------------------------------------
                INITIALIZE
    ------------------------------------
    '''
    # app
    app = App(font_name='Roboto-Regular.ttf', unit_size=15)

    # player: Human & AI
    human = caro.Human("Hu mần")
    ai = MiniMax(
        name="AI lỏ",
        depth=2,
        search_radius=1,
        random_move=10,
        evaluate_function=evaluate
    )

    '''
    ---------------------------------
                PLAY
    ---------------------------------
    '''
    number_of_game = 4

    # Human vs Human
    # game_record = app.play_n_game(
    #     player_x=human,
    #     player_o=human,
    #     number_of_game=number_of_game,
    #     first_turn=caro.X_PIECE,
    #     allow_take_back_move=True,
    #     review_game_after_finish=True
    # )

    # AI vs AI
    # game_record = app.play_n_game(
    #     player_x=ai,
    #     player_o=ai,
    #     number_of_game=number_of_game,
    #     first_turn=caro.X_PIECE,
    #     allow_take_back_move=True,
    #     review_game_after_finish=True
    # )

    # AI vs Human
    game_record = app.play_n_game(
        player_x=ai,
        player_o=human,
        number_of_game= number_of_game,
        first_turn=caro.X_PIECE,
        allow_take_back_move=True,
        review_game_after_finish=True
    )

    '''
    ---------------------------------
        SAVE GAME RECORD
    ---------------------------------
    '''
    file_name = f"game_record_{int(time.time())}.json"
    caro.GameRecord.save_to_file(get_game_record_path(file_name), game_record)
    print(f"Game record was saved to '{get_game_record_path(file_name)}'")