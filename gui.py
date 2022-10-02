from ipycanvas import Canvas, hold_canvas
import time

ROWS = 9
COLUMNS = 9
WIDTH = 540
HEIGHT = 540

SLEEP_TIME = 0.01
FONT_SIZE = 28
FONT_FAMILY = str(FONT_SIZE) + 'pt sans-serif'

class Board:
    """ Representation for the Sudoku board.
    """
    def __init__(self, board):
        self.rows = ROWS
        self.cols = COLUMNS
        self.width = WIDTH
        self.height = HEIGHT
        self.board = board
        self.cubes = [[Cube(self.board[i][j], i, j, self.width, self.height)
            for j in range(self.cols)] for i in range(self.rows)]
        self.model = None
        self.update_model()
        self.selected = None
        self.action_steps = 0

        self.canvas = Canvas(width=self.width,height=self.height+2*FONT_SIZE)
        self.canvas.layout.width = '50%'
        self.canvas.layout.height = 'auto'
        self.start = time.time()


    def update_model(self):
        self.model = [[self.cubes[i][j].value if self.cubes[i][j].value != 0 else self.cubes[i][j].temp
            for j in range(self.cols)] for i in range(self.rows)]

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.model[i][j] == 0:
                    return False
        return True

    def find_empty(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.model[i][j] == 0:
                    return (i, j)  # row, col
        return None


    def find_good_empty(self):
        (n,m) = (None,None)
        choices = self.rows
        for i in range(self.rows):
            for j in range(self.cols):
                if self.model[i][j] == 0:
                    c = self.choices(i,j)
                    if c == 1:
                        return (i, j)
                    elif c < choices:
                        (n, m) = (i, j)
                        choices = c
        if (n is None) and (m is None):
            return None 
        else:
            return (n, m)  # row, col


    def is_valid(self, num):
        if self.selected is None:
            return False
        i, j = self.selected
        
        # Check row
        for k in range(self.cols):
            if self.model[i][k] == num and j != k:
                return False

        # Check column
        for k in range(self.rows):
            if self.model[k][j] == num and i != k:
                return False

        # Check box
        box_x = j // 3
        box_y = i // 3

        i %= 3
        j %= 3

        for k in range(3):
            for l in range(3):
                m = 3*box_x + l
                n = 3*box_y + k
                if self.model[n][m] == num and (k,l) != (i,j):
                    return False

        return True


    def choices(self, n, m):
        c = [0]*self.rows
        for j in range(self.cols):
            num = self.model[n][j]
            if num != 0:
                c[num-1] += 1
        for i in range(self.rows):
            num = self.model[i][m]
            if num != 0:
                c[num-1] += 1
        # Check box
        box_x = m // 3
        box_y = n // 3
        n %= 3
        m %= 3
        for k in range(3):
            for l in range(3):
                j = 3*box_x + l
                i = 3*box_y + k
                num = self.model[i][j]
                if num != 0:
                    c[num-1] += 1
        return c.count(0)        



    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()
            self.redraw_window(SLEEP_TIME)
            self.action_steps += 1
            


    def confirm_all(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    val = self.cubes[i][j].temp
                    self.cubes[i][j].set(val)
                    self.redraw_window()
                
                

    def sketch(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(val)
            self.update_model()
            self.redraw_window(SLEEP_TIME)
        self.action_steps += 1


    def steps(self):
        return self.action_steps


    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)
        self.redraw_window()


    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)
            self.update_model()
            self.redraw_window(SLEEP_TIME)
            self.action_steps += 1

    def draw(self):
        # Draw Grid Lines
        gap = self.width / self.cols
        self.canvas.stroke_style = 'black'
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                self.canvas.line_width = 4
            else:
                self.canvas.line_width = 1
            self.canvas.stroke_line(0, round(i*gap), self.width, round(i*gap))
            self.canvas.stroke_line(round(i * gap), 0, round(i * gap), self.height)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.canvas)


    def redraw_window(self, sleep_time = 0):
        if sleep_time != 0:
            time.sleep(sleep_time)
        play_time = round(time.time() - self.start)

        with hold_canvas(self.canvas):
            self.canvas.clear()
            # Draw time
            self.canvas.fill_style = 'black'
            self.canvas.stroke_style = 'black'
            self.canvas.font = FONT_FAMILY
            self.canvas.fill_text('Time: ' + format_time(play_time), WIDTH // 2, HEIGHT+1.5*FONT_SIZE)
            # Draw grid and board
            self.draw()


class Cube:
    rows = ROWS
    cols = COLUMNS

    def __init__(self, value, row, col, width ,height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, canvas):
        gap = self.width / self.rows
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            canvas.fill_style = 'lightblue'
            canvas.stroke_style = 'lightblue'
            text = str(self.temp)
            canvas.fill_text(text,
                round(x + (gap - FONT_SIZE)/2), round(y + (gap + FONT_SIZE)/2))
        elif not(self.value == 0):
            canvas.fill_style = 'black'
            canvas.stroke_style = 'black'
            text = str(self.value)
            canvas.fill_text(text,
                round(x + (gap - FONT_SIZE)/2), round(y + (gap + FONT_SIZE)/2))
        if self.selected:
            canvas.line_width = 2
            canvas.stroke_style = 'red'
            canvas.stroke_rect(round(x), round(y), round(gap) , round(gap))


    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def format_time(secs):
    sec = secs%60
    minute = secs//60
    hour = minute//60
    mat = " " + str(minute) + ":" + str(sec)
    return mat


