"""GUI interface and widgets.

More than meets the eye in this example. To see all features, look at the source
code of each widget.
"""


from arcade import create_rectangle_filled, draw_rectangle_outline, \
    enable_timings, get_fps, get_window, \
    load_texture, run, schedule, unschedule
from arcade import Sprite, SpriteList, Text, Window
from cmath import tau
from string import printable
from tkinter import Tk
from typing import Tuple

from color import BLACK, BLUE_YONDER, COOL_BLACK, DARK_GRAY, DARK_SLATE_GRAY, GRAY, GRAY_BLUE, RED, WHITE
from color import four_byte, scale_color
from constants import BOTTOM, CENTER, DEFAULT_FONT, DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, DISABLE_ALPHA, \
     ENTRY_BLINK_INTERVAL, KNOB_HOVER_SCALE, LEFT, MULTIPLE, SINGLE, SLIDER_VELOCITY, \
     TOGGLE_FADE, TOGGLE_VELOCITY, TOP
from file import button, entry_normal, knob, none, slider_horizontal, \
     toggle_false, toggle_true, toggle_false_hover, toggle_true_hover
from key import  A, C, CONTROL, ENTER, KEY_LEFT, KEY_RIGHT, MOTION_BACKSPACE, MOTION_BEGINNING_OF_FILE, MOTION_BEGINNING_OF_LINE, MOTION_COPY, MOTION_DELETE, MOTION_DOWN, MOTION_END_OF_FILE, MOTION_END_OF_LINE, MOTION_LEFT, MOTION_NEXT_WORD, MOTION_PREVIOUS_WORD, MOTION_RIGHT, MOTION_UP, \
     MOUSE_BUTTON_LEFT, SHIFT, SPACE, TAB, V, X
from key import Keys

from pyglet.event import EventDispatcher
from pyglet.text import decode_text
from pyglet.text.caret import Caret
from pyglet.text.layout import IncrementalTextLayout
from pyglet.shapes import BorderedRectangle, Circle, Ellipse, Line, Triangle, Sector, Star, Polygon, Arc

from webbrowser import open_new_tab

MAX = 2 ** 32

enable_timings()

clipboard = Tk()
clipboard.withdraw()

def clipboard_get():
    """Get some text from the clipboard.
    
    returns: str
    """
    
    return clipboard.clipboard_get()

def clipboard_append(text):
    """Append some text to the clipboard.
    
    text - text to append to the clipboard
    
    parameters: str
    """
    
    clipboard.clipboard_append(text)

def insert(index, text, add):
    return text[:index] + add + text[index:]

def delete(start, end, text):
    if len(text) > end:
        text = text[0: start:] + text[end + 1::]
    return text


class Font:
    """An object-oriented Font."""

    def __init__(self,
                 family=DEFAULT_FONT_FAMILY,
                 size=DEFAULT_FONT_SIZE
                ):
                
        """Initialize an object-oriented Font. This is an experimental
        feature developed on August 4th 2022 and has no effect.
        
        family - family of the font (style)
        size - size of the font (not in pixels
        
        parameters: int, int
        """

        self.family = family
        self.size = size

        self.list = [self.family, self.size]

    def __getitem__(self, item):
        """Get an item from the list.
        
        item - item whose value to be returned
        
        parameters: int
        returns: str or int
        """

        return self.list[item]

    def __setitem__(self, index, item):
        """Get an item from the list.
        
        item - item whose value to be set
        
        parameters: int, str or int
        """

        self.list[index] = item


default_font = Font()


class Container(EventDispatcher):

    def __init__(self, window=None, shadow=False):
        EventDispatcher.__init__(self)

        self.focus = None
        self.enable = True

        self.shadow = shadow
        
        self.widgets = SpriteList()

        self.window = window or get_window()
        
        self.window.push_handlers(self.on_key_press)

    def append(self, widget):
        self.widgets.append(widget)

        widget.container = self

    def draw(self):
        for widget in self.widgets:
            widget.draw()
            widget.frame.draw()

            shade = 1
            
            if self.shadow:
                for i in range(1, 100):
                    shade += 0.01
                    print(scale_color(self.shadow, int(shade)))
                    draw_rectangle_outline(widget.x, widget.y,
                                            widget.width + 1, widget.height + 1,
                                            RED)

    def draw_bbox(self, width=1, padding=0):
        for widget in self.widgets: widget.draw_bbox(width, padding)

    def exit(self):
        for widget in self.widgets: widget.destroy()

        self.enable = False
        
    def on_key_press(self, keys, modifiers):
       if keys == TAB:
            if modifiers & SHIFT:
                direction = -1
            else:
                direction = 1

            if self.focus in self.widgets:
                i = self.widgets.index(self.focus)
            else:
                i = 0
                direction = 0
            
            self.focus = self.widgets[(i + direction) % len(self.widgets)]

            self.focus.focus = True

##            if isinstance(self.focus, Button):
##                self.focus.image.scale = FOCUS_SIZE
##            elif isinstance(self.focus, Toggle) or \
##                 isinstance(self.focus, Slider):
##                self.focus.bar.scale = FOCUS_SIZE
##                self.focus.knob.scale = FOCUS_SIZE
##
            for widget in self.widgets:
                if not widget == self.focus:
                    widget.focus = False


class Frame:

    def __init__(self, x, y, width=200, height=200, direction=BOTTOM):
        self.x = x
        self.y = y

        self.width = self.x
        self.height = self.y

        self.direction = direction
        self.color = WHITE

        self.widgets = []

        self.shape = create_rectangle_filled(self.x, self.y,
                                             10, 10,
                                             self.color)

    def append(self, widget):
        self.widgets.append(widget)

    def draw(self):
        self.shape.draw()

    
