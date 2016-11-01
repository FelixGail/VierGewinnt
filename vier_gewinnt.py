from tkinter import Tk, Canvas, Entry, Label, Button
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
    FONT_COLOR_WINNER = '#151515'
    FONT_COLOR_WINS = '#1C1C1C'


# player names
class PlayerType(Enum):
    PLAYER_1 = 'RED'
    PLAYER_2 = 'YELLOW'


# possible field states
class FieldStatus(Enum):
    FREE = 0
    OCCUPIED = 1


# player object will determine which colors to use and keeps track of won games
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


# Main class
class Game(object):
    def __init__(self, columns=7, rows=6, field_radius=50, field_space=10, win_condition=4):
        self.columns = columns
        self.rows = rows
        self.win_condition = win_condition
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
        self.window_width = (self.columns + 1) * self.field_space + 2 * self.columns * self.field_radius
        self.window_height = (self.rows + 1) * self.field_space + 2 * self.rows * self.field_radius
        tk = open_centered_window(self.window_width, self.window_height, '4 Gewinnt')
        self.initiate_board(tk)
        self.initiate_win_labels()
        self.bind_events()
        tk.mainloop()

    # create game fields and add them to the board array
    def initiate_board(self, master):
        self.create_canvas(master)
        self.board = []
        start = self.field_space + self.field_radius
        add = 2 * self.field_radius + self.field_space
        x_pos = start
        for column in range(self.columns):
            y_pos = self.window_height - start
            inner = []
            for row in range(self.rows):
                field_object = Field(x_pos, y_pos, self.field_radius, self.canvas, column, row)
                field_object.create_gui_element()
                inner.append(field_object)
                y_pos -= add
            self.board.append(inner)
            x_pos += add

    # create the end game message labels
    def initiate_win_labels(self):
        half_width = int(self.window_width / 2)
        one_quarter_height = int(self.window_height / 6)
        self.canvas_text_winner_id = self.canvas.create_text(half_width, one_quarter_height*2,
                                                             font='Helvetica 42 bold',
                                                             fill=Color.FONT_COLOR_WINNER.value)
        self.canvas_text_wins_id = self.canvas.create_text(half_width, one_quarter_height*3,
                                                           font='Helvetica 35 bold', fill=Color.FONT_COLOR_WINS.value)

    # create a canvas to draw the field objects in
    def create_canvas(self, master):
        self.canvas = Canvas(master=master, bg=Color.BOARD.value, highlightthickness=0)
        self.canvas.place(x=0, y=0, width=self.window_width, height=self.window_height)

    # bind the default events
    def bind_events(self):
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Motion>', self.on_motion)

    # Remove the default binds. Mouse click will reset the game now
    def after_win_events(self):
        self.canvas.bind('<Button-1>', self.reset_game)
        self.canvas.unbind('<Motion>')

    # remove the end game message, reset the board and bind the default events
    def reset_game(self, event):
        self.canvas.itemconfigure(self.canvas_text_wins_id, text='')
        self.canvas.itemconfigure(self.canvas_text_winner_id, text='')
        self.reset_board()
        self.bind_events()

    # What to do on mouse motion
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

    # What to do with a mouse click event
    def on_click(self, event):
        if self.hovered is not None:
            self.hovered.claim(self.active_player)
            self.is_end()
            self.active_player = self.active_player.next_player
            self.hovered = None

    # determine if the game ended with the recently claimed field
    def is_end(self):
        winner = None
        claimed = self.hovered

        directions = [[0, 1], [1, 0], [1, 1], [-1, 1]]
        for direction in directions:
            streak = self.get_occupied_streak(claimed, direction[0], direction[1])
            if len(streak) >= self.win_condition:
                for field in streak:
                    field.outline()
                self.end_game(self.active_player)
                return True

        for column in self.board: #detect if board is full without anyone winning
            last_item = column[-1]
            if last_item.status == FieldStatus.FREE:
                return False
        self.end_game(winner)
        return True

    # determine how many connected fields can be found in the selected direction.
    # example: (1,0) will test along the x axis
    def get_occupied_streak(self, field, add_x, add_y):
        streak_active = True
        direction = 1
        x = field.column
        y = field.row
        streak = [field]
        while streak_active:
            x += (add_x * direction)
            y += (add_y * direction)
            if 0 <= x < self.columns and 0 <= y < self.rows and self.board[x][y].status == FieldStatus.OCCUPIED and self.board[x][y].claimed_by == field.claimed_by:
                streak.append(self.board[x][y])
            else:
                if direction > 0:
                    direction = -1
                    x = field.column
                    y = field.row
                else:
                    streak_active = False
        return streak

    # display the game over message
    def end_game(self, winner):
        self.after_win_events()
        if winner is not None:
            text = '{} WINS'.format(winner.player_type.value)
            winner.add_point()
            self.canvas.itemconfigure(self.canvas_text_wins_id, text='Wins: {}'.format(winner.points))
        else:
            text = 'NOBODY WINS'
        self.canvas.itemconfigure(self.canvas_text_winner_id, text=text)

    # reset every field on the board
    def reset_board(self):
        for column in self.board:
            for field in column:
                field.reset()

    # reset the outline of every field (Note: not used in current version)
    def reset_soft(self):
        for column in self.board:
            for field in column:
                field.reset_outline()


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

    # create the gui element
    def create_gui_element(self):
        self.outer_circle_id = self.canvas.create_circle(self.x_pos, self.y_pos, self.radius, fill=Color.WHITE.value,
                                                         outline=Color.OUTLINE.value, width=2)
        self.inner_circle_id = self.canvas.create_circle(self.x_pos, self.y_pos, self.radius - 10,
                                                         fill=Color.WHITE.value)

    # claim the field
    def claim(self, player: Player):
        self.canvas.itemconfigure(self.outer_circle_id, fill=player.color_outer)
        self.canvas.itemconfigure(self.inner_circle_id, fill=player.color_inner)
        self.status = FieldStatus.OCCUPIED
        self.claimed_by = player

    # set the field to hover
    def hover(self, player: Player):
        self.canvas.itemconfigure(self.outer_circle_id, fill=player.color_hovered_outer)
        self.canvas.itemconfigure(self.inner_circle_id, fill=player.color_hovered_inner)

    # completely reset the field
    def reset(self):
        self.canvas.itemconfigure(self.outer_circle_id, fill=Color.WHITE.value, outline=Color.OUTLINE.value, width=2)
        self.canvas.itemconfigure(self.inner_circle_id, fill=Color.WHITE.value)
        self.status = FieldStatus.FREE
        self.claimed_by = None

    # set highlighting
    def outline(self):
        self.canvas.itemconfigure(self.outer_circle_id, outline=Color.HIGHLIGHT.value, width=5)

    # remove highlighting
    def reset_outline(self):
        self.canvas.itemconfigure(self.outer_circle_id, outline=Color.OUTLINE.value, width=2)


