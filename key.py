"""Key symbols, tools, and constants for arcade-gui."""

from arcade import get_window
from pyglet.event import EventDispatcher

from geometry import Point

__all__ = [
           "Keys",
           "Mouse",
           "modifiers_string",
           "key_string",
           "motion_string",
           "user_key",
           "_key_names",
           "_motion_names",
           "_name",
           "_value"
          ]


class Keys(EventDispatcher):
    """Key state handler inspired by pyglet.window.key.KeyStateHandler."""

    def __init__(self):
        """Initialize key state handler.

        When creating a key state handler, it will push events automatically.
        
        >>> keys = Keys()
        >>> # Press and hold down the "right" key...
        >>> keys[RIGHT]
        True
        >>> keys[LEFT]
        False

        This is quite useful when seeing if a key is being held down.
        
        properties:
            data - internal map of key state handler used to track keys
            window - current window to push events to
        
        methods:
            on_key_press(self, keys, modifiers)
                Called as an event when a key is pressed.
            on_key_release(self, keys, modifiers)
                Called as an event when a key is released.
        """

        self.data = {}

        self.window = get_window()
        
        # Push event handlers to the window
        self.window.push_handlers(
            self.on_key_press,
            self.on_key_release
        )

    def on_key_press(self, keys, modifiers):
        """Called as an event when a key is pressed. This is used to update the
        key state handler.
        
        keys - key pressed
        modifiers - modifiers pressed (use bit-wise operations)
        """

        self.data[keys] = True

    def on_key_release(self, keys, modifiers):
        """Called as an eventwhen a key is released. This is used to update the 
        key state handler.
        
        keys - key released
        modifiers - modifiers released (use bit-wise operations)
        """

        self.data[keys] = False

    def __getitem__(self, key):
        """Get an item from data with key.
        
        key - key to get item from
        
        parameters: int
        returns: int
        """

        return self.data.get(key, False)


class Mouse(EventDispatcher):
    """Mouse state handler."""

    def __init__(self):
        """Initialize mouse state handler.
        
        Like a key state handler, a mouse state handler will push events
        automatically.
        
        >>> mouse = Mouse()
        >>> # Press and hold down the left mouse button...
        >>> mouse[MOUSE_BUTTON_LEFT]
        True
        >>> mouse[MOUSE_BUTTON_RIGHT]
        False

        This is quite useful when seeing if a mouse button is being held down.
        
        properties:
            x - x coordinate of mouse
            y - y coordinate of mouse
            press - bool whether or not the mouse is currently pressed
            window - current window to push events to
        
        methods:
            on_mouse_press
            on_mouse_release
            on_mouse_motion
            on_mouse_drag
            on_update
        
        TODO: add specifying button functionality
        """
        
        self.x = 0
        self.y = 0

        self.press = False

        self.point = Point()

        self.window = get_window()

        self.window.push_handlers(
            self.on_mouse_motion,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_drag,
            self.on_update
        )

    def on_mouse_press(self, x, y, buttons, modifiers):
        """Called when the mouse is pressed.
        
        x - x coordinate of mouse press
        y - y coordinate of mouse press
        buttons - buttons pressed by mouse
        modifiers - modifiers being held down during mouse press
        
        parameters: int, int, int, int
        """

        self.press = True

    def on_mouse_release(self, x, y, buttons, modifiers):
        """Called when the mouse is released.
        
        x - x coordinate of mouse release
        y - y coordinate of mouse release
        buttons - buttons released by mouse
        modifiers - modifiers being held down during mouse release
        
        parameters: int, int, int, int
        """

        self.press = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Called when the mouse is moved.
        
        x - x coordinate of mouse
        y - y coordinate of mouse
        dx - difference in x coordinates from last position
        dy - difference in y coordinates from last position
        
        parameters: int, int, int, int
        """

        self.x = x
        self.y = y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Called when the mouse is dragged.

        x - x coordinate of mouse drag
        y - y coordinate of mouse drag
        dx - difference in x coordinates from last position
        dy - difference in y coordinates from last position
        buttons - buttons being held down during mouse drag
        modifiers - modifiers being held down during mouse drag
        
        parameters: int, int, int, int, int, int
        """

        self.x = x
        self.y = y

    def on_update(self, delta):
        """Called every tick of the update cycle.
        
        delta - time since the last update was called
        
        parameters: int
        """

        self.point.x = self.x
        self.point.y = self.y


