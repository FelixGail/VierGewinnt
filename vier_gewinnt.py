from tkinter import Tk, Frame, Label, Canvas
from enum import Enum


# Change Color Codes to edit Board GUI
class Color(Enum):
    RED_OUTER = '#FF0000'
    RED_INNER = '#8A0808'
    YELLOW_OUTER = '#FACC2E'
    YELLOW_INNER = '#DBA901'
    WHITE = '#FFFFFF'
    BOARD = '#2E2EFE'
    OUTLINE = '#1C1C1C'
    HIGHLIGHT = '#04B404'
    RED_HOVERED_OUTER = '#610B0B'
    RED_HOVERED_INNER = '#3B0B0B'
    YELLOW_HOVERED_OUTER = '#886A08'
    YELLOW_HOVERED_INNER = '#5F4C0B'


class ClickAble(Frame):
    def __init__(self, on_enter=None, on_leave=None, on_click=None, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.on_enter_call = on_enter
        self.on_leave_call = on_leave
        self.on_click_call = on_click
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def __del__(self):
        self.unbind('<Enter')
        self.unbind('Leave')

    def on_enter(self, event):
        if hasattr(self.on_click_call, '__call__'):
            self.bind('<Button-1>', self.on_click_call)
        if hasattr(self.on_enter_call, '__call__'):
            self.on_enter_call(event)

    def on_leave(self, event):
        if hasattr(self.on_click_call, '__call__'):
            self.unbind('<Button-1>')
        if hasattr(self.on_leave_call, '__call__'):
            self.on_leave_call(event)


class Player(object):
    def __init__(self, color):
        self.points = 0
        self.next_player = None
        if color == 'red':
            self.color_outer = Color.RED_OUTER.value
            self.color_inner = Color.RED_INNER.value
            self.color_hovered_outer = Color.RED_HOVERED_OUTER.value
            self.color_hovered_inner = Color.RED_HOVERED_INNER.value
        elif color == 'yellow':
            self.color_outer = Color.YELLOW_OUTER.value
            self.color_inner = Color.YELLOW_INNER.value
            self.color_hovered_outer = Color.YELLOW_HOVERED_OUTER.value
            self.color_hovered_inner = Color.YELLOW_HOVERED_INNER.value
        else:
            raise ValueError('Playercolor "{}" not recognized'.format(color))

    def add_point(self):
        self.points += 1


class Game(object):
    def __init__(self, columns=7, rows=6, field_radius=50, field_space=10):
        self.columns = columns
        self.rows = rows
        self.board = None
        self.canvas = None
        self.hovered = None
        self.player1 = Player('red')
        self.player2 = Player('yellow')
        self.player1.next_player = self.player2
        self.player2.next_player = self.player1
        self.active_player = self.player1
        self.field_radius = field_radius
        self.field_space = field_space
        tk = Tk()
        tk.geometry('1180x770')
        tk.title('4 Gewinnt')
        self.initiate_board(tk, 200, 50)
        self.bind_events()
        tk.mainloop()

    def initiate_board(self, master, x, y):
        width = (self.columns + 1) * self.field_space + 2 * self.columns * self.field_radius
        height = (self.rows + 1) * self.field_space + 2 * self.rows * self.field_radius
        self.create_canvas(master, x, y, width, height)
        self.board = []
        start = self.field_space + self.field_radius
        add = 2 * self.field_radius + self.field_space
        x_pos = start
        for column in range(self.columns):
            y_pos = height - start
            inner = []
            for row in range(self.rows):
                field_object = Field(x_pos, y_pos, self.field_radius, self.canvas, column, row)
                field_object.create_gui_element()
                inner.append(field_object)
                y_pos -= add
            self.board.append(inner)
            x_pos += add

    def create_canvas(self, master, x, y, width, height):
        self.canvas = Canvas(master=master, bg=Color.BOARD.value)
        self.canvas.place(x=x, y=y, width=width, height=height)

    def bind_events(self):
        self.canvas.bind('<Enter>', self.on_enter)
        self.canvas.bind('<Leave>', self.on_leave)

    def unbind_event(self):
        self.canvas.unbind('<Enter>')
        self.canvas.unbind('<Leave>')

    def on_enter(self, event):
        self.canvas.bind('<Motion>', self.on_motion)
        self.canvas.bind('<Button-1>', self.on_click)

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
            if not self.is_end():
                self.active_player = self.active_player.next_player
            self.hovered = None

    def on_leave(self, event):
        if self.hovered is not None:
            self.hovered.reset()
            self.hovered = None
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<Button-1>')

    def is_end(self):
        winner = None
        claimed = self.hovered
        claimed_row = claimed.row
        claimed_column = claimed.column
        # TODO: Win Detection
        for column in self.board:
            last_item = column[-1]
            if last_item.status == FieldStatus.FREE:
                return False
        self.end_game(winner)

    def end_game(self, winner):
        self.reset_board()

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


class FieldStatus(Enum):
    FREE = 0
    OCCUPIED = 1


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

Canvas.create_circle = _create_circle

if __name__ == '__main__':
    game = Game()
