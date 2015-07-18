import os


COLOR_BLACK    = 0
COLOR_RED      = 1
COLOR_GREEN    = 2
COLOR_YELLOW   = 3
COLOR_BLUE     = 4
COLOR_MAGENTA  = 5
COLOR_CYAN     = 6
COLOR_WHITE    = 7
ATTR_INTENSITY = 8
COLOR_GRAY     = COLOR_BLACK | ATTR_INTENSITY
COLOR_BRIGHT_RED      = COLOR_RED | ATTR_INTENSITY
COLOR_BRIGHT_GREEN    = COLOR_GREEN | ATTR_INTENSITY
COLOR_BRIGHT_YELLOW   = COLOR_YELLOW | ATTR_INTENSITY
COLOR_BRIGHT_BLUE     = COLOR_BLUE | ATTR_INTENSITY
COLOR_BRIGHT_MAGENTA  = COLOR_MAGENTA | ATTR_INTENSITY
COLOR_BRIGHT_CYAN     = COLOR_CYAN | ATTR_INTENSITY
COLOR_BRIGHT_WHITE    = COLOR_WHITE | ATTR_INTENSITY

KEY_UP = 1
KEY_DOWN = 2
KEY_LEFT = 3
KEY_RIGHT = 4
KEY_HOME = 5
KEY_END = 6
KEY_PGUP = 7
KEY_PGDN = 8
KEY_QUIT = 9
KEY_ENTER = 10
KEY_BACKSPACE = 11
KEY_DELETE = 12

KEYMAP = {
b"\x1b[A": KEY_UP,
b"\x1b[B": KEY_DOWN,
b"\x1b[D": KEY_LEFT,
b"\x1b[C": KEY_RIGHT,
b"\x1bOH": KEY_HOME,
b"\x1bOF": KEY_END,
b"\x1b[1~": KEY_HOME,
b"\x1b[4~": KEY_END,
b"\x1b[5~": KEY_PGUP,
b"\x1b[6~": KEY_PGDN,
b"\x03": KEY_QUIT,
b"\r": KEY_ENTER,
b"\x7f": KEY_BACKSPACE,
b"\x1b[3~": KEY_DELETE,
}


class Screen:

    @staticmethod
    def enable_mouse():
        # Mouse reporting - X10 compatibility mode
        os.write(1, b"\x1b[?9h")

    @staticmethod
    def wr(s):
        # TODO: When Python is 3.5, update this to use only bytes
        if isinstance(s, str):
            s = bytes(s, "utf-8")
        os.write(1, s)

    @staticmethod
    def wr_fixedw(s, width):
        # Write string in a fixed-width field
        s = s[:width]
        Screen.wr(s)
        Screen.wr(" " * (width - len(s)))
        # Doesn't work here, as it doesn't advance cursor
        #Screen.clear_num_pos(width - len(s))

    @staticmethod
    def cls():
        Screen.wr(b"\x1b[2J")

    @staticmethod
    def goto(row, col):
        # TODO: When Python is 3.5, update this to use bytes
        Screen.wr("\x1b[%d;%dH" % (row + 1, col + 1))

    @staticmethod
    def clear_to_eol():
        Screen.wr(b"\x1b[0K")

    # Clear specified number of positions
    @staticmethod
    def clear_num_pos(num):
        if num > 0:
            Screen.wr("\x1b[%dX" % num)

    @staticmethod
    def attr_color(fg, bg):
        assert bg <= 8
        if (fg > 8):
            Screen.wr(b"\x1b[%d;%d;1m" % (fg + 30 - 8, bg + 40))
        else:
            Screen.wr(b"\x1b[%d;%dm" % (fg + 30, bg + 40))

    @staticmethod
    def attr_reset():
        Screen.wr(b"\x1b[0m")

    @staticmethod
    def cursor(onoff):
        if onoff:
            Screen.wr(b"\x1b[?25h")
        else:
            Screen.wr(b"\x1b[?25l")

    def draw_box(self, left, top, width, height):
        # Use http://www.utf8-chartable.de/unicode-utf8-table.pl
        # for utf-8 pseudographic reference
        bottom = top + height - 1
        self.goto(top, left)
        # "┌"
        self.wr(b"\xe2\x94\x8c")
        # "─"
        hor = b"\xe2\x94\x80" * (width - 2)
        self.wr(hor)
        # "┐"
        self.wr(b"\xe2\x94\x90")

        self.goto(bottom, left)
        # "└"
        self.wr(b"\xe2\x94\x94")
        self.wr(hor)
        # "┘"
        self.wr(b"\xe2\x94\x98")

        top += 1
        while top < bottom:
            # "│"
            self.goto(top, left)
            self.wr(b"\xe2\x94\x82")
            self.goto(top, left + width - 1)
            self.wr(b"\xe2\x94\x82")
            top += 1

    def clear_box(self, left, top, width, height):
        # doesn't work
        #self.wr("\x1b[%s;%s;%s;%s$z" % (top + 1, left + 1, top + height, left + width))
        s = b" " * width
        bottom = top + height
        while top < bottom:
            self.goto(top, left)
            self.wr(s)
            top += 1

    def dialog_box(self, left, top, width, height, title=""):
        self.clear_box(left + 1, top + 1, width - 2, height - 2)
        self.draw_box(left, top, width, height)
        if title:
            #pos = (width - len(title)) / 2
            pos = 1
            self.goto(top, left + pos)
            self.wr(title)

    @classmethod
    def init_tty(cls):
        import tty, termios
        cls.org_termios = termios.tcgetattr(0)
        tty.setraw(0)

    @classmethod
    def deinit_tty(cls):
        import termios
        termios.tcsetattr(0, termios.TCSANOW, cls.org_termios)