# Predefines keyboard constants

# These constants allow you to use the keyboard and mouse constants without
# defining your own. There are also functions to find your own keyboard
# constants, which can be put into variables for simplicity.

# Mouse buttons
MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_MIDDLE = 2
MOUSE_BUTTON_RIGHT = 4

# Key modifiers
# Done in powers of two, so you can do a bit-wise 'and' to detect
# multiple modifiers.
SHIFT = 1
CONTROL = 2
ALT = 4
CAPSLOCK = 8
NUMLOCK = 16
WINDOWS = 32
COMMAND = 64
OPTION = 128
SCROLLLOCK = 256
ACCEL = 2

# Keys
BACKSPACE = 65288
TAB = 65289
LINEFEED = 65290
CLEAR = 65291
RETURN = 65293
ENTER = 65293
PAUSE = 65299
SCROLLLOCK = 65300
SYSREQ = 65301
ESCAPE = 65307
HOME = 65360
KEY_LEFT = 65361
KEY_UP = 65362
KEY_RIGHT = 65363
KEY_DOWN = 65364
PAGEUP = 65365
PAGEDOWN = 65366
END = 65367
BEGIN = 65368
DELETE = 65535
SELECT = 65376
PRINT = 65377
EXECUTE = 65378
INSERT = 65379
UNDO = 65381
REDO = 65382
MENU = 65383
FIND = 65384
CANCEL = 65385
HELP = 65386
BREAK = 65387
MODESWITCH = 65406
SCRIPTSWITCH = 65406

MOTION_UP = 65362
MOTION_RIGHT = 65363
MOTION_DOWN = 65364
MOTION_LEFT = 65361
MOTION_NEXT_WORD = 1
MOTION_PREVIOUS_WORD = 2
MOTION_BEGINNING_OF_LINE = 3
MOTION_END_OF_LINE = 4
MOTION_NEXT_PAGE = 65366
MOTION_PREVIOUS_PAGE = 65365
MOTION_BEGINNING_OF_FILE = 5
MOTION_END_OF_FILE = 6
MOTION_BACKSPACE = 65288
MOTION_DELETE = 65535
MOTION_COPY = 7
MOTION_PASTE = 8

NUMLOCK = 65407
NUM_SPACE = 65408
NUM_TAB = 65417
NUM_ENTER = 65421
NUM_F1 = 65425
NUM_F2 = 65426
NUM_F3 = 65427
NUM_F4 = 65428
NUM_HOME = 65429
NUM_LEFT = 65430
NUM_UP = 65431
NUM_RIGHT = 65432
NUM_DOWN = 65433
NUM_PRIOR = 65434
NUM_PAGE_UP = 65434
NUM_NEXT = 65435
NUM_PAGE_DOWN = 65435
NUM_END = 65436
NUM_BEGIN = 65437
NUM_INSERT = 65438
NUM_DELETE = 65439
NUM_EQUAL = 65469
NUM_MULTIPLY = 65450
NUM_ADD = 65451
NUM_SEPARATOR = 65452
NUM_SUBTRACT = 65453
NUM_DECIMAL = 65454
NUM_DIVIDE = 65455

# Numbers on the numberpad
NUM_0 = 65456
NUM_1 = 65457
NUM_2 = 65458
NUM_3 = 65459
NUM_4 = 65460
NUM_5 = 65461
NUM_6 = 65462
NUM_7 = 65463
NUM_8 = 65464
NUM_9 = 65465

F1 = 65470
F2 = 65471
F3 = 65472
F4 = 65473
F5 = 65474
F6 = 65475
F7 = 65476
F8 = 65477
F9 = 65478
F10 = 65479
F11 = 65480
F12 = 65481
F13 = 65482
F14 = 65483
F15 = 65484
F16 = 65485
LSHIFT = 65505
RSHIFT = 65506
LCTRL = 65507
RCTRL = 65508
CAPSLOCK = 65509
LMETA = 65511
RMETA = 65512
LALT = 65513
RALT = 65514
LWINDOWS = 65515
RWINDOWS = 65516
LCOMMAND = 65517
RCOMMAND = 65518
LOPTION = 65488
ROPTION = 65489
SPACE = 32
EXCLAMATION = 33
DOUBLEQUOTE = 34
HASH = 35
POUND = 35
DOLLAR = 36
PERCENT = 37
AMPERSAND = 38
APOSTROPHE = 39
PARENLEFT = 40
PARENRIGHT = 41
ASTERISK = 42
PLUS = 43
COMMA = 44
MINUS = 45
PERIOD = 46
SLASH = 47

