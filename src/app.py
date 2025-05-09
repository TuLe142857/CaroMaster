import os
import sys
import threading
import queue
import time
import pygame
import ui
import caro
from typing import Any, Callable

# color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (144, 238, 144)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
LIGHT_CYAN = (224, 255, 255)

# pygame mouse button value
MOUSE_LEFT = 1
MOUSE_MIDDLE = 2
MOUSE_RIGHT = 3
MOUSE_SCROLL_UP = 4
MOUSE_SCROLL_DOWN = 5

class AnimationBox(ui.Component):
    def __init__(
            self,
            rect: pygame.Rect | tuple[int, int, int, int] | list[int],
            gif_path: str,
            frame_delay:int=1,
            background:tuple[int, int, int]|tuple[int, int, int, int]|list[int] = (0, 255, 255),
            border_color: tuple[int, int, int] | tuple[int, int, int, int] | list[int] = (0, 0, 0),
            border_radius: int = 5,
            border_width:int = 0,
            outer_surface:pygame.Surface|None=None
    ):
        super().__init__(rect, outer_surface)
        self.avatar_gif = ui.Gif(
            rect=(10, 10, self.width - 20, self.height - 20),
            frames=ui.utils.gif_to_surfaces(gif_path),
            frame_delay=frame_delay,
            outer_surface=self.surface
        )
        self.background = background
        self.border_color = border_color
        self.border_width = border_width if border_width >= 0 else 0
        self.border_radius = border_radius if border_radius >= 0 else 0

    def set_gif(self, gif_path, frame_delay:int=1):
        self.avatar_gif = ui.Gif(
            rect=(10, 10, self.width - 20, self.height - 20),
            frames=ui.utils.gif_to_surfaces(gif_path),
            frame_delay=frame_delay,
            outer_surface=self.surface
        )

    def render(self):
        pygame.draw.rect(self.surface, self.background, (0, 0, self.width, self.height), border_radius=self.border_radius)
        if self.border_width > 0:
            pygame.draw.rect(self.surface, self.border_color, (0, 0, self.width, self.height),border_radius=self.border_radius, width=self.border_width)
        self.avatar_gif.render()
        super().render()