class Widget(Sprite, EventDispatcher):
    """Base widget class"""
    
    def __init__(self, image=none, scale=1.0, frame=None):
        Sprite.__init__(self, image, scale)

        self.frame = frame or Frame(0, 0)
        
        self.x = 0
        self.y = 0

        self.frame.append(self)

        self.hover = False
        self.press = False
        self.disable = False
        
        self.drag = False

        self.focus = False

        self.component = None
        self.container = None

        self._left = None
        self._right = None
        self._top = None
        self._bottom = None
        
        self.frames = 0

        self.keys = Keys()

        self.window = get_window()

        self.window.push_handlers(
            self.on_key_press,
            self.on_key_release,
            self.on_mouse_motion,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_scroll,
            self.on_mouse_drag,
            self.on_text_motion_select,
            self.on_update
        )

    def _get_x(self):
        return self._position[0]

    def _set_x(self, new_value):
        if new_value != self._position[0]:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._position = (new_value, self._position[1])
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_location(self)

    def _get_y(self):
        return self._position[1]

    def _set_y(self, new_value):
        if new_value != self._position[1]:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._position = (self._position[0], new_value)
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_location(self)

    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)

    def center(self, width, height):
        self.x = width / 2
        self.y = height / 2

    def _check_collision(self, x, y):
        return (0 < x - self.x < self.width and
                0 < y - self.y < self.height)

    def check_collision(self, x, y):
        if self._right and \
           self._left and \
           self._top and \
           self._bottom:
            return x > self._left and x < self._right and \
                   y > self._bottom and y < self._top
        
        return x > self.left and x < self.right and \
               y > self.bottom and y < self.top

    def draw_bbox(self, width=1, padding=0):
        draw_rectangle_outline(self.x, self.y,
                                      self.width, self.height,
                                      RED, width)

    def destroy(self):
        self.keys = []
        self.disable = True
        self.focus = False
        
        self.window.remove_handlers(
            self.on_key_press,
            self.on_key_release,
            self.on_mouse_motion,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_scroll,
            self.on_mouse_drag,
            self.on_text_motion_select,
            self.on_update)
        
        self.remove_from_sprite_lists()
        
    def on_key_press(self, keys, modifiers):
        if self.disable:
            return
        
        self.dispatch_event("on_key", keys, modifiers)

        if self.focus:
            self.dispatch_event("on_focus")
            
    def on_key_release(self, keys, modifiers):
        if self.disable:
            return
        
        self.press = False

        self.dispatch_event("on_lift", keys, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.disable:
            return

        if self.check_collision(x, y):
            self.hover = True

            self.dispatch_event("on_hover", x, y, dx, dy)
        else:
            self.hover = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.disable:
            return

        if self.check_collision(x, y):
            self.press = True
            self.focus = True

            self.dispatch_event("on_press", x, y, buttons, modifiers)
            self.dispatch_event("on_focus")

    def on_mouse_release(self, x, y, buttons, modifiers):
        if self.disable:
            return
        
        self.press = False

        if not self.check_collision(x, y):
            self.focus = False

        self.drag = False

        self.dispatch_event("on_release", x, y, buttons, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.disable:
            return
        
        self.drag = True

        if self.check_collision(x, y):
            self.dispatch_event("on_drag", x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x, y, mouse, direction):
        if self.disable:
            return
        
        if self.check_collision(x, y):
            if self.disable:
                return
        
            self.dispatch_event("on_scroll", x, y, mouse, direction)

    def on_text_motion_select(self, motion):
        self.dispatch_event("on_text_select", motion)

    def on_update(self, delta_time):
        self.frames += 1
        
        if self.component:
            self.x = self.component.x
            self.y = self.component.y
            
            self.width = self.component.width
            self.height = self.component.height

            self.left = self.component.left
            self.right = self.component.right
            self.top = self.component.top
            self.bottom = self.component.bottom

            self.hit_box = self.component.hit_box

            if self.disable:
                self.component.alpha = DISABLE_ALPHA

        if self.container and not self.container.enable:
            self.disable = True
            
        self.dispatch_event("update")

   
Widget.register_event_type("update")

Widget.register_event_type("on_key")
Widget.register_event_type("on_lift")
Widget.register_event_type("on_hover")
Widget.register_event_type("on_press")
Widget.register_event_type("on_release")
Widget.register_event_type("on_drag")
Widget.register_event_type("on_scroll")
Widget.register_event_type("on_focus")

Widget.register_event_type("on_text_select")


class Image(Widget):
    
    def __init__(self, image, x, y, scale=1):
        Widget.__init__(self, image, scale)

        self.image = image
        
        self.x = x
        self.y = y


class Label(Widget):
    """Label widget to draw and display HTML text."""
    
    def __init__(self, text, x, y, frame=None,
                 colors=[BLACK, (COOL_BLACK, DARK_SLATE_GRAY, DARK_GRAY)],
                 font=DEFAULT_FONT, title=False,
                 justify=LEFT, width=0, multiline=False,
                 command=None, parameters=[],
                 outline=None
                ):
        
        # For new arcade installations, change the self.label property in
        # Text to a HTMLLabel for HTML scripting
        #
        # self._label = pyglet.text.HTMLLabel(
        #     text=text,
        #     x=start_x,
        #     y=start_y,
        #     width=width,
        #     multiline=multiline
        # )
        #
        # The Label widget is the only widget with a LEFT x anchor.
        #

        if not text:
            text = "Label"
            
        self.label = Text(f"{text}", x, y,
                          anchor_x=LEFT, anchor_y=CENTER,
                          width=width, multiline=multiline)
        
        Widget.__init__(self, frame=frame)

        self.x = x + self.frame.x
        self.y = y + self.frame.y
        
        if self.frame.direction == TOP:
            self.x = self.frame.x - x
            self.y = self.frame.y - y
                
        self.text = text
        self.colors = colors
        self.font = font
        self.title = title
        self.justify = justify
        self.width = width
        self.multiline = multiline
        self.command = command
        self.parameters = parameters
        self.outline = outline

        self.keys = []
    
        self.activated = False

        self.document = None
        self.length = 0

    def bind(self, *keys):
        self.keys = [*keys]
        return self.keys

    def unbind(self, *keys):
        for key in keys:
            self.keys.remove(key)
        return self.keys
    
    def draw_bbox(self, width=1, padding=0):
        """Overrides the Widget.bbox because of anchor_x"""
        draw_rectangle_outline(
            self.x + self.width / 2,
            self.y, self.width + padding,
            self.height + padding, RED, width
        )
        
    def invoke(self):
        if self.disable or not self.command:
            return
        
        self.press = True
        
        if self.parameters:
            self.command(*self.parameters)
        else:
            self.command()
        
    def draw(self):
        self.label.draw()
        
        self.width = self.label.content_width
        self.height = self.label.content_height

        if self.text == "Label":
            self.label.visible = False
        else:
            self.label.visible = True
        
        if self.outline:
            draw_rectangle_outline(
                self.x + self.width / 2, self.y,
                self.width + self.outline[1],
                self.height + self.outline[1],
                self.outline[0], self.outline[2]
            )

        if self.text:
            self._left = self.label.left
            self._right = self.label.right
            self._top = self.label.top
            self._bottom = self.label.bottom
        
        self.activated = True

    def on_key(self, keys, modifiers):
        if isinstance(self.keys, list):
            if keys in self.keys:
                self.invoke()

        else:
            if self.keys == keys:
                self.invoke()

    def on_press(self, x, y, buttons, modifiers):
        if self.disable or not self.command:
            return

        if buttons == MOUSE_BUTTON_LEFT:
            self.invoke()

    def update(self):
        """Update the Label. This upgrades its properties and registers its
        states and events.
        
        The following section has been tested dozens of times. The performance
        is incredibly slow, with about 1 fps for 100 Labels. Usually, for a
        single Label the processing time is about one-hundredth of a second.
        
        With the begin_update() and end_update() functions for the label, the
        processing time is much faster. With 100 Labels, the fps is about eight.
        """

        self.label._label.begin_update()

        self.label.value = self.text
        self.label.x = self.x
        self.label.y = self.y
        self.label.font_name = self.font[0]
        self.label.font_size = self.font[1]
        self.label.opacity = self.alpha
        self.label.align = self.justify
        self.label.multiline = self.multiline

        self.label._label.end_update()

        self.document = self.label._label.document
        self.length = len(self.text)
        
        if "<u" in self.text and "<\\u>":
            # ValueError: Can only assign sequence of same size
            return

        # States
        if self.hover:
            self.document.set_style(0, self.length,
                                    {"color" : four_byte(self.colors[1][0])})
        if self.press:
            self.document.set_style(0, self.length,
                                    {"color" : four_byte(self.colors[1][1])})
        if self.disable:
            self.document.set_style(0, self.length,
                                    {"color" : four_byte(self.colors[1][2])})

        if self.focus:
            self.document.set_style(0, self.length,
                                    {"color" : four_byte(self.colors[1][0])})

        
class Button(Widget):
    """Button widget to invoke and call commands. Pressing on a Button invokes
    its command, which is a function or callable.
    """

    keys = []
    
    def __init__(
                 self, text, x, y, command=None, parameters=[],
                 link=None,
                 colors=["yellow", BLACK], font=default_font,
                 callback=SINGLE
                ):

        """Initialize a Button. A Button has two components: an Image and a
        Label. You can customize the Button's images and display by changing
        its normal_image, hover_image, press_image, and disable_image
        properties, but it is recommended to use the CustomButton widget.

        text - text to be displayed on the Button
        x - x coordinate of the Button
        y - y coordinate of the Button
        command - command to be invoked when the Button is called
        parameters - parameters of the callable when invoked
        link - website link to go to when invoked
        colors - colors of the Button
        font - font of the Button
        callback - how the Button is invoked:
                   SINGLE - the Button is invoked once when pressed
                   DOUBLE - the Button can be invoked multiple times in focus
                   MULTIPLE - the Button can be invoked continuously
        
        parameters: str, int, int, callable, list, tuple, Font, str
        """

        # A two-component widget:
        #     - Image
        #     - Label

        self.image = Image(button[f"{colors[0]}_button_normal"], x, y)
        self.label = Label(text, x, y, font=font)

        Widget.__init__(self)

        self.text = text
        self.x = x
        self.y = y
        self.command = command
        self.parameters = parameters
        self.link = link
        self.colors = colors
        self.font = font
        self.callback = callback

        self.normal_image = load_texture(button[f"{colors[0]}_button_normal"])
        self.hover_image = load_texture(button[f"{colors[0]}_button_hover"])
        self.press_image = load_texture(button[f"{colors[0]}_button_press"])
        self.disable_image = load_texture(button[f"{colors[0]}_button_disable"])

    def bind(self, *keys):
        """Bind some keys to the Button. Invoking these keys activates the
        Button. If the key Enter was binded to the Button, pressing Enter will
        invoke its command and switches its display to a pressed state.

        >>> button.bind(ENTER, PLUS)
        [65293, 43]

        *keys - keys to be binded

        parameters: *int (32-bit)
        returns: list
        """

        self.keys = [*keys]
        return self.keys

    def unbind(self, *keys):
        """Unbind keys from the Button.

        >>> button.bind(ENTER, PLUS, KEY_UP, KEY_DOWN)
        [65293, 43, 65362, 65364]
        >>> button.unbind(PLUS, KEY_UP)
        [65293, 65364]

        parameters: *int(32-bit)
        returns: list
        """

        for key in keys:
            self.keys.remove(key)
        return self.keys

    def invoke(self):
        """Invoke the Button. This switches its image to a pressed state and
        calls the command with the specified parameters. If the Button is
        disabled this will do nothing.
        """

        if self.disable or not self.command:
            return

        self.press = True

        if self.parameters:
            self.command(self.parameters)
        else:
            self.command()
        
        if self.link:
            open_new_tab(self.link)
    
    def draw(self):
        """Draw the Button. The component of the Button is the image, which takes
        all of the collision points.
        
        1. Image - background image of the Button
        2. Label - text of the Button
        """

        self.image.draw()
        self.label.draw()

        # Update Label properties

        self.label.text = self.text
        self.label.x = self.x
        self.label.y = self.y
        self.label.colors[0] = self.colors[1]
        self.label.font = self.font
        self.label.label.anchor_x = CENTER

        self.component = self.image

    def on_press(self, x, y, buttons, modifiers):
        """The Button is pressed. This invokes its command if the mouse button
        is the left one.

        TODO: add specifying proper mouse button in settings

        x - x coordinate of the press
        y - y coordinate of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if buttons == MOUSE_BUTTON_LEFT:
            self.invoke()

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the
        Button has focus.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int (32-bit), int (32-bit)
        """

        if keys == SPACE and self.focus:
            self.invoke()

        if isinstance(self.keys, list):
            if keys in self.keys:
                self.invoke()

        else:
            if self.keys == keys:
                self.invoke()
            
    def update(self):
        """Update the Button. This registers events and updates the Button
        image.
        """

        if self.hover:
            self.image.texture = self.hover_image
        if self.press:
            self.image.texture = self.press_image
        if self.disable:
            self.image.texture = self.disable_image
        if not self.hover \
           and not self.press \
           and not self.disable:
            self.image.texture = self.normal_image

        if self.callback == MULTIPLE and self.press:
            self.invoke()

        # .update is not called for the Label, as it is uneccessary for the
        # Label to switch colors on user events.
        
        self.image.update()


class Slider(Widget):
    """Slider widget to display slidable values.
    
    FIXME: add keyboard functionality
    """

    _value = 0
    destination = 0
    
    def __init__(self, text, x, y, colors=BLACK, font=DEFAULT_FONT,
                 size=10, length=200, padding=50, round=0):
        """Initialize a Slider."""
        
        self.bar = Image(slider_horizontal, x, y)
        self.knob = Image(knob, x, y)
        self.label = Label(text, x, y, font=font)

        Widget.__init__(self)
        
        self.x = x
        self.y = y
        self.text = text
        self.colors = colors
        self.font = font
        self.size = size
        self.length = length
        self.padding = padding
        self.round = round
        
        self.knob.left = self.bar.x - self.length / 2
        self.label.x = self.bar.left - self.padding
    
    def _get_value(self):
        """Get the value or x of the Slider.
        
        returns: int
        """

        return self._value

    def _set_value(self, value):
        """Set the value or x of the Slider.
        
        value - new value to be set
        
        parameters: int
        """

        if self._value >= self.size:
            self._value = self.size
            return
        elif self._value <= 0:
            self._value = 0
            return

        max_knob_x = self.right# + self.knob.width / 2

        self._value = round(value, self.round)

        x = (max_knob_x - self.left) * value / self.size \
            + self.left + self.knob.width / 2
        self.knob.x = max(self.left, min(x - self.knob.width / 2, max_knob_x))

    value = property(_get_value, _set_value)

    def update_knob(self, x):
        """Update the knob and give it a velocity when moving. When calling
        this, the knob's position will automatically update so it is congruent 
        with its size.
        
        x - x coordinate of the position
        
        parameters: int
        """

        self.destination = max(self.left, 
                               min(x - self.knob.width / 2, self.right))
        self._value = round(abs(((self.knob.x - self.left) * self.size) \
                      / (self.left - self.right)), self.round)
    
    def reposition_knob(self):
        """Update the value of the Slider. This is used when you want to move
        the knob without it snapping to a certain position and want to update
        its value. update_knob(x) sets a velocity so the knob can glide.
        """

        self._value = round(abs(((self.knob.x - self.left) * self.size) \
                      / (self.left - self.right)), self.round)
        
    def draw(self):
        """Draw the Slider. The component of the Slider is the bar, which takes
        all of the collision points.
        
        1. Bar (component)
        2. Knob
        3. Label
        """

        self.bar.draw()
        self.knob.draw()
        self.label.draw()

        if not self.text:
            self.text = "Label"

        # Repositioning
        self.knob.y = self.y
        
        self.label.x = self.bar.left - self.padding
        self.label.y = self.y
        
        self.label.text = self.text
        self.label.font = self.font
        self.label.colors[0] = self.colors

        self.bar.width = self.length
        self.component = self.bar

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the Slider
        has focus. On a right key press, the value is incremented by one. On a
        left key press, the value is decremented by one.
        
        Unfortunately, this is not working currently.

        keys - key pressed
        modifiers - modifier pressed
        
        parameters: int (32-bit), int (32-bit)
        """

        if not self.focus:
            return
        
        if keys == KEY_RIGHT:
            self.knob.x = self.knob.x + (int(self.length / self.size))
            self.reposition_knob()
        elif keys == KEY_LEFT:
            self.knob.x = self.knob.x - (int(self.length / self.size))
            self.reposition_knob()

    def on_press(self, x, y, buttons, modifiers):
        """The Slider is pressed. This updates the knob to the x position of the
        press.
        
        x - x coordinate of the press
        y - y coordinate of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        self.update_knob(x)

    def on_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse when it was pressed. This updates the knob
        to the x position of the press.
        
        x - x coordinate of the press
        y - y coordinate of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        self.update_knob(x)

    def on_scroll(self, x, y, mouse, direction):
        """The user scrolled the mouse wheel. This will change the knob's
        position and adjust its x position.
        
        x - x coordinate of the mouse scroll
        y - y coordinate of the mouse scroll
        mouse - movement in vector from the last position (x, y)
        direction - direction of mouse scroll
        
        parameters: int, int, tuple (x, y), float
        """

        self.update_knob(self.knob.x + self.knob.width / 2 + direction)
        
    def update(self):
        """Update the knob. This adjusts its position and adds effects like
        gliding when the knob is moving. This way, the knob doesn't just snap to
        position. When the knob is hovered, its scale is increased by
        KNOB_HOVER_SCALE.
        """

        if self.destination:
            if self.knob.x <= self.destination and \
               self.knob.right <= self.right:
                # Knob too left, moving to the right
                self.knob.x += SLIDER_VELOCITY
                self.reposition_knob()
            if self.knob.x > self.destination and \
               self.knob.left >= self.left:
                # Knob too right, moving to the left
                self.knob.x -= SLIDER_VELOCITY
                self.reposition_knob()

        # Knob hover effect
        if self.knob.hover:
            self.knob.scale = KNOB_HOVER_SCALE
        else:
            self.knob.scale = 1
        
        self.bar.update()
        self.knob.update()
        self.label.update()


class Toggle(Widget):
    """Toggle widget to switch between true and false values. This uses
    a special effect of fading during the switch.
    """

    true_image = load_texture(toggle_true)
    false_image = load_texture(toggle_false)
    hover_true_image = load_texture(toggle_true_hover)
    hover_false_image = load_texture(toggle_false_hover)

    on_left = True
    on_right = False
    value = None
    switch = False

    def __init__(
                 self, text, x, y,
                 colors=BLACK, font=DEFAULT_FONT,
                 default=True, padding=160
                ):

        """Initialize a Toggle. A Toggle is a widget that when pressed, switches
        between True and False values.

        text - text to be displayed alongside the Toggle
        x - x coordinate of the Toggle
        y - y coordinate of the Toggle
        colors - text color of the Label
        font - font of the Label
        default - default value of the Toggle
        padding - padding of the Label and the Toggle
        
        parameters: str, int, int, tuple, tuple, bool, int
        """

        # A three-component widget:
        #     - Image
        #     - Image
        #     - Label

        if default:
            image = toggle_true
        else:
            image = toggle_false
        
        self.bar = Image(image, x, y)
        self.knob = Image(knob, x, y)

        self.label = Label(knob, x, y, font=font)
                
        Widget.__init__(self)
             
        self.text = text
        self.x = x
        self.y = y
        self.colors = colors
        self.font = font
        self.padding = padding

        self.knob.left = self.bar.left + 2

    def draw(self):
        """Draw the toggle. The component of the toggle is the bar, which takes
        all of the collision points.
        
        1. Bar (component)
        2. Knob
        3. Label
        """

        self.bar.draw()
        self.knob.draw()
        self.label.draw()

        # Repositioning
        self.knob.y = self.y
        
        self.label.x = self.bar.left - self.padding
        self.label.y = self.y
        
        self.label.text = self.text
        self.label.colors[0] = self.colors
        self.label.font = self.font
        self.label.disable = self.disable
        
        self.component = self.bar
        
    def on_press(self, x, y, buttons, modifiers):
        """The Toggle is pressed. This switches between True and False values. If
        the Control key is held down during this, this will have no effect.
        
        x - x coordinate of the press
        y - y coordinate of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """
        
        if not modifiers & CONTROL:
            self.switch = True

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the Toggle
        has focus. If the Space or Enter key is pressed, the Toggle will be
        switched.
        
        keys - key pressed
        modifiers - modifier pressed
        
        parameters: int (32-bit), int (32-bit)
        """

        if self.focus:
            if keys == SPACE or keys == ENTER:
                self.switch = True
        
    def update(self):
        """Update the toggle. This updates its position and registers its
        special effects.
        """

        if self.on_left:
            self.value = True
        else:
            self.value = False

        if self.switch and not self.disable:
            if self.on_left:
                # Knob on the left, moving towards the right
                if self.knob.right < self.bar.right - 2:
                    self.knob.x += TOGGLE_VELOCITY
                else:
                    self.on_right = True
                    self.on_left = False

                    self.switch = False
                    
                if self.knob.x < self.x:
                    try: self.bar.alpha -= TOGGLE_FADE
                    except ValueError: pass
                elif self.knob.x > self.x: # More than halfway
                    try: self.bar.alpha += TOGGLE_FADE
                    except ValueError: pass

                    self.bar.texture = self.false_image
                    if self.hover: self.bar.texture = self.hover_false_image

            elif self.on_right:
                # Knob on the right, moving towards the left
                if self.knob.left > self.bar.left + 2:
                    self.knob.x -= TOGGLE_VELOCITY
                else:
                    self.on_left = True
                    self.on_right = False

                    self.switch = False

                if self.knob.x > self.x:
                    try: self.bar.alpha -= TOGGLE_FADE
                    except ValueError: pass
                elif self.knob.x < self.x:
                    try: self.bar.alpha += TOGGLE_FADE
                    except ValueError: pass

                    self.bar.texture = self.hover_true_image
                    if self.hover: self.bar.texture = self.hover_true_image

        else:
            if self.hover:
                if self.value: self.bar.texture = self.hover_true_image
                else: self.bar.texture = self.hover_false_image
            else:
                if self.value: self.bar.texture = self.true_image
                else: self.bar.texture = self.false_image

        if self.disable:
            if self.value: self.bar.texture = self.true_image
            else: self.bar.texture = self.false_image

        self.bar.update()
        self.knob.update()


class Caret(Caret):
    """Caret used for pyglet.text.IncrementalTextLayout."""

    def on_text_motion(self, motion, select=False):
        """The caret was moved or a selection was made with the keyboard.

        motion - motion the user invoked. These are found in the keyboard.
                 MOTION_LEFT                MOTION_RIGHT
                 MOTION_UP                  MOTION_DOWN                
                 MOTION_NEXT_WORD           MOTION_PREVIOUS_WORD
                 MOTION_BEGINNING_OF_LINE   MOTION_END_OF_LINE
                 MOTION_NEXT_PAGE           MOTION_PREVIOUS_PAGE
                 MOTION_BEGINNING_OF_FILE   MOTION_END_OF_FILE
                 MOTION_BACKSPACE           MOTION_DELETE
                 MOTION_COPY                MOTION_PASTE
        select - a selection was made simultaneously

        parameters: int (32-bit), bool
        returns: event
        """

        if motion == MOTION_BACKSPACE:
            if self.mark is not None:
                self._delete_selection()
            elif self._position > 0:
                self._position -= 1
                self._layout.document.delete_text(self._position, self._position + 1)
                self._update()
        elif motion == MOTION_DELETE:
            if self.mark is not None:
                self._delete_selection()
            elif self._position < len(self._layout.document.text):
                self._layout.document.delete_text(self._position, self._position + 1)
        elif self._mark is not None and not select and \
            motion is not MOTION_COPY:
            self._mark = None
            self._layout.set_selection(0, 0)

        if motion == MOTION_LEFT:
            self.position = max(0, self.position - 1)
        elif motion == MOTION_RIGHT:
            self.position = min(len(self._layout.document.text), self.position + 1)
        elif motion == MOTION_UP:
            self.line = max(0, self.line - 1)
        elif motion == MOTION_DOWN:
            line = self.line
            if line < self._layout.get_line_count() - 1:
                self.line = line + 1
        elif motion == MOTION_BEGINNING_OF_LINE:
            self.position = self._layout.get_position_from_line(self.line)
        elif motion == MOTION_END_OF_LINE:
            line = self.line
            if line < self._layout.get_line_count() - 1:
                self._position = self._layout.get_position_from_line(line + 1) - 1
                self._update(line)
            else:
                self.position = len(self._layout.document.text)
        elif motion == MOTION_BEGINNING_OF_FILE:
            self.position = 0
        elif motion == MOTION_END_OF_FILE:
            self.position = len(self._layout.document.text)
        elif motion == MOTION_NEXT_WORD:
            pos = self._position + 1
            m = self._next_word_re.search(self._layout.document.text, pos)
            if not m:
                self.position = len(self._layout.document.text)
            else:
                self.position = m.start()
        elif motion == MOTION_PREVIOUS_WORD:
            pos = self._position
            m = self._previous_word_re.search(self._layout.document.text, 0, pos)
            if not m:
                self.position = 0
            else:
                self.position = m.start()

        self._next_attributes.clear()
        self._nudge()

    def _update(self, line=None, update_ideal_x=True):
        """Update the caret. This is used internally for the Entry widget.
        
        line - current line of the caret
        update_ideal_x - x coordinate of line is updated
        
        parameters: int, bool
        """

        if line is None:
            line = self._layout.get_line_from_position(self._position)
            self._ideal_line = None
        else:
            self._ideal_line = line
        x, y = self._layout.get_point_from_position(self._position, line)
        if update_ideal_x:
            self._ideal_x = x

        # x -= self._layout.view_x
        # y -= self._layout.view_y
        # add 1px offset to make caret visible on line start
        x += self._layout.x + 1

        y += self._layout.y + self._layout.height / 2

        font = self._layout.document.get_font(max(0, self._position - 1))
        self._list.position[:] = [x, y + font.descent, x, y + font.ascent]

        if self._mark is not None:
            self._layout.set_selection(min(self._position, self._mark), max(self._position, self._mark))

        self._layout.ensure_line_visible(line)
        self._layout.ensure_x_visible(x)


class Entry(Widget):
    """Entry widget to display user-editable text. This makes use of the
    pyglet.text.layout.IncrementalTextLayout and a modified version of its
    built-in caret.

    FIXME: caret not showing on line start
           make caret transparent or invisible instead of changing color
           caret glitching out on blinks at line end
    
    TODO
    1. Add rich text formatting (use pyglet.text.document.HTMLDocument)
    2. Add show feature for passwords
    3. Add copy, paste, select all, and more text features (COMPLETED)
    4. Add undo and redo features
    5. Enable updates for the layout for smoother performance. This raises
       AssertionError, one that has been seen before.

    Last updated: August 4th 2022
    """

    blinking = True
    index = 0
    length = 0
    max = MAX
    _validate = printable

    undo_stack = []
    redo_stack = []

    # Validations
    VALIDATION_LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    VALIDATION_UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    VALIDATION_LETTERS = VALIDATION_LOWERCASE + VALIDATION_UPPERCASE
    VALIDATION_DIGITS = "1234567890"
    VALIDATION_ADVANCED_DIGITS = "1234567890.+-*/^<>[]{}()!|"
    VALIDATION_PUNCTUATION = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    VALIDATION_WHITESPACE = " \t\n\r\v\f"
    VALIDATION_REGULAR = None

    def __init__(self, x, y, text="", font=default_font, color=BLACK):
        """Initialize the Entry. Typically a widget will push events
        automatically, but because there are custom named events, they have
        to be defined here.

        An Entry is a widget where text input can be returned. Typing into
        an Entry appends some text, which can be used for usernames,
        passwords, and more. Text can be removed by many keys.
        
        x - x coordinate of the Entry
        y - y coordinate of the Entry
        text - default text of the Entry
        font - font of the text in the Entry
        color - color of the text in the Entry

        properties:
            document - document of the IncrementalTextLayout
            layout - internal IncrementalTextLayout for efficient rendering
            caret - caret of the Entry
            image - image displayed to give the Entry a graphical look

            x - x coordinate of the Entry
            y - y coordinate of the Entry
            default - default text of the Entry (changing this has no effect)
            font - font of the Entry

            blinking - caret is visible or not visible
            
            length - length of the text in the Entry
            max - maximum amount of characters in the Entry

            text - displayed text of the Entry
            selection - selected text of the Entry
            layout_colors - layout colors of the Entry
            validate - validation of the characters in the Entry
            index - index of the caret (position)
            view - view vector of the Entry
        
        methods:
            blink - blink the caret and switch its visibility
            insert - insert some text in the Entry
            delete - delete some text from the Entry
        """

        self.document = decode_text(text)
        
        self.layout = IncrementalTextLayout(self.document, 190, 24)

        self.image = Image(entry_normal, x, y)
        self.caret = Caret(self.layout)

        Widget.__init__(self)

        self.x = x
        self.y = y
        self.default = text
        self.font = font

        self.document.set_style(0, len(text), dict(font_name=DEFAULT_FONT[0],
                                              font_size=DEFAULT_FONT[1],
                                              color=four_byte(color)))

        self.window.push_handlers(
            self.on_text,
            self.on_text_motion
        )

    def _get_text(self):
        """Return the text of the Entry.
        
        returns: str
        """

        return self.document.text

    def _set_text(self, text):
        """Set the text of the Entry.
        
        text - new text to be displayed. This can be a string or a tuple
        change_index - index is changed after text input. If True, the index
                       is set to the end of the Entry.
        
        parameters: str or tuple
        """

        if isinstance(text, Tuple):
            self.document.text = text[0]

            if text[1]:
                # Put the caret to the end
                self.index = self.length

            return
        
        self.document.text = text

    def _get_index(self):
        """Return the index of the current caret position within the
        document.
        
        returns: int
        """

        return self.caret.position
    
    def _set_index(self, index):
        """Set the index of the current caret position within the document.
        
        index - new index of the caret position
        
        parameters: int
        """

        self.caret.position = index
    
    def _get_selection(self):
        """Get the selection indices of the Entry, with the start and end as
        a tuple.
        
        (start, end)

        returns: tuple (int, int), (start, end)
        """

        return (
                self.layout.selection_start,
                self.layout.selection_end,
                self.text[
                    self.layout.selection_start : self.layout.selection_end
                ]
               )
    
    def _set_selection(self, selection):
        """Set the selection indices of the Entry, which are defined with
        the property layout_colors.
        
        selection - tuple of selection indices (start, end)
        
        parameters: tuple
        """

        self.caret.mark = selection[1]

        self.layout.selection_start = selection[0]
        self.layout.selection_end = selection[1]
        
    def _get_layout_colors(self):
        """Get the layout colors of the Entry. This will return a tuple of
        three colors defined by _set_layout_color. The selection background
        defaults to (46, 106, 197).

        (selection, caret, text)

        returns: tuple (list, list, list)
        """

        return (
                self.layout.selection_background_color,
                self.caret.color,
                self.layout.selection_color
                )

    def _set_layout_colors(self, colors):
        """Set the layout colors of the Entry.
        
        colors - tuple of three colors. The first item is the background
                color of the selection, while the second item is the caret
                color. The third item is the color of the text selected.
        
        parameters: tuple (selection, caret, text)
        """

        self.layout.selection_background_color = colors[0]
        self.layout.selection_color = colors[2]
        self.caret.color = colors[1]
    
    def _get_validate(self):
        """Get the validation of the Entry.
        
        returns: str
        """

        return self._validate
    
    def _set_validate(self, validate):
        """Set the validation of the Entry. This is a string containing all
        of the characters the user is able to type. Common charsets cam be
        found in the string module.
        
        validate - validation to set
        
        parameters: str
        """

        self._validate = validate
    
    def _get_view(self):
        """Get the view vector of the Entry.
        
        returns: tuple (x, y)
        """
        
        return (
                self.layout.view_x,
                self.layout.view_y
        )
    
    def _set_view(self, view):
        """Set the view of the Entry as a vector.
        
        view - vector of x and y views as a Point
        
        parameters: Point
        """

        self.layout.begin_update()

        self.layout.view_x = view.x
        self.layout.view_y = view.y

        self.layout.end_update()

    text = property(_get_text, _set_text)
    index = property(_get_index, _set_index)
    selection = property(_get_selection, _set_selection)
    layout_colors = property(_get_layout_colors, _set_layout_colors)
    validate = property(_get_validate, _set_validate)
    view = property(_get_view, _set_view)

    def blink(self, delta):
        """The caret toggles between white and black colors. This is called
        every 0.5 seconds, and only when the caret has focus.
        
        delta - delta time in seconds since the function was last called.
                This varies about 0.5 seconds give or take, because of
                calling delay, lags, and other inefficiencies.
        
        parameters: float
        """

        if self.caret.color == list(BLACK):
            self.caret.color = WHITE
        else:
            self.caret.color = BLACK
            
    def insert(self, index, text, change_index=True):
        """Insert some text at a given index one character after the index.

        >>> entry.text = "Hello!"
        >>> entry.insert(6, " world")
        >>> entry.text
        "Hello world!"

        "Hello world!"
              ^^^^^^
              678...

        index - index of the text addition
        text - text to be added
        change_index - index is updated to the end of the addition
        
        parameters: int, str
        """

        # self.text = insert(index, self.text, text)

        self.document._insert_text(index, text)

        if change_index:
            self.index = self.index + len(text)

    def delete(self, start, end):
        """Delete some text at a start and end index, one character after the
        start position and a character after the end position

        >>> entry.text = "Hello world!"
        >>> entry.delete(5, 10)
        >>> entry.text
        "Hello!"

        "Hello world!"
              ^^^^^^
              6... 11
        
        start - start of the text to be deleted
        end - end of the text to be deleted
        
        parameters: int, int
        """

        # self.text = delete(start, end, self.text)

        self.document._delete_text(start, end)
    
    def draw(self):
        """Draw the Entry. The layout is drawn with pyglet rendering.
        
        1. Image component
        2. Layout
        """

        self.image.draw()
        
        self.image.x = self.x
        self.image.y = self.y
        
        self.layout.width = 190

        try:
            self.layout.x = self.x - self.layout.width / 2 + 1
            self.layout.y = self.y - 5
        
            self.layout.anchor_x = LEFT
            self.layout.anchor_y = CENTER
        
        except: # Too many different errors
            pass
        
        with get_window().ctx.pyglet_rendering():
            self.layout.draw()

        self.component = self.image

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts.
        
        keys - key pressed
        modifiers - modifier pressed
        
        parameters: int (32-bit), int (32-bit)
        """
        
        if keys == SPACE:
            self.undo_stack.append(self.text)

        if modifiers & CONTROL:
            if keys == V:
                self.insert(self.index, clipboard_get(), change_index=True)
            elif keys == C:
                clipboard_append(self.selection[2])
            if keys == X:
                clipboard_append(self.selection[2])
                self.caret._delete_selection()
            elif keys == A:
                self.index = 0
                self.selection = (0, self.length, self.text)
            
    def on_focus(self):
        """The Entry has focus, activating events. This activates the caret
        and stops a few errors.
        """

        if self.text == self.default:
            self.text = ""
            self.index = 0
            
    def on_text(self, text):
        """The Entry has text input. The Entry adds text to the end.
        Internally, the Entry does a few things:
        
            - Remove all selected text
            - Update the caret position
            - Appends text to the end of the layout
        
        text - text inputed by the user

        parameters: str
        """

        if self.focus and \
            self.length < self.max:
            if self.validate:
                if text in self.validate:
                    self.caret.on_text(text)

                    return
            
            self.caret.on_text(text)

    def on_text_motion(self, motion):
        """The Entry has caret motion. This can be moving the caret's
        position to the left with the Left key, deleting a character
        previous with the Backspace key, and more.
        
        motion - motion used by the user. This can be one of many motions,
                 defined by keyboard constants found in the keyboard module.

                 MOTION_LEFT                MOTION_RIGHT
                 MOTION_UP                  MOTION_DOWN                
                 MOTION_NEXT_WORD           MOTION_PREVIOUS_WORD
                 MOTION_BEGINNING_OF_LINE   MOTION_END_OF_LINE
                 MOTION_NEXT_PAGE           MOTION_PREVIOUS_PAGE
                 MOTION_BEGINNING_OF_FILE   MOTION_END_OF_FILE
                 MOTION_BACKSPACE           MOTION_DELETE
                 MOTION_COPY                MOTION_PASTE

                 You can get the list of all text motions with
                 motions_string() in the keyboard module.
                 
        parameters: int (32-bit)
        """

        if self.focus:
            try:
                self.caret.on_text_motion(motion)
            except AssertionError: # assert self.glyphs
                pass

            self.index = self.caret.position

    def on_text_select(self, motion):
        """Some text in the Entry is selected. When this happens, the
        selected text will have a blue background to it. Moving the caret
        with a text motion removes the selection (does not remove the text).

        NOTE: this is not called with caret mouse selections. See on_press.
        
        motion - motion used by the user. These can be made with the user.

                 SHIFT + LEFT               SHIFT + RIGHT
                 SHIFT + UP                 SHIFT + DOWN
                 CONTROL + SHIFT + LEFT     CONTROL + SHIFT + RIGHT
        
        parameters: int (32-bit)
        """

        if self.focus:
            self.caret.on_text_motion_select(motion)

            self.index = self.caret.position

    def on_press(self, x, y, buttons, modifiers):
        """The Entry is pressed. This will do a number of things.
            
            - The caret's position is set to the nearest character.
            - If text is selected, the selection will be removed.
            - If the Shift key is being held, a selection will be created
              between the current caret index and the closest character to
              the mouse.
            - If two clicks are made within 0.5 seconds (double-click), the
              current word is selected.
            - If three clicks are made within 0.5 seconds (triple-click), the
              current paragraph is selected.
        
        x - x coordinate of the press
        y - y coordinate of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        _x, _y = x - self.layout.x, y - self.layout.y
        
        self.caret.on_mouse_press(_x, _y, buttons, modifiers)

    def on_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse when it was pressed. This can
        create selections.
        
        x - x coordinate of the current position
        y - y coordinate of the current position
        dx - movement in x vector from the last position
        dy - movement in y vector from the last position
        
        buttons - buttons that were dragged with the mouse
        modifiers - modifiers being held down
        
        parameters: int, int, float, float, int (32-bit), int (32-bit)
        """

        _x, _y = x - self.layout.x, y - self.layout.y

        if self.press:
            self.caret.on_mouse_drag(_x, _y, dx, dy, buttons, modifiers)

            self.index = self.caret.position
        else:
            if self.focus:
                self.caret.on_mouse_drag(_x, _y, dx, dy, buttons, modifiers)

                self.index = self.caret.position
        
    def update(self):
        """Update the caret and Entry. This schedules caret blinking and
        keeps track of focus.
        """

        self.length = len(self.text)
        
        if self.focus:
            if not self.blinking:
                schedule(self.blink, ENTRY_BLINK_INTERVAL)

                self.blinking = True
            
        else:
            self.index = 0
            self.blinking = False

            unschedule(self.blink)


class Shape(Widget):
    """Primitive drawing shape"""

    def __init__(self):
        Widget.__init__(self)

    def delete(self):
        self.shape.delete()

    def draw(self):
        with self.window.ctx.pyglet_rendering():
            self.shape.draw()
    
    def update(self):
        self.shape.opacity = self.alpha
        self.shape.rotation = self.angle


_Circle = Circle
_Ellipse = Ellipse
_Sector = Sector
_Line = Line
_Triangle = Triangle
_Star = Star
_Polygon = Polygon
_Arc = Arc


class Rectangle(Shape):

    def __init__(self, x, y, width, height, border=1,
                 colors=(WHITE, BLACK), label=None):
        
        self.shape = BorderedRectangle(
                            x, y, width, height,
                            border, colors[0], colors[1]
                        )

        Shape.__init__(self) # Do this after defining self.shape

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border = border
        self.colors = colors
        self.label = label

    def update(self):
        self.shape.x = self.x - self.width / 2
        self.shape.y = self.y - self.height / 2
        self.shape.width = self.width
        self.shape.height = self.height
        self.shape.color = self.colors[0]
        self.shape.border_color = self.color[1]
        self.shape.border = self.border

        if self.label:
            self.label.x = self.x + self.width / 2
            self.label.y = self.y + self.height / 2


class Circle(Shape):

    def __init__(self, x, y, radius, segments=5, color=BLACK):
        self.shape = _Circle(x, y, radius, segments, color)

        Shape.__init__(self)

        self.x = x
        self.y = y
        self.radius = radius
        self.segments = segments
        self.color = color

    def update(self):
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.radius = self.radius
        self.shape.segments = self.segments
        self.shape.color = self.color


class Ellipse(Shape):

    def __init__(self, x, y, a, b, color=BLACK):
       self.shape = _Ellipse(x, y, a, b, color)

       Shape.__init__(self)

       self.x = x
       self.y = y
       self.a = a
       self.b = b
       self.color = color
    
    def update(self):
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.a = self.a
        self.shape.b = self.b
        self.shape.color = self.color


Oval = Ellipse


class Sector(Shape):

    def __init__(self, x, y, radius, segments=None,
                 angle=tau, start=0, color=BLACK):
    
        self.shape = _Sector(x, y, radius, segments, angle, start, color)

        Shape.__init__(self)

        self.x = x
        self.y = y
        self.radius = radius
        self.segments = segments
        self.rotation = angle
        self.start = start
        self.color = color

    def update(self):
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.radius = self.radius
        self.shape.segments = self.segments
        self.shape.rotation = self.angle
        self.shape.start = self.start
        self.shape.color = self.color


class Line(Shape):

    def __init__(self, x1, y1, x2, y2, width=1, color=BLACK):
        self.shape = _Line(x1, y1, x2, y2, width, color)

        Shape.__init__(self)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width
        self.color = color
    
    def update(self):
        self.shape.x1 = self.x1
        self.shape.y1 = self.y1
        self.shape.x2 = self.x2
        self.shape.y2 = self.y2
        self.shape.width = self.width
        self.shape.color = self.color


class Triangle(Shape):

    def __init__(self, x1, y1, x2, y2, x3, y3, color=BLACK):
        self.shape = _Triangle(x1, y2, x2, y2, x2, y2, color)

        Shape.__init__(self)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.color = color

    def update(self):
        self.shape.x = self.x1
        self.shape.y = self.y1
        self.shape.x2 = self.x2
        self.shape.y2 = self.y2
        self.shape.x3 = self.x3
        self.shape.y3 = self.y3
        self.shape.color = self.color


class Star(Shape):

    def __init__(self, x, y, outer, inner,
                 spikes=5, rotation=0, color=BLACK):

        self.shape = _Star(x, y, outer, inner, spikes, rotation, color)

        Shape.__init__(self)

        self.x = x
        self.y = y
        self.outer = outer
        self.inner = inner
        self.spikes = spikes
        self.rotation = rotation
        self.color = color

    def update(self):
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.outer_radius = self.outer
        self.shape.inner_radius = self.inner
        self.shape.num_spikes = self.spikes
        self.shape.rotation = self.rotation
        self.shape.color = self.color


class Polygon(Shape):
    
    def __init__(self, *coordinates, color=BLACK):
        self.shape = _Polygon(*coordinates, color)

        Shape.__init__(self)

        self.coordinates = list(coordinates)
        self.color = color
    
    def update(self):
        self.shape.coordinates = self.coordinates
        self.shape.color = self.color


class Arc(Shape):

    def __init__(self, x, y, radius, segments=None,
                 angle=tau, start=0, closed=False, color=BLACK):
        self.shape = _Arc(x, y, radius, segments, angle, start, closed, color)
        
        Shape.__init__(self)

        self.x = x
        self.y = y
        self.radius = radius
        self.segments = segments
        self.rotation = angle
        self.start = start
        self.closed = closed
        self.color = color
    
    def update(self):
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.radius = self.radius
        self.shape.segments = self.segments
        self.shape.angle = self.rotation
        self.shape.start = self.start
        self.shape.closed = self.closed
        

class MyWindow(Window):
    def __init__(self, title, width, height):
        Window.__init__(
            self, width, height, title, style=Window.WINDOW_STYLE_DIALOG
        )

        from file import blank1, blank2
        from pyglet.image import load

        self.container = Container()

        self.set_icon(load(blank1), load(blank2))

        self.label = Label(
            "<b>Bold</b, <i>italic</i>, and <u>underline</u> text.",
            10,
            60,
            multiline=True,
            width=500)
        
        self._label = Label(
            None,
            10,
            80)

        self.button = Button(
            "Click me!",
            250,
            250,
            command=self.click
            )

        self.toggle = Toggle(
            "Show fps",
            250,
            350)
        
        self.slider = Slider(
            None,
            250,
            300)

        self.entry = Entry(
            250,
            160,
            )
        
        self.circle = Circle(
            100, 
            150,
            50,
            segments=100,
            color=BLUE_YONDER)
        
        self.container.append(self.label)
        self.container.append(self._label)
        self.container.append(self.button)
        self.container.append(self.toggle)
        self.container.append(self.slider)
        self.container.append(self.entry)
        self.container.append(self.circle)

        self.button.bind(ENTER)

        self.background_color = WHITE

    def click(self):
        self._label.text = self.entry.text

    def on_draw(self):
        self.clear()
        self.container.draw()

        if self.toggle.value:
            self.label.text = f"{int(get_fps())} fps"
        else:
            self.label.text = "<b>Bold</b>, <i>italic</i>, and <u>underline</u> text in HTML"

        self.slider.text = str(int(self.slider.value))


if __name__ == "__main__":
    window = MyWindow(" ", 500, 400)

    from pyglet.app import run
    run(1/120)
