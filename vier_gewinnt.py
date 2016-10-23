from tkinter import Tk, Canvas
from enum import Enum


# Change Color Codes to edit Board GUI
class Color(Enum):
    PLAYER_1_OUTER = '#FF0000'
    PLAYER_1_INNER = '#8A0808'
    PLAYER_2_OUTER = '#FACC2E'
    PLAYER_2_INNER = '#DBA901'
    WHITE = '#FFFFFF'
    BOARD = '#2E2EFE'
    OUTLINE = '#1C1C1C'
    HIGHLIGHT = '#04B404'
    PLAYER_1_HOVERED_OUTER = '#610B0B'
    PLAYER_1_HOVERED_INNER = '#3B0B0B'
    PLAYER_2_HOVERED_OUTER = '#886A08'
    PLAYER_2_HOVERED_INNER = '#5F4C0B'
    FONT_COLOR_WINNER = '#B40404'
    FONT_COLOR_WINS = '#FFFFFF'


class PlayerType(Enum):
    PLAYER_1 = 'RED'
    PLAYER_2 = 'YELLOW'


class FieldStatus(Enum):
    FREE = 0
    OCCUPIED = 1


class Player(object):
    def __init__(self, player: PlayerType):
        self.points = 0
        self.next_player = None
        self.player_type = player
        if player == PlayerType.PLAYER_1:
            self.color_outer = Color.PLAYER_1_OUTER.value
            self.color_inner = Color.PLAYER_1_INNER.value
            self.color_hovered_outer = Color.PLAYER_1_HOVERED_OUTER.value
            self.color_hovered_inner = Color.PLAYER_1_HOVERED_INNER.value
        elif player == PlayerType.PLAYER_2:
            self.color_outer = Color.PLAYER_2_OUTER.value
            self.color_inner = Color.PLAYER_2_INNER.value
            self.color_hovered_outer = Color.PLAYER_2_HOVERED_OUTER.value
            self.color_hovered_inner = Color.PLAYER_2_HOVERED_INNER.value
        else:
            raise ValueError('PlayerType "{}" not recognized'.format(player))

    def add_point(self):
        self.points += 1