# Allows to edit the game settings
class GameSettings(object):
    def __init__(self):
        self.columns = 7
        self.rows = 6
        self.field_radius = 50
        self.space = 10
        self.win_condition = 4
        self.win_condition_entry = None
        self.columns_entry = None
        self.rows_entry = None
        self.field_radius_entry = None
        self.space_entry = None
        self.tk = None
        self.height = 30

    # Create the settings window with its widgets
    def create_window(self):
        self.tk = open_centered_window(310, 210, 'Settings')

        self.create_label(0, 'Columns:')
        self.columns_entry = self.create_entry(0, self.columns)

        self.create_label(1, 'Columns')
        self.rows_entry = self.create_entry(1, self.rows)

        self.create_label(2, 'Field Radius:')
        self.field_radius_entry = self.create_entry(2, self.field_radius)

        self.create_label(3, 'Space:')
        self.space_entry = self.create_entry(3, self.space)

        self.create_label(4, 'Win Condition:')
        self.win_condition_entry = self.create_entry(4, self.win_condition)

        button = Button(master=self.tk, text='Start', command=self.button_click)
        self.place(button, 80, 170)

        self.tk.mainloop()

    # Button Command
    def button_click(self):
        try:
            self.columns = int(self.columns_entry.get())
            self.rows = int(self.rows_entry.get())
            self.field_radius = int(self.field_radius_entry.get())
            self.space = int(self.space_entry.get())
            self.win_condition = int(self.win_condition_entry.get())
        except ValueError:
            raise
        finally:
            self.tk.destroy()

    # Place any Tkinter widget at the selected coordinates
    def place(self, widget, x, y):
        widget.place(x=x, y=y, width=140, height=self.height)

    # Create an entry field on the given position (0 or higher)
    def create_entry(self, pos, text):
        entry = Entry(master=self.tk)
        entry.insert(0, str(text))
        self.place(entry, 160, pos*self.height+10)
        return entry

    # Create a label on the given position (0 or higher)
    def create_label(self, pos, text):
        label = Label(master=self.tk, text=str(text))
        self.place(label, 10, pos*self.height+10)
        return label


# Add a create circle method to Tkinters Canvas
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)
Canvas.create_circle = _create_circle


# Creates a Tkinter window and center it on the screen. Return the created window
def open_centered_window(width, height, title):
    tk = Tk()

    screen_width = tk.winfo_screenwidth()
    screen_height = tk.winfo_screenheight()

    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)

    tk.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    tk.title(title)
    return tk


# Start the Settings window and wait for input - start game with default values if ValueErrors occur.
settings = GameSettings()
try:
    settings.create_window()
    Game(columns=settings.columns, rows=settings.rows, field_radius=settings.field_radius,
         field_space=settings.space, win_condition=settings.win_condition)
except ValueError:
    Game()

