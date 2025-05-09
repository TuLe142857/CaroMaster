import os
if not ('caro_module_intro' in os.environ):
    print(r'''
---------------------------------------------------------------------------------------
   _____          _____   ____          __  __           _____ _______ ______ _____  
  / ____|   /\   |  __ \ / __ \        |  \/  |   /\    / ____|__   __|  ____|  __ \ 
 | |       /  \  | |__) | |  | |       | \  / |  /  \  | (___    | |  | |__  | |__) |
 | |      / /\ \ |  _  /| |  | |       | |\/| | / /\ \  \___ \   | |  |  __| |  _  / 
 | |____ / ____ \| | \ \| |__| |       | |  | |/ ____ \ ____) |  | |  | |____| | \ \ 
  \_____/_/    \_\_|  \_\\____/        |_|  |_/_/    \_\_____/   |_|  |______|_|  \_\

                **************************************************
                * Welcome to our team project for the course     *
                * "Introduction to Artificial Intelligence".     *
                *                                                *
                * In this assignment, we have developed a simple *
                * AI-based Caro game that can play against a     *
                * human player.                                  *
                *                                                *
                *                                                *
                * Team Members:                                  *
                *     1. Trần Thái Sơn      -   N22DCCN170       *
                *     2. Triệu Việt Thành   -   N22DCCN177       *
                *     3. Lê Hoàng Thắng     -   N22DCCN178       *
                *     4. Lê Ngọc Tú         -   N22DCCN193       *
                **************************************************
---------------------------------------------------------------------------------------
''')
    os.environ['caro_module_intro'] = 'x'

from .constants import *
from .board_state import BoardState
from .game_record import GameRecord
from .player import Player, Human, AI