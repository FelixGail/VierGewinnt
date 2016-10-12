from tkinter import Tk, Frame, Label, Canvas
from enum import Enum


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


class Game(object):
    def __init__(self):
        tk = Tk()
        tk.geometry('1180x770')
        tk.title('4 Gewinnt')
        self.board = Board()
        self.board.initiate_board(tk, 200, 50)
        tk.mainloop()


class Player(object):
    def __init__(self, next_player, color_outer, color_inner):
        self.points = 0
        self.next_player = next_player
        self.color_outer = color_outer
        self.color_inner = color_inner

    def add_point(self):
        self.points += 1


class Board(object):
    def __init__(self, size_width=7, size_height=6):
        self.size_width = size_width
        self.size_height = size_height
        self.board = None
        self.canvas = None

    def initiate_board(self, master, x, y, field_radius=50, space=10):
        self.create_canvas(master, x, y, field_radius, space)
        self.board = []
        start = space+field_radius
        add = 2*field_radius+space
        y_pos = start
        for y in range(self.size_height):
            x_pos = start
            inner = []
            for x in range(self.size_width):
                field_object = Field(x_pos, y_pos, field_radius)
                field_object.create_gui_element(self.canvas)
                inner.append(field_object)
                x_pos += add
            self.board.append(inner)
            y_pos += add

    def create_canvas(self, master, x, y, field_radius, space):
        self.canvas = Canvas(master=master, bg=Color.BOARD.value)
        self.canvas.place(x=x, y=y, width=(self.size_width+1)*space+2*self.size_width*field_radius,
                          height=(self.size_height+1)*space+2*self.size_height*field_radius)


class Field(object):
    def __init__(self, x_pos, y_pos, radius):
        self.status = FieldStatus.FREE
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.outer_circle = None
        self.inner_circle = None

    def create_gui_element(self, canvas: Canvas):
        self.outer_circle = canvas.create_circle(self.x_pos, self.y_pos, self.radius, fill=Color.WHITE.value,
                                                 outline=Color.OUTLINE.value, width=2)
        self.inner_circle = canvas.create_circle(self.x_pos, self.y_pos, self.radius-10, fill=Color.WHITE.value)

    def occupy(self, player: Player):
        self.outer_circle.config(fill=player.color_outer)
        self.inner_circle.config(fill=player.color_inner)
        self.status = FieldStatus.OCCUPIED

    def hover(self):
        self.outer_circle.config(fill=Color.LIGHT_GREY.value)
        self.inner_circle.config(fill=Color.DARK_GREY.value)

    def reset(self):
        self.outer_circle.config(fill=Color.WHITE.value, outline=Color.OUTLINE.value, width=2)
        self.inner_circle.config(fill=Color.WHITE.value)
        self.status = FieldStatus.FREE

    def outline(self):
        self.outer_circle.config(outline=Color.HIGHLIGHT.value, width=5)


class FieldStatus(Enum):
    FREE = 0
    OCCUPIED = 1


class Color(Enum):
    RED_OUTER = '#FF0000'
    RED_INNER = '#8A0808'
    YELLOW_OUTER = '#FACC2E'
    YELLOW_INNER = '#DBA901'
    LIGHT_GREY = '#A4A4A4'
    DARK_GREY = '#6E6E6E'
    WHITE = '#FFFFFF'
    BOARD = '#2E2EFE'
    OUTLINE = '#1C1C1C'
    HIGHLIGHT = '#04B404'


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle


if __name__ == '__main__':
    game = Game()