class App:
    def __init__(
            self,
            unit_size: int = 15,
            font_name: str | None = None,
            player_avatar:dict[str, Any]|None=None
    ):
        """

        :param unit_size: Base unit size used for calculating screen and component sizes.
        :param font_name: The name of the font to use, selected from the 'assets/fonts' directory. If None, a default system font will be used.
        """

        '''
        ---------------------------------------------------------------------------------------------
        |                           INITIALIZE APPLICATION                                          |
        ---------------------------------------------------------------------------------------------
        '''
        print("-" * 50)
        print("Initialize the application")
        pygame.init()

        '''
        -----------------------------------------
        |       UNIT SIZE, FONT, ..             |
        -----------------------------------------
        board cell size = 3u => 15 cell = 45 u
        component spacing = u
        button height = 3 - 5 u
        
        '''
        self.unit_size = unit_size
        self.font_name = font_name if font_name is None else App.get_asset_path("fonts", font_name)

        if player_avatar is None:
            player_avatar = {
                "normal": {
                    'gif':"cute.gif",
                    'frame delay': 8,
                    'background': (128, 128, 128, 128)
                },
                "thinking": {
                    'gif': "thinking.gif",
                    'frame delay': 8,
                    'background': (0, 255, 255)
                },
                "win": {
                    'gif': "laugh.gif",
                    'frame delay': 8,
                    'background': (255, 255, 0)
                },
                "loss": {
                    'gif': "cry.gif",
                    'frame delay': 8,
                    'background': (128, 128, 128, 100)
                },
            }
        self.player_avatar = player_avatar
        u = self.unit_size
        '''
        -----------------------------------------
        |       SCREEN WIDTH, HEIGHT            |
        -----------------------------------------
        '''
        display_infor = pygame.display.Info()
        self.screen_width = u + (caro.BOARD_SIZE * 3 * u) + u + (30 * u) + u
        self.screen_height = (caro.BOARD_SIZE * 3 * u) + (10*u)

        print(f"Display screen size: {display_infor.current_w} x {display_infor.current_h}")
        print("Unit Size:", self.unit_size)
        print(f"Application screen size: {self.screen_width} x {self.screen_height}")
        print("To change the application size, adjust the unit size.")
        if self.screen_width > display_infor.current_w or self.screen_height > display_infor.current_h:
            raise RuntimeError("Application screen size too large. Please reduce the unit size.")
        '''
        -----------------------------------------
        |    SCREEN, LOOP FLAG, FPS LIMIT, ...  |
        -----------------------------------------
        '''
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60

        pygame.display.set_caption("CARO MASTER")
        '''
        -----------------------------------------
        |           FONT, COMPONENT, ...         |
        -----------------------------------------
        '''

        self.FONT_3U = pygame.font.Font(self.font_name, 3 * u)
        self.FONT_2U = pygame.font.Font(self.font_name, 2 * u)

        self.board = ui.Board(
            x= u,
            y= 5*u,
            rows= caro.BOARD_SIZE,
            columns= caro.BOARD_SIZE,
            cell_size= 3*u,
            font=self.FONT_3U
        )

        self.fps_box = ui.TextBox(
            rect=ui.utils.generate_relative_rect(self.board.rect(), (10*u, 3*u), 'top', spacing=u),
            font=self.FONT_2U,
            border_radius=0
        )

        self.player_x_avatar = AnimationBox(
            rect=ui.utils.generate_relative_rect(self.board.rect(), (10*u, 10*u), 'right', spacing=u),
            gif_path=App.get_asset_path("gifs", self.player_avatar['normal']['gif']),
            background= self.player_avatar['normal']['background'],
            frame_delay=self.player_avatar['normal']['frame delay']
        )

        self.player_x_name_box = ui.TextBox(
            rect=ui.utils.generate_relative_rect(self.player_x_avatar.rect(), (10*u, 3*u), "bottom", spacing=u),
            font=self.FONT_2U,
            border_radius=0,
        )

        self.player_o_avatar = AnimationBox(
            rect=ui.utils.generate_relative_rect(self.player_x_avatar.rect(), (10 * u, 10 * u), 'right', spacing=10*u),
            gif_path=App.get_asset_path("gifs", self.player_avatar['normal']['gif']),
            background=self.player_avatar['normal']['background'],
            frame_delay=self.player_avatar['normal']['frame delay']
        )

        self.player_o_name_box = ui.TextBox(
            rect=ui.utils.generate_relative_rect(self.player_o_avatar.rect(), (10 * u, 3 * u), "bottom", spacing=u),
            font=self.FONT_2U,
            border_radius=0
        )

        self.score_x = ui.TextBox(
            rect=ui.utils.generate_relative_rect(self.player_x_avatar.rect(), (3 * u, 5 * u), "right", spacing=u),
            font=self.FONT_2U,
            border_radius=0
        )
        self.score_x.y += 3*u

        self.score_o = ui.TextBox(
            rect=ui.utils.generate_relative_rect(self.score_x.rect(), (3 * u, 5 * u), "right", spacing=2*u),
            font=self.FONT_2U,
            border_radius=0
        )

        self.message_box = ui.TextBox(
            rect=ui.utils.generate_relative_rect(self.player_x_name_box.rect(), (30 * u, 10 * u), "bottom", spacing=u),
            font=self.FONT_2U
        )

        prev_btn_ico = pygame.image.load(App.get_asset_path("images", "previous-button-icon.png"))
        next_btn_ico = pygame.image.load(App.get_asset_path("images", "next-button-icon.png"))
        self.prev_btn = ui.Button(
            rect=ui.utils.generate_relative_rect(self.message_box.rect(), (14*u, 3 * u), 'bottom', spacing=u),
            label=prev_btn_ico,
            font=self.FONT_2U
        )

        self.next_btn = ui.Button(
            rect=ui.utils.generate_relative_rect(self.prev_btn.rect(), (14 * u, 3 * u), 'right', spacing=2*u),
            label=next_btn_ico,
            font=self.FONT_2U
        )

        self.takeback_btn = ui.Button(
            rect=ui.utils.generate_relative_rect(self.prev_btn.rect(), (30 * u, 3 * u), 'bottom', spacing=u),
            label="takeback move",
            font=self.FONT_2U
        )

        self.continue_btn = ui.Button(
            rect=ui.utils.generate_relative_rect(self.takeback_btn.rect(), (30 * u, 3 * u), 'bottom', spacing=u),
            label="continue",
            font=self.FONT_2U
        )


        print("-" * 50, '\n')
        '''
        ---------------------------------------------------------------------------------------------
        |                           INITIALIZE APPLICATION COMPLETED                                |
        ---------------------------------------------------------------------------------------------
        '''

    @staticmethod
    def get_asset_path(*path):
        asset_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        return os.path.join(asset_directory, *path)

    def reset_components(self):
        """
        reset: board, player name, player avatar, score, message box to default
        :return:
        """
        self.board.clear()
        self.set_player_name("", "")
        self.set_score()
        self.set_message("")
        self.set_player_avatar('normal', 'normal')

    def set_player_name(self, player_x_name:str, player_o_name:str):
        self.player_x_name_box.set_text(f'{player_x_name}(X)')
        self.player_o_name_box.set_text(f'{player_o_name}(O)')

    def set_player_avatar(self, player_x_status:str, player_o_status:str):
        """
        :param player_x_status: normal, thinking, win, loss
        :param player_o_status: normal, thinking, win, loss
        """
        # player x
        self.player_x_avatar.background = self.player_avatar[player_x_status]['background']
        self.player_x_avatar.set_gif(
            App.get_asset_path("gifs", self.player_avatar[player_x_status]['gif']),
            self.player_avatar[player_x_status]['frame delay']
        )

        # player o
        self.player_o_avatar.background = self.player_avatar[player_o_status]['background']
        self.player_o_avatar.set_gif(
            App.get_asset_path("gifs", self.player_avatar[player_o_status]['gif']),
            self.player_avatar[player_o_status]['frame delay']
        )

    def set_score(self, x_score:int|float|None=None, o_score:int|float|None=None):
        """
        :param x_score: if None => set empty. Default: None
        :param o_score: if None => set empty. Default: None
        """
        self.score_x.set_text(str(x_score) if x_score is not None else "")
        self.score_o.set_text(str(o_score) if o_score is not None else "")

    def set_message(self, msg:str):
        """
        set message display in message box
        """
        self.message_box.set_text(msg)

    def draw_board(self,
                   state:caro.BoardState,
                   lastest_move:tuple[int, int]|None=None,
                   highlight_winning_sequence:bool=True
        ):
        """
        draw board: background = white; color = red, blue for x, o piece

        highlight lastest move with background = green (if lastest move != None)

        highlight winning sequence: background = YELLOW(`if highlight_winning_sequence` == True)
        """
        self.board.clear()
        for r in range(caro.BOARD_SIZE):
            for c in range(caro.BOARD_SIZE):
                self.board.put(
                    piece=state.get((r, c)),
                    position=(r, c),
                    color=RED if state.get((r, c)) == caro.X_PIECE else BLUE,
                    background=WHITE
                )

        # highlight last move
        if lastest_move is not None:
            self.board.put(
                piece=state.get(lastest_move),
                position=lastest_move,
                color=RED if state.get(lastest_move) == caro.X_PIECE else BLUE,
                background=GREEN
            )

        # highlight winning sequence
        if highlight_winning_sequence:
            for p in state.get_winning_sequence():
                self.board.put(
                    piece=state.get(p),
                    position=p,
                    color=RED if state.get(p) == caro.X_PIECE else BLUE,
                    background=YELLOW
                )

    def play_n_game(
            self,
            player_x:caro.Human|caro.AI,
            player_o:caro.Human|caro.AI,
            first_turn: str,
            number_of_game:int=1,
            review_game_after_finish: bool = True,
            allow_take_back_move: bool = True
    )->list[caro.GameRecord]:
        self.reset_components()
        game_records = []
        score = [0, 0]
        self.set_score(score[0], score[1])
        for i in range(number_of_game):
            # clear board & set message
            self.board.clear()
            self.set_message(f"Game {i + 1}/{number_of_game}")

            # append record
            record = self.play(
                player_x=player_x,
                player_o=player_o,
                first_turn=first_turn,
                review_game_after_finish=False,
                allow_take_back_move=allow_take_back_move
            )
            game_records.append(record)

            # update score
            result = record.result()
            if result == caro.X_WIN:
                score[0] += 1
            elif result == caro.O_WIN:
                score[1] += 1
            elif result == caro.DRAW:
                score[0] += 0.5
                score[1] += 0.5
            self.set_score(score[0], score[1])

            # review game
            if review_game_after_finish:
                self.review_game(record)

            # change first turn after each game
            first_turn = caro.X_PIECE if first_turn == caro.O_PIECE else caro.O_PIECE
        # end for loop

        print(f'{player_x.name} vs {player_o.name} score:{score}')
        return game_records

    def play(self,
            player_x:caro.Human|caro.AI,
            player_o:caro.Human|caro.AI,
            first_turn: str,
            review_game_after_finish: bool = True,
            allow_take_back_move: bool= True
        )-> caro.GameRecord:
        if not(isinstance(player_x, (caro.Human, caro.AI)) or isinstance(player_o, (caro.Human, caro.AI))):
            print(f"player x is instance of {type(player_x)}")
            print(f"player o is instance of {type(player_o)}")
            raise RuntimeError("Player must be caro.Human or caro.AI")
        if allow_take_back_move and not(isinstance(player_x, caro.Human) or isinstance(player_o, caro.Human)):
            allow_take_back_move = False

        self.set_player_name(player_x.name, player_o.name)

        # state, game record, player, ...
        board_state = caro.BoardState()
        game_record = caro.GameRecord(player_x_name=player_x.name, player_o_name=player_o.name, first_turn=first_turn)
        player = {caro.X_PIECE: player_x, caro.O_PIECE: player_o}
        current_turn = first_turn
        if current_turn == caro.X_PIECE:
            self.set_player_avatar('thinking', 'normal')
        else:
            self.set_player_avatar('normal', 'thinking')

        # function to call in thread to let AI decide move
        ai_calc_result = queue.Queue()
        ai_is_thinking = False
        def let_ai_decide_move(state:caro.BoardState, ai:caro.AI, piece:str):
            m = ai.decide_move(state, piece)
            ai_calc_result.put(m)

        # function to make move
        def make_move(move:tuple[int, int]):
            # update value
            nonlocal current_turn
            game_record.add_move(move)
            board_state.put(current_turn, move)
            current_turn = caro.X_PIECE if current_turn == caro.O_PIECE else caro.O_PIECE

            # update component
            if current_turn == caro.X_PIECE:
                self.set_player_avatar('thinking', 'normal')
            else:
                self.set_player_avatar('normal', 'thinking')
            self.draw_board(board_state, game_record.moves[-1])

            # check game status
            status = board_state.status()
            if status != caro.NOT_FINISH:
                self.running = False

        # function to take back move
        def takeback():
            if len(game_record.moves) < 2:
                return
            board_state.put(caro.EMPTY_CELL, game_record.moves[-1])
            game_record.remove_last_move()

            board_state.put(caro.EMPTY_CELL, game_record.moves[-1])
            game_record.remove_last_move()

            if len(game_record.moves) != 0:
                self.draw_board(board_state, game_record.moves[-1])
            else:
                self.draw_board(board_state)


        '''
        ---------------------------------------------------
                            GAME LOOP
        ---------------------------------------------------
        '''

        components = [
            self.board,
            self.player_x_avatar,
            self.player_o_avatar,
            self.player_x_name_box,
            self.player_o_name_box,
            self.score_x,
            self.score_o,
            self.message_box
        ]

        if allow_take_back_move:
            components.append(self.takeback_btn)
        self.running = True

        while self.running:
            '''
            ---------------------------------------------
                        AI DECIDE MOVE
            ---------------------------------------------
            '''
            if isinstance(player[current_turn], caro.AI):
                # not create thread => create thread
                if not ai_is_thinking:
                    # calculating in new thread
                    ai_is_thinking = True
                    # Use board.clone() to ensure AI works on a copy and doesn't modify the real game state
                    t = threading.Thread(target=let_ai_decide_move, args=[board_state.clone(), player[current_turn], current_turn])
                    t.start()
                # thread completed => update
                elif not ai_calc_result.empty():
                    ai_is_thinking = False
                    make_move(ai_calc_result.get())
            '''
            ------------------------------------------------
                HANDLE EVENT: human move, take back, ...
            ------------------------------------------------
            '''
            for event in pygame.event.get():

                for c in components:
                    c.handle_event(event)

                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit(0)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT:
                    pos = pygame.mouse.get_pos()
                    # human make move
                    if self.board.contain_coordinate(pos) and isinstance(player[current_turn], caro.Human):
                        if board_state.get(self.board.cell_detect(pos)) == caro.EMPTY_CELL:
                            make_move(self.board.cell_detect(pos))
                    # human takeback move
                    if allow_take_back_move and self.takeback_btn.contain_coordinate(pos) and isinstance(player[current_turn], caro.Human):
                        takeback()
            '''
            -------------------------------------------------
                                RENDER
            -------------------------------------------------
            '''
            self.screen.fill(WHITE)
            for c in components:
                c.render()
            pygame.display.update()
            self.clock.tick(self.fps)
        # end game loop

        if review_game_after_finish and len(game_record.moves) != 0:
            self.review_game(game_record)
        return game_record


    def review_game(self, game_record:caro.GameRecord):
        if len(game_record.moves) == 0:
            raise RuntimeError("Game record contains no moves!")

        # turn on key repeat mode
        pygame.key.set_repeat(500, 100)

        # reset component
        self.set_player_name(game_record.player_x, game_record.player_o)
        game_result = game_record.result()
        if game_result == caro.DRAW:
            self.set_message("Game review mode\nDRAW")

        elif game_result == caro.X_WIN:
            self.set_message("Game review mode\nX WIN")
            self.set_player_avatar('win', 'loss')
        elif game_result == caro.O_WIN:
            self.set_message("Game review mode\nO WIN")
            self.set_player_avatar('loss', 'win')
        elif game_result == caro.NOT_FINISH:
            self.set_message("Game review mode\nGame not finish")

        move_id = len(game_record.moves) - 1
        self.draw_board(caro.BoardState.from_moves(game_record.moves[:move_id + 1:], game_record.first_turn), lastest_move=game_record.moves[move_id])

        components = [
            self.board,
            self.player_x_avatar,
            self.player_o_avatar,
            self.player_x_name_box,
            self.player_o_name_box,
            self.score_x,
            self.score_o,
            self.message_box,
            self.prev_btn,
            self.next_btn,
            self.continue_btn
        ]
        self.running = True
        while self.running:
            '''
            -------------------------
                HANDLE EVENT
            -------------------------
            '''
            for event in pygame.event.get():
                for c in components:
                    c.handle_event(event)
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT:
                    pos = pygame.mouse.get_pos()
                    if self.prev_btn.contain_coordinate(pos):
                        if move_id > 0:
                            move_id -= 1
                            self.draw_board(caro.BoardState.from_moves(game_record.moves[:move_id + 1:], game_record.first_turn), lastest_move=game_record.moves[move_id])
                    elif self.next_btn.contain_coordinate(pos):
                        if move_id != len(game_record.moves)-1:
                            move_id += 1
                            self.draw_board(caro.BoardState.from_moves(game_record.moves[:move_id + 1:], game_record.first_turn), lastest_move=game_record.moves[move_id])
                    elif self.continue_btn.contain_coordinate(pos):
                        self.running = False
                        break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if move_id > 0:
                            move_id -= 1
                            self.draw_board(caro.BoardState.from_moves(game_record.moves[:move_id + 1:], game_record.first_turn), lastest_move=game_record.moves[move_id])
                    elif event.key == pygame.K_RIGHT:
                        if move_id != len(game_record.moves) - 1:
                            move_id += 1
                            self.draw_board(caro.BoardState.from_moves(game_record.moves[:move_id + 1:], game_record.first_turn), lastest_move=game_record.moves[move_id])
            '''
            ---------------------------
                        RENDER
            ---------------------------
            '''
            self.screen.fill(WHITE)
            for c in components:
                c.render()
            pygame.display.update()
            self.clock.tick(self.fps)

        # end game loop
        # reset key repeat mode
        pygame.key.set_repeat()

    def testing_mode(self, function:Callable[[caro.BoardState], Any], message:str="Testing mode"):
        """
        Launch an interactive testing mode for manual board manipulation and function testing.

        This mode is useful for debugging or visualizing how a function behaves on a manually modified board.
        Users can place pieces (X, O, or empty) on the board and click a button to invoke the given function.

        Example:
            if __name__ == '__main__':
                app = App(font_name="Roboto-Regular.ttf")
                pygame.display.set_caption("TESTING MODE")

                def callme(state):
                    print("Called")
                    print(state)

                app.testing_mode(function=callme, message="Hello world")

        :param function: A callable that will be executed with the current board state
                         when the "Call function" button is clicked.
        :param message: A message to display in the message box during testing.
        """

        pieces = [caro.X_PIECE, caro.O_PIECE, caro.EMPTY_CELL]
        piece_id = 0
        state = caro.BoardState()

        # components
        self.reset_components()
        self.set_message(message)
        change_piece_btn = ui.Button(
            rect=ui.utils.generate_relative_rect(self.message_box.rect(), (20*self.unit_size, 3*self.unit_size), 'bottom'),
            label=f"Piece: '{pieces[piece_id]}'",
            font=self.FONT_2U
        )

        call_func_btn = ui.Button(
            rect=ui.utils.generate_relative_rect(change_piece_btn.rect(), (20 * self.unit_size, 3 * self.unit_size),'bottom'),
            label="Call function",
            font=self.FONT_2U
        )

        components = [
            self.fps_box,
            self.board,
            self.player_x_avatar,
            self.message_box,
            change_piece_btn,
            call_func_btn
        ]
        self.running = True
        # calculating fps
        t = time.time()
        count = 0
        while self.running:
            # fps
            count += 1
            if time.time() - t >= 1.0:
                avg_fps = count / (time.time() - t)
                t = time.time()
                count = 0
                self.fps_box.set_text(f'{avg_fps:.02f} fps')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_LEFT:
                    pos = pygame.mouse.get_pos()
                    if self.board.contain_coordinate(pos):
                        position = self.board.cell_detect(pos)
                        state.put(pieces[piece_id], position)
                        self.draw_board(state, highlight_winning_sequence=False)
                    if change_piece_btn.contain_coordinate(pos):
                        piece_id = (piece_id+1)%len(pieces)
                        change_piece_btn.label = f"Piece: '{pieces[piece_id]}'"
                        change_piece_btn.update()
                    if call_func_btn.contain_coordinate(pos):
                        function(state)
                for c in components:
                    c.handle_event(event)

            self.screen.fill((255, 255, 255))
            for c in components:
                c.render()
            pygame.display.update()
            self.clock.tick(self.fps)
        self.reset_components()

    def show_all_components(self):
        """
        use for testing render component
        """
        self.set_player_name("player", "player")
        self.set_player_avatar('win', 'loss')
        self.set_message("A vs B\nGame 5/5\nA win")
        self.set_score(3.5, 1.5)

        components = [
            self.fps_box,
            self.board,
            self.player_x_avatar,
            self.player_o_avatar,
            self.player_x_name_box,
            self.player_o_name_box,
            self.score_x,
            self.score_o,
            self.message_box,
            self.prev_btn,
            self.next_btn,
            self.takeback_btn,
            self.continue_btn
        ]

        self.running = True

        # calculating fps
        t = time.time()
        count = 0
        while self.running:
            # fps
            count += 1
            if time.time() - t >= 1.0:
                avg_fps = count / (time.time() - t)
                t = time.time()
                count = 0
                self.fps_box.set_text(f'{avg_fps:.02f} fps')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit(0)

                for c in components:
                    c.handle_event(event)

            self.screen.fill((255, 255, 255))
            for c in components:
                c.render()
            pygame.display.update()

            self.clock.tick(self.fps)

if __name__ == '__main__':
    app = App(font_name="Roboto-Regular.ttf")
    pygame.display.set_caption("TESTING MODE")
    # app.show_all_components()

    def callme(state):
        print("Called")
        print(state)
    app.testing_mode(function=callme)