# Numbers on the main keyboard
KEY_0 = 48
KEY_1 = 49
KEY_2 = 50
KEY_3 = 51
KEY_4 = 52
KEY_5 = 53
KEY_6 = 54
KEY_7 = 55
KEY_8 = 56
KEY_9 = 57
COLON = 58
SEMICOLON = 59
LESS = 60
EQUAL = 61
GREATER = 62
QUESTION = 63
AT = 64
BRACKETLEFT = 91
BACKSLASH = 92
BRACKETRIGHT = 93
ASCIICIRCUM = 94
UNDERSCORE = 95
GRAVE = 96
QUOTELEFT = 96
A = 97
B = 98
C = 99
D = 100
E = 101
F = 102
G = 103
H = 104
# noinspection PyPep8
I = 105
J = 106
K = 107
L = 108
M = 109
N = 110
# noinspection PyPep8
O = 111
P = 112
Q = 113
R = 114
S = 115
T = 116
U = 117
V = 118
W = 119
X = 120
Y = 121
Z = 122
BRACELEFT = 123
BAR = 124
BRACERIGHT = 125
ASCIITILDE = 126

_key_names = {}
_motion_names = {}

for _name, _value in locals().copy().items():
    if _name[:2] != '__' and _name.upper() == _name and \
        not _name.startswith('SHIFT') and \
        not _name.startswith("CONTROL") and \
        not _name.startswith("ALT") and \
        not _name.startswith("CAPSLOCK") and \
        not _name.startswith("NUMLOCK") and \
        not _name.startswith("SCROLLLOCK") and \
        not _name.startswith("COMMAND") and \
        not _name.startswith("OPTION"):
        if _name.startswith('MOTION_'):
            _motion_names[_value] = _name
        else:
            _key_names[_value] = _name

def modifiers_string(modifiers):
    """Return a string describing a set of modifiers.

    >>> modifiers_string(SHIFT | CONTROL)
    "SHIFT|CONTROL"

    modifiers - bitwise combination of modifiers

    returns: str
    """

    modifier_names = []

    if modifiers & SHIFT:
        modifier_names.append("SHIFT")
    if modifiers & CONTROL:
        modifier_names.append("CTRL")
    if modifiers & ALT:
        modifier_names.append("ALT")
    if modifiers & CAPSLOCK:
        modifier_names.append("CAPSLOCK")
    if modifiers & NUMLOCK:
        modifier_names.append("NUMLOCK")
    if modifiers & SCROLLLOCK:
        modifier_names.append("SCROLLLOCK")
    if modifiers & COMMAND:
        modifier_names.append("COMMAND")
    if modifiers & OPTION:
        modifier_names.append("OPTION")
    
    return '|'.join(modifier_names)

def key_string(key):
    """Return a string describing a key symbol.

    >>> key_string(BACKSPACE)
    "BACKSPACE"

    key - key symbol

    parameters: int (32-bit)
    returns: str
    """

    if key < 1 << 32:
        return _key_names.get(key, str(key))
    else:
        return 'user_key(%x)' % (key >> 32)


def motions_string(motion):
    """Return a string describing a text motion. These motions are called
    with pyglet.text.layout.IncrementalTextLayouts.

    >>> motion_string(MOTION_NEXT_WORD)
    "MOTION_NEXT_WORD"

    motion - text motion constant

    parameters: int (32-bit)
    returns: str
    """

    return _motion_names.get(motion, str(motion))


def user_key(scancode):
    """Return a key symbol for a key not supported.

    This can be used to map virtual keys or scancodes from unsupported
    keyboard layouts into a machine-specific symbol.  The symbol will
    be meaningless on any other machine, or under a different keyboard layout.

    Applications should use user-keys only when user explicitly binds them
    (for example, mapping keys to actions in a game options screen).
    """

    assert scancode > 0
    return scancode << 32