class Game(object):
    def __init__(self, columns=2, rows=2, field_radius=100, field_space=50):
        self.columns = columns
        self.rows = rows
        self.board = None
        self.canvas = None
        self.hovered = None
        self.canvas_text_winner_id = None
        self.canvas_text_wins_id = None
        self.player1 = Player(PlayerType.PLAYER_1)
        self.player2 = Player(PlayerType.PLAYER_2)
        self.player1.next_player = self.player2
        self.player2.next_player = self.player1
        self.active_player = self.player1
        self.field_radius = field_radius
        self.field_space = field_space
        self.canvas_width = (self.columns + 1) * self.field_space + 2 * self.columns * self.field_radius
        self.canvas_height = (self.rows + 1) * self.field_space + 2 * self.rows * self.field_radius
        tk = Tk()
        tk.geometry('{}x{}'.format(self.canvas_width, self.canvas_height))
        tk.title('4 Gewinnt')
        self.initiate_board(tk)
        self.initiate_win_labels()
        self.bind_events()
        tk.mainloop()

    def initiate_board(self, master):
        self.create_canvas(master)
        self.board = []
        start = self.field_space + self.field_radius
        add = 2 * self.field_radius + self.field_space
        x_pos = start
        for column in range(self.columns):
            y_pos = self.canvas_height - start
            inner = []
            for row in range(self.rows):
                field_object = Field(x_pos, y_pos, self.field_radius, self.canvas, column, row)
                field_object.create_gui_element()
                inner.append(field_object)
                y_pos -= add
            self.board.append(inner)
            x_pos += add

    def initiate_win_labels(self):
        half_width = int(self.canvas_width/2)
        one_quarter_height = int(self.canvas_height/6)
        self.canvas_text_winner_id = self.canvas.create_text(half_width, one_quarter_height*2,
                                                             font='Helvetica 20 bold',
                                                             fill=Color.FONT_COLOR_WINNER.value)
        self.canvas_text_wins_id = self.canvas.create_text(half_width, one_quarter_height*3,
                                                           font='Helvetica 16 bold', fill=Color.FONT_COLOR_WINS.value)

    def create_canvas(self, master):
        self.canvas = Canvas(master=master, bg=Color.BOARD.value, highlightthickness=0)
        self.canvas.place(x=0, y=0, width=self.canvas_width, height=self.canvas_height)

    def bind_events(self):
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Motion>', self.on_motion)

    def after_win_events(self):
        self.canvas.bind('<Button-1>', self.reset_binds)
        self.canvas.unbind('<Motion>')

    def reset_binds(self, event):
        self.canvas.itemconfigure(self.canvas_text_wins_id, text='')
        self.canvas.itemconfigure(self.canvas_text_winner_id, text='')
        self.reset_board()
        self.bind_events()

    def on_motion(self, event):
        current_percent_right = \
            float(event.x-self.field_space) / (self.columns * self.field_space + 2 * self.columns * self.field_radius)
        current_column = int(current_percent_right * self.columns)
        if self.hovered is not None:
            if self.hovered.column == current_column:
                return
            self.hovered.reset()
        for field in self.board[current_column]:
            if field.status == FieldStatus.FREE:
                field.hover(self.active_player)
                self.hovered = field
                return
        self.hovered = None

    def on_click(self, event):
        if self.hovered is not None:
            self.hovered.claim(self.active_player)
            self.is_end()
            self.active_player = self.active_player.next_player
            self.hovered = None

    def is_end(self):
        winner = None
        claimed = self.hovered

        directions = [[0, 1], [1, 0], [1, 1]]
        for direction in directions:
            streak = self.get_occupied_streak(claimed, direction[0], direction[1])

        for column in self.board: #detect if board is full without anyone winning
            last_item = column[-1]
            if last_item.status == FieldStatus.FREE:
                return
        self.end_game(winner)

    def get_occupied_streak(self, field, add_x, add_y):
        return []

    def end_game(self, winner):
        winner = self.player1
        self.after_win_events()
        if winner is not None:
            text = '{} WINS'.format(winner.player_type.value)
            winner.add_point()
            self.canvas.itemconfigure(self.canvas_text_wins_id, text='Wins: {}'.format(winner.points))
        else:
            text = 'NOBODY WINS'
        self.canvas.itemconfigure(self.canvas_text_winner_id, text=text)

    def reset_board(self):
        for column in self.board:
            for field in column:
                field.reset()


class Field(object):
    def __init__(self, x_pos, y_pos, radius, canvas: Canvas, column, row):
        self.status = FieldStatus.FREE
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.canvas = canvas
        self.column = column
        self.row = row
        self.outer_circle_id = None
        self.inner_circle_id = None
        self.claimed_by = None

    def create_gui_element(self):
        self.outer_circle_id = self.canvas.create_circle(self.x_pos, self.y_pos, self.radius, fill=Color.WHITE.value,
                                                         outline=Color.OUTLINE.value, width=2)
        self.inner_circle_id = self.canvas.create_circle(self.x_pos, self.y_pos, self.radius - 10,
                                                         fill=Color.WHITE.value)

    def claim(self, player: Player):
        self.canvas.itemconfigure(self.outer_circle_id, fill=player.color_outer)
        self.canvas.itemconfigure(self.inner_circle_id, fill=player.color_inner)
        self.status = FieldStatus.OCCUPIED
        self.claimed_by = player

    def hover(self, player: Player):
        self.canvas.itemconfigure(self.outer_circle_id, fill=player.color_hovered_outer)
        self.canvas.itemconfigure(self.inner_circle_id, fill=player.color_hovered_inner)

    def reset(self):
        self.canvas.itemconfigure(self.outer_circle_id, fill=Color.WHITE.value, outline=Color.OUTLINE.value, width=2)
        self.canvas.itemconfigure(self.inner_circle_id, fill=Color.WHITE.value)
        self.status = FieldStatus.FREE
        self.claimed_by = None

    def outline(self):
        self.canvas.itemconfigure(self.outer_circle_id, outline=Color.HIGHLIGHT.value, width=5)


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

Canvas.create_circle = _create_circle

if __name__ == '__main__':
    game = Game()
