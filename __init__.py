"""GUI interface and widgets. Documentation and details can be found at:
https://github.com/eschan145/Armies/blob/main/README.md.

More than meets the eye in this example. To see all features, look at the source
code of each widget. This includes several different types of interactive
widgets and displays an example at the end. It also includes API for creating
your own widgets, which are quite easy to do.

Several widgets are provided to use. These include Image, Label, Button,
Slider, Toggle, Entry, Combobox, and various shapes. Like most projects based
off pyglet, in this GUI toolkit, all widgets subclass a base widget class,
which dispatches events to them.

This uses the awesome pyglet and arcade libraries, which are still active and
working today. Arcade's website is https://arcade.academy/, while pyglet's is
https://pyglet.org/.

Contributions are welcome. Visit my Github respository at
https://github.com/eschan145/Armies. From there, you can submit pull requests
or chat in discussions.

Code and graphics by Ethan Chan

GitHub: eschan145
Discord: EthanC145

Contact me at esamuelchan@gmail.com
"""

from cmath import tau
from html import entities
from html.parser import HTMLParser
from string import printable
from tkinter import Tk
from typing import Tuple
from webbrowser import open_new

from arcade import (PointList, ShapeElementList, Sprite, SpriteList, Window,
                    create_rectangle_filled, create_rectangle_outline,
                    draw_rectangle_outline, enable_timings, get_fps,
                    get_window, load_texture, run, schedule, unschedule)
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch
from pyglet.image import load
from pyglet.shapes import (Arc, BorderedRectangle, Circle, Ellipse, Line,
                           Polygon, Sector, Star, Triangle)
from pyglet.text import DocumentLabel, HTMLLabel, decode_text
from pyglet.text.caret import Caret
from pyglet.text.formats.html import (_block_containers, _block_elements,
                                      _metadata_elements, _parse_color,
                                      _whitespace_re)
from pyglet.text.formats.structured import (ImageElement, OrderedListBuilder,
                                            StructuredTextDecoder,
                                            UnorderedListBuilder)
from pyglet.text.layout import IncrementalTextLayout
from pymunk import shapes

from color import (BLACK, BLUE_YONDER, COOL_BLACK, DARK_GRAY, DARK_SLATE_GRAY,
                   RED, WHITE, four_byte)
from constants import (BOTTOM, CENTER, DEFAULT_FONT, DEFAULT_FONT_FAMILY,
                       DEFAULT_FONT_SIZE, DISABLE_ALPHA, DOUBLE,
                       ENTRY_BLINK_INTERVAL, KNOB_HOVER_SCALE, LEFT, MULTIPLE,
                       RIGHT, SINGLE, SLIDER_VELOCITY, TOGGLE_FADE,
                       TOGGLE_VELOCITY, TOP, Y)
from file import (combobox_bottom_normal, combobox_middle_normal,
                  combobox_top_normal, entry_normal, knob, none,
                  slider_horizontal, toggle_false, toggle_false_hover,
                  toggle_true, toggle_true_hover, widgets)
from geometry import Point, get_distance
from key import (ALT, CONTROL, ENTER, KEY_LEFT, KEY_RIGHT, MOTION_BACKSPACE,
                 MOTION_BEGINNING_OF_FILE, MOTION_BEGINNING_OF_LINE,
                 MOTION_COPY, MOTION_DELETE, MOTION_DOWN, MOTION_END_OF_FILE,
                 MOTION_END_OF_LINE, MOTION_LEFT, MOTION_NEXT_WORD,
                 MOTION_PREVIOUS_WORD, MOTION_RIGHT, MOTION_UP,
                 MOUSE_BUTTON_LEFT, SHIFT, SPACE, TAB, A, C, Keys, V, X)

MAX = 2 ** 32

enable_timings()

clipboard = Tk()
clipboard.withdraw()

_widgets = SpriteList()
batch = Batch()
widgets_list = SpriteList()


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
    """Insert some text to a string given an index. This was originally used for
    the entry widget but was deceprated when we found a faster and more
    efficient way to insert text.

    index - index of the text addition
    text - string to be edited
    add - new text to be inserted

    parameters: int, str, str
    returns: str
    """

    return text[:index] + add + text[index:]

def delete(start, end, text):
    """Delete some text to a string given an index. This was originally used for
    the entry widget but was deceprated when we found a faster and more
    efficient way to delete text.

    start - start index of the text removal
    end - end index of the text removal
    text - string to be edited

    parameters: int, int, str
    returns: str
    """

    if len(text) > end:
        text = text[0: start:] + text[end + 1::]
    return text


class HTMLDecoder(HTMLParser, StructuredTextDecoder):
    """A custom HTML decoder based off pyglet's built-in one. This has limited
    functionality but still feature-rich.
    """

    default_style = {
        "font_name" : "Montserrat",
        "font_size" : 12,
        "margin_bottom" : "12pt",
        "bold" : False,
        "italic" : False,
    }

    font_sizes = {
        1 : 8,
        2 : 10,
        3 : 12,
        4 : 14,
        5 : 18,
        6 : 24,
        7 : 48
    }

    def decode_structured(self, text, location):
        """Decode some structured text and convert it to the pyglet attributed
        text (vnd.pyglet-attributed).

        text - given HTML text to be decoded into pyglet attributed text
        location - location of images and filepaths for the document

        parameters: str, str
        """

        self.location = location
        self._font_size_stack = [3]
        self.list_stack.append(UnorderedListBuilder({}))
        self.strip_leading_space = True
        self.block_begin = True
        self.need_block_begin = False
        self.element_stack = ["_top_block"]
        self.in_metadata = False
        self.in_pre = False

        # Set default style

        self.push_style("_default", self.default_style)

        self.feed(text)
        self.close()

    def get_image(self, filename):
        """Get an image from a filename. This uses the location.

        filename - filename of image

        parameters: str
        """

        return load(filename, file=self.location.open(filename))

    def prepare_for_data(self):
        """Prepare the document for insertion of HTML text.
        """

        if self.need_block_begin:
            self.add_text("\n")
            self.block_begin = True
            self.need_block_begin = False

    def handle_data(self, data):
        """Handle HTML data.

        data - HTML data
        """

        if self.in_metadata:
            return

        if self.in_pre:
            self.add_text(data)
        else:
            data = _whitespace_re.sub(" ", data)
            if data.strip():
                self.prepare_for_data()
                if self.block_begin or self.strip_leading_space:
                    data = data.lstrip()
                    self.block_begin = False
                self.add_text(data)
            self.strip_leading_space = data.endswith(" ")

    def handle_starttag(self, tag, case_attributes):
        """Handle the start of tags for all HTML elements. This creates a map
        of all the elements and pushes its style to a pyglet structured text
        decoder. They may be upper or lower case.

        Pyglet uses a subset of HTML 4.01 transitional.

        TODO: make code blocks have a gray background, keyboard blocks with a
              glowing gray background

        The following elements are currently supported.

        ALIGN B BLOCKQUOTE BR CODE DD DIR DL EM FONT H1 H2 H3 H4 H5 H6 I IMG
        KBD LI MENU OL P PRE Q STRONG SUB SUP U UL VAR

        The mark (bullet or number) of a list item is separated from the body
        of the list item with a tab, as the pyglet document model does not
        allow out-of-stream text. This means lists display as expected, but
        behave a little oddly if edited.

        No style elements are currently supported.

        A description of each tag is found below.

        ALIGN - alignment of the text. This can be LEFT, CENTER, or RIGHT.
        B - bold or heavy text. This has no parameters, and is defined in
            Markdown as two asterisks (**). Alias of <strong>.
        BLOCKQOUTE - a quote of some text. Later, a line drawn on the left side
                     may be implemented. The left margin is indented by 60
                     pixels, but can be changed by specifying a padding
                     parameter. In Markdown, this is a greater than equal sign,
                     with the level on the number of signs.
        BR - a line break. This draws a horizontal line below the text.
        CODE - a code block. This is displayed as ` for single-line code and
               ``` for multiline code blocks in Markdown. This is an alias for
               <pre>
        DD - description, definition, or value for a item
        DIR - unordered list. This takes a type parameter, either CIRCLE or
              SQUARE. It defaults to a bullet point. Alias for <ul> and <menu>.
        DL - description list. This just sets the bottom margin to nothing.
        EM - italic or slanted text. This has no parameters. Alias for <i> and
             <var>.
        FONT - font and style of the text. It takes several parameters.
               family       font family of the text. This must be a pyglet
                            loaded font.
               size         size changes of the text. If negative the text will
                            shrink, and if positive the text will be enlarged.
                            If not specified the text size will be 3.
               real_size    actual font size of the text. This only accepts
                            positive values.
               color        font color of the text in RGBA format

        H1 - largest HTML heading. This sets the font size to 24 points. All
             headings except <h6> are bold.
        H2 - second largest HTML heading. This sets the font size to 18 points.
        H3 - third largest HTML heading. This sets the font size to 16 points.
        H4 - fourth largest HTML heading. This sets the font size to 14 points.
        H5 - fifth largest HTML heading. This sets the font size to 12 points.
        H6 - a copy of <h5>, but with italic instead of bold text

        I - italic or slanted text. This has no parameters. Alias for <em> and
            <var>.
        IMG - display an image. This takes several parameters.
              filepath      filepath of the image. This is not a loaded image.
              width         width of the image. This must be set to a value
                            greater than 0, or the image will not be rendered.
              height        height of the image. This must be set to a value
                            greater than 0, or the image will not be rendered.
        KBD - display keyboard shortcut
        LI - display a list item. This should be inserted in a ordered or
             unordered list, like this.

             <ul> My special list
                 <li> My first list item </li>
                 <li> My second list item </li>
             </ul>

        MENU - unordered list. This takes a type parmeter, either CIRCLE or
               SQUARE. It defaults to a bullet point. Alias for <dir> and <ul>.
        OL - ordered list. Instead of having symbols, this uses sequential
             titles. Parameters and options are listed below.
             start          start title of ordered list. (int)
             format         list format. Pyglet's ordered list supports
                            1       Decimal arabic (1, 2, 3)
                            a       Lowercase alphanumeric (a, b, c)
                            A       Uppercase alphanumeric (A, B, C)
                            i       Lowercase roman (i, ii, i)
                            I       Uppercase roman (I, II, III)

                            These values can contain prefixes and suffixes,
                            like "1.", "(1)", and so on. If the format is
                            invalid a question mark will be used instead.
        P - paragraph. This is different that just plain HTML text, as it will
            be formatted to the guidelines of a paragraph. This takes a align
            parameter, either LEFT, CENTER, or RIGHT. Defaults to LEFT.
        PRE - a code block. This is displayed as ` for single-line code and
              ``` for multiline code blocks in Markdown. This is an alias to
              <code>
        Q - inline quotation element. This adds formal quotation marks around
            enclosed text. NOTE: not a regular ".
        STRONG - bold or heavy text. This has no parameters, and is defined in
                 Markdown as two asterisks (**). Alias of <b>
        SUB - subscript text. Enclosed text is offset by points given in the
              baseline parameter. This has two parameters.
              size          size decrement of the enclosed text. This is the
                            amount the text is leveled down.
              baseline      offset of the enclosed text. This should be
                            negative. Defaults to -3 points.
        SUP - superscript text. Enclosed text is offset by points given in the
              baseline parameter. This has two parameters.
              size          size increment of the enclosed text. This is the
                            amount the text is leveled up.
              baseline      offset of the enclosed text. This should be
                            positive. Defaults to 3 points.
        U - underlined text. This can take an optional color argument for the
            color of the underline. If not specified this defaults to BLACK.
        UL - unordered list. This takes a type parameter, either CIRCLE or
             SQUARE. It defaults to a bullet point. Alias for <dir> and<menu>.
        VAR -  italic or slanted text. This has no parameters. Alias for <i>
               and <em>.
        """

        if self.in_metadata:
            return

        element = tag.lower()
        attributes = {}

        for key, value in case_attributes:
            attributes[key.lower()] = value

        if element in _metadata_elements:
            self.in_metadata = True

        elif element in _block_elements:
            # Pop off elements until we get to a block container

            while self.element_stack[-1] not in _block_containers:
                self.handle_endtag(self.element_stack[-1])

            if not self.block_begin:
                self.add_text("\n")

                self.block_begin = True
                self.need_block_begin = False

        self.element_stack.append(element)

        style = {}

        if element in ("b", "strong"):
            style["bold"] = True

        elif element in ("i", "em", "var"):
            style["italic"] = True

        elif element in ("tt", "code", "kbd"):
            style["font_name"] = "Courier New"

        elif element == "u":
            color = self.current_style.get("color")

            if color is None:
                color = attributes.get("color") or [0, 0, 0, 255]

            style["underline"] = color

        elif element == "font":
            if "family" in attributes:
                style["font_name"] = attributes["family"].split(",")

            if "size" in attributes:
                size = attributes["size"]

                try:
                    if size.startswith("+"):
                        size = self._font_size_stack[-1] + int(size[1:])

                    elif size.startswith("-"):
                        size = self._font_size_stack[-1] - int(size[1:])

                    else:
                        size = int(size)

                except ValueError:
                    size = 3

                self._font_size_stack.append(size)

                if size in self.font_sizes:
                    style["font_size"] = self.font_sizes.get(size, 3)

            elif "real_size" in attributes:
                size = int(attributes["real_size"])

                self._font_size_stack.append(size)
                style["font_size"] = size

            else:
                self._font_size_stack.append(self._font_size_stack[-1])

            if "color" in attributes:
                try:
                    style["color"] = _parse_color(attributes["color"])

                except ValueError:
                    pass

        elif element == "sup":
            size = self._font_size_stack[-1] - (attributes.get("size") or 1)

            style["font_size"] = self.font_sizes.get(size, 1)
            style["baseline"] = attributes.get("baseline") or "3pt"

        elif element == "sub":
            size = self._font_size_stack[-1] - (attributes.get("size") or 1)

            style["font_size"] = self.font_sizes.get(size, 1)
            style["baseline"] = attributes.get("baseline") or "-3pt"

        elif element == "h1":
            style["font_size"] = 24
            style["bold"] = True

        elif element == "h2":
            style["font_size"] = 18
            style["bold"] = True

        elif element == "h3":
            style["font_size"] = 16
            style["bold"] = True

        elif element == "h4":
            style["font_size"] = 14
            style["bold"] = True

        elif element == "h5":
            style["font_size"] = 12
            style["bold"] = True

        elif element == "h6":
            style["font_size"] = 12
            style["italic"] = True

        elif element == "br":
            self.add_text(u"\u2028")

            self.strip_leading_space = True

        elif element == "p":
            if attributes.get("align") in ("left", "center", "right"):
                style["align"] = attributes["align"]

        elif element == "align":
            style["align"] = attributes.get("type")

        elif element == "pre":
            style["font_name"] = "Courier New"
            style["margin_bottom"] = 0

            self.in_pre = True

        elif element == "blockquote":
            padding = attributes.get("padding") or 60

            left_margin = self.current_style.get("margin_left") or 0
            right_margin = self.current_style.get("margin_right") or 0

            style["margin_left"] = left_margin + padding
            style["margin_right"] = right_margin + padding

        elif element == "q":
            self.handle_data(u"\u201c")

        elif element == "ol":
            try:
                start = int(attributes.get("start", 1))
            except ValueError:
                start = 1

            format = attributes.get("format", "1") + "."

            builder = OrderedListBuilder(start, format)

            builder.begin(self, style)
            self.list_stack.append(builder)

        elif element in ("ul", "dir", "menu"):
            type = attributes.get("type", "disc").lower()

            if type == "circle":
                mark = u"\u25cb"
            elif type == "square":
                mark = u"\u25a1"
            else:
                if type:
                    mark = type
                else:
                    mark = u"\u25cf"

            builder = UnorderedListBuilder(mark)

            builder.begin(self, style)
            self.list_stack.append(builder)

        elif element == "li":
            self.list_stack[-1].item(self, style)
            self.strip_leading_space = True

        elif element == "dl":
            style["margin_bottom"] = 0

        elif element == "dd":
            left_margin = self.current_style.get("margin_left") or 0
            style["margin_left"] = left_margin + 30

        elif element == "img":
            image = self.get_image(attributes.get("filepath"))

            if image:
                width = attributes.get("width")

                if width:
                    width = int(width)

                height = attributes.get("height")

                if height:
                    height = int(height)

                self.prepare_for_data()

                self.add_element(ImageElement(image, width, height))
                self.strip_leading_space = False

        self.push_style(element, style)

    def handle_endtag(self, tag):
        """Handle the end tags for the HTML document. They may be upper or lower case.
        """

        element = tag.lower()

        if element not in self.element_stack:
            return

        self.pop_style(element)

        while self.element_stack.pop() != element:
            pass

        if element in _metadata_elements:
            self.in_metadata = False
        elif element in _block_elements:
            self.block_begin = False
            self.need_block_begin = True

        if element == "font" and len(self._font_size_stack) > 1:
            self._font_size_stack.pop()
        elif element == "pre":
            self.in_pre = False
        elif element == "q":
            self.handle_data(u"\u201d")
        elif element in ("ul", "ol"):
            if len(self.list_stack) > 1:
                self.list_stack.pop()

    def handle_entityref(self, name):
        """Handle entity references from the HTML document.
        """

        if name in entities.name2codepoint:
            self.handle_data(chr(entities.name2codepoint[name]))

    def handle_charref(self, name):
        """Handle character references from the HTML document. This is used
        internally for the pyglet document formatter.
        """

        name = name.lower()

        try:
            if name.startswith("x"):
                self.handle_data(chr(int(name[1:], 16)))
            else:
                self.handle_data(chr(int(name)))
        except ValueError:
            pass


class HTMLLabel(DocumentLabel):
    """HTML formatted text label.

    A subset of HTML 4.01 is supported.  See `pyglet.text.formats.html` for
    details.
    """

    def __init__(self, text='', location=None,
                 x=0, y=0, width=None, height=None,
                 anchor_x='left', anchor_y='baseline',
                 multiline=False):
        """Create a label with an HTML string.

        :Parameters:
            `text` : str
                HTML formatted text to display.
            `location` : `Location`
                Location object for loading images referred to in the
                document.  By default, the working directory is used.
            `x` : int
                X coordinate of the label.
            `y` : int
                Y coordinate of the label.
            `width` : int
                Width of the label in pixels, or None
            `height` : int
                Height of the label in pixels, or None
            `anchor_x` : str
                Anchor point of the X coordinate: one of ``"left"``,
                ``"center"`` or ``"right"``.
            `anchor_y` : str
                Anchor point of the Y coordinate: one of ``"bottom"``,
                ``"baseline"``, ``"center"`` or ``"top"``.
            `multiline` : bool
                If True, the label will be word-wrapped and render paragraph
                and line breaks.  You must also set the width of the label.
        """

        self._text = text
        self._location = location

        document = HTMLDecoder().decode(text, location)

        DocumentLabel.__init__(self, document, x, y, width, height,
                               anchor_x, anchor_y, multiline, None, batch,
                               None)

    def _get_text(self):
        """HTML formatted text of the label.

        :type: str
        """
        return self._text

    def _set_text(self, text):
        if text == self._text:
            return

        self._text = text

        self.document = HTMLDecoder().decode(text)

    text = property(_get_text, _set_text)


class WidgetsError(Exception):
    """Widgets error. When creating custom widgets, this can be invoked. Only
    use this if you need to, like if it is going to cause something to hang or
    crash, or it raises an unhelpful error. Making this unnecessary will be
    annoying in some scenarios. If the user absolutely wants to do something
    and this error keeps on being raised, this is aggravating and he will have
    to edit the source code.
    """


class Font:
    """An object-oriented Font."""

    def __init__(self,
                 family=DEFAULT_FONT_FAMILY,
                 size=DEFAULT_FONT_SIZE
                ):

        """Initialize an object-oriented Font. This is an experimental
        feature developed on August 4th 2022 and has no effect.

        family - family of the font (style)
        size - size of the font (not in pixels)

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
    """"Container class to draw and update widgets. One current problem is that
    each widget in its widget spritelist is being drawn every frame
    individually. Though it is much faster to draw in a batch, this has not
    been implemented.

    A container is already created. You shouldn't usually need to subclass this
    or create an instance. You can access the container by getting the
    container variable. It is already created. Containers have several useful
    properties, like getting the current application focus and the list of
    created widgets. You can exit the application (if you are going to create a
    new view) by calling the exit function. You can also call draw_bbox or its
    aliases to draw each bounding box for each widget.
    """

    focus = None
    enable = True

    widgets = []

    _window = None

    def __init__(self, window=None, shadow=False):
        """Initialize a container. You shouldn't usually need to create an
        instance of this class directly.
        """

        EventDispatcher.__init__(self)

    def _get_window(self):
        """Get the current pyglet window of the container.

        returns: Window
        """

        return self._window

    def _set_window(self, window):
        """Set the current pyglet window of the container.

        window - window of the container

        parameters: Window
        """

        self._window = window or get_window()

        self._window.push_handlers(self)

    window = property(_get_window, _set_window)

    def append(self, widget):
        """Add a widget to the drawing list. Unfortunately each widget must be
        drawn individually instead of drawing them in a batch, which really
        slows down performance with hundreds of widgets. This is called
        internally for all widgets. If you are not going to subclass the base
        widget class, you will need to do this manually.

        This asserts that a current window is open.

        widget - widget to add to the list

        parameters: Widget
        """

        assert self.window, (
            "No window is active. It has not been created yet, or it was"
            "closed. Be sure to set the window property of the container before"
            "adding any widgets."
        )

        if not isinstance(widget, Image):
            self.widgets.append(widget)

        widget.container = self

    def draw(self):
        """Draw the container's widgets. This should be manually called in the
        draw function of your application.
        """

        widgets_list.draw()

        [widget.draw() for widget in self.widgets]

        with self.window.ctx.pyglet_rendering():
            batch.draw()

            # A shadow effect not in progress anymore

            # Interesting feature:
            # Press Control + slash when on the line with "shade = 1"
            # The text "shade" will turn light green for a second.

            # shade = 1

            # if self.shadow:
            #     for i in range(1, 100):
            #         shade += 0.01
            #         print(scale_color(self.shadow, int(shade)))
            #         draw_rectangle_outline(widget.x, widget.y,
            #                                 widget.width + 1, widget.height + 1,
            #                                 RED)

    def draw_bbox(self, width=1, padding=0):
        """Draw the bounding box of each widget in the list. The drawing is
        cached in a ShapeElementList so it won't take up more time. This can
        also be called draw_hitbox or draw_hit_box.

        width - width of the bounding box outline
        padding - padding around the widget
        """

        [widget.draw_bbox(width, padding) for widget in self.widgets]

    draw_hitbox = draw_bbox # Alias
    draw_hit_box = draw_bbox

    def exit(self):
        """Exit the event sequence and delete all widgets. This sets its
        enable property to False.
        """

        [widget.delete() for widget in self.widgets]

        self.enable = False

    def on_key_press(self, keys, modifiers):
        """A key is pressed. This is used to detect focus change by pressing
        Tab and Shift-Tab."""

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

            for widget in self.widgets:
                if not widget == self.focus:
                    widget.focus = False


container = Container()


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
    """Create a user interface GUI widget. This is a high-level class, and is
    not suitable for very complex widgets. It comes with built-in states,
    which can be accessed just by getting its properties. Dispatching events
    makes subclassing a widget and creating your own very easy.

    Widgets can have components, which are essentially smaller, secondary
    widgets that are inside the widget. For example, a button widget has a
    Label and an Image for components. A widget can have a main component,
    which takes the hitbox used for detecting states. For a button widget the
    main component would be the Image.

    Plenty of things are built-in here. For example, you can access the
    current window just by using the window property. Or the key state handler
    with the key property. You can draw the hit box of a widget for debugging,
    and performance is not lost because the drawing is cached. When removing a
    widget, use its delete function.

    There are dozens and dozens of properties for the widget. You can add an
    arcade Shape to its ShapeElementList, in the shapes property. Key state
    handlers are aleady built-in.

    You can access the widget's state by properties. Several built-in states
    are supported: normal, hover, press, disable, and focus. A disabled widget
    cannot have focus. It is highly not recommended to change any of these
    properties, as these may lead to drawing glitches.

    TODO: of course, there are many enhancements and other things that need to
          be worked on for the built-in widgets. If you would like to work on
          these post your enhancements in the discussions.

          https://github.com/eschan145/Armies/discussions/1

        1. Adding left, right, top, and bottom properties to widgets. This has
           been implemented in arcade sprites and should be for this too. It
           can be useful for enhanced positioning.
           - Create an _set_coords() function that is called whenever border
             coordinate properties are modified
           - Add setting properties for each widget. This is not recommended
             because it's a hassle to code and will take up more space.
           - Make functions like set_border_coords

        2. Move documentation from setters to getters for properties
    """

    def __init__(self, widgets=(), image=none, scale=1.0, frame=None):
        """
        Here's an example of a widget. This _colorchooser dispatches events, so
        a widget that subclasses it can use it.

        >>> class _Colorchooser(Widget):

                def __init__(self):
                    Widget.__init__(self)

                def on_press(self, x, y, buttons, modifiers):
                    color = self.get_color_from_pos(x, y)
                    self.dispatch_event("on_color_pick", color)

                def get_color_from_pos(self, x, y):
                    # Get a color from x, y
                    pass

        >>> _Colorchooser.register_event_type("on_color_pick")

        On lines 1-5 we create and initialize the widget. An event is
        dispatched by the widget called on_press when the widget is pressed.
        This _colorchooser widget then dispatches an event, called
        "on_color_pick", with its parameters listed beside it. At the end of
        defining the widget you have to register it, so we do that in the last
        line. This just confirms to pyglet that we're creating an event.

        Now, the actual colorchooser would look like this:

        >>> class Colorchooser(_Colorchooser):

                def __init__(self):
                    _Colorchooser.__init__(self)

                def on_color_pick(self, color):
                    print("Color picked: ", color)
        _______________________________________________________________

        widgets - widgets and components to be added. If you are creating
                components, add them before initializing the widget.
        image - image to be displayed. Use this only for defining an image
                widget, though one is already pre-defined.
        scale - scale of the widget. This has been deceprated, as setting this
                to a value different that one will mess up the widget's bbox
        frame - not yet implemented. This is supposed to have a frame widget,
                which stores multiple widgets. It's similar to tkinter's Frame.

        parameters:
            widgets: tuple
            image - str (filepath) or arcade Texture
        """

        Sprite.__init__(self, image, scale)

        self.frame = frame or Frame(0, 0)

        self.frame.append(self)

        self.hover = False
        self.press = False
        self.disable = False

        self.widgets = widgets

        self.drag = False

        self.focus = False

        self.component = None
        self.container = None

        self._left = None
        self._right = None
        self._top = None
        self._bottom = None

        self.frames = 0

        self.last_press = ()

        self.keys = Keys()
        self.shapes = None

        container.append(self)

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

    def _check_collision(self, point):
        """Check if a x and y position exists within the widget's hit box. This
        is an alternative to check_collision, and should only be used if you
        are not using any components (ex. label widget), or they do not have
        left, right, top and bottom properties.
        
        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.

        TODO: replace x and y parameters with Point (DONE)

        point - point to check for collision

        parameters: int, int
        returns: bool
        """

        return (0 < point.x - self.x < self.width and
                0 < point.y - self.y < self.height)

    def check_collision(self, point):
        """Check if a x and y position exists within the widget's hit box. This
        should be used if you are using components, or if they do have left,
        right, top and bottom properties.
        
        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.

        TODO: replace x and y parameters with Point (DONE)

        point - point to check for collision

        parameters: int, int
        returns: bool
        """

        if self._right and \
           self._left and \
           self._top and \
           self._bottom:
            return point.x > self._left and point.x < self._right and \
                   point.y > self._bottom and point.y < self._top

        return point.x > self.left and point.x < self.right and \
               point.y > self.bottom and point.y < self.top

    def draw_bbox(self, width=1, padding=0):
        """Draw the bounding box of the widget. The drawing is cached in a
        ShapeElementList so it won't take up more time. This can also be called
        draw_hitbox or draw_hit_box.
        
        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.

        width - width of the bounding box outline
        padding - padding around the widget

        parameters: int, int
        """

        if self.shapes is None:
            shape = create_rectangle_outline(self.x, self.y,
                                             self.width + padding,
                                             self.height + padding,
                                             RED, width
                                            )

            self.shapes = ShapeElementList()
            self.shapes.append(shape)

            self.shapes.center_x = self.x
            self.shapes.center_y = self.y
            self.shapes.angle = self.angle

    draw_hitbox = draw_bbox # Alias
    draw_hit_box = draw_bbox

    def snap_to_point(self, point, distance):
        """Snap the widget's position to a Point. This is useful in dragging
        widgets around, so snapping can make them snap to position if they are
        aligned to a certian widget, etc.
        
        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.
        
        point - Point for the widget to snap to. Typically this should be a
                mouse position.
        distance - distance of the snapping. This gives the user less freedom
                   but makes it easier for larger snaps.
        
        parameters: Point
        returns: bool (whether or not the widget was snapped to position)
        """
        
        if get_distance(self, point) <= distance:
            self.x = point.x
            self.y = point.y
            
            return True
        
        return False
            
    def delete(self):
        """Delete this widget and remove it from the event stack. The widget
        is not drawn and will not be accepting any events. You may want to
        override this if creating your own custom widget.

        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.
        
        If overriding this, you should remove all bindings of the widget and
        all events.
        """

        self.bindings = []
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
            self.on_update
        )

        self.remove_from_sprite_lists()

    def on_key_press(self, keys, modifiers):
        """The user pressed a key(s) on the keyboard.

        keys - key pressed by the user. In pyglet, this can be called symbol.
        modifiers - modifiers held down during the key press.

        parameters: int (32-bit), int (32-bit)
        """

        if self.disable:
            return

        self.dispatch_event("on_key", keys, modifiers)

        if self.focus:
            self.dispatch_event("on_focus")

    def on_key_release(self, keys, modifiers):
        """The user released a key(s) on the keyboard.

        keys - key released by the user. In pyglet, this can be called symbol.
        modifiers - modifiers held down during the key press.

        parameters: int (32-bit), int (32-bit)
        """

        if self.disable:
            return

        self.press = False

        self.dispatch_event("on_lift", keys, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        """The user moved the mouse.

        x - x position of mouse
        y - y position of mouse
        dx - x vector in last position from mouse
        dy - y vector in last position from mouse

        parameters: int, int, int, int
        """

        if self.disable:
            return

        if self.check_collision(Point(x, y)):
            self.hover = True

            self.dispatch_event("on_hover", x, y, dx, dy)
        else:
            self.hover = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        """The user pressed a mouse button.

        x - x position of press
        y - y position of press
        buttons - buttons defined in keyboard pressed
        modifiers - modifiers held down during the press

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if self.disable:
            return

        self.last_press = Point(x, y)

        if self.check_collision(Point(x, y)):
            self.press = True
            self.focus = True

            self.dispatch_event("on_press", x, y, buttons, modifiers)
            self.dispatch_event("on_focus")

    def on_mouse_release(self, x, y, buttons, modifiers):
        """The user released a mouse button.

        x - x position of press
        y - y position of press
        buttons - buttons defined in keyboard released
        modifiers - modifiers held down during the release

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if self.disable:
            return

        self.press = False

        self.drag = False

        self.dispatch_event("on_release", x, y, buttons, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse.

        x - x position of mouse during drag
        y - y position of mouse during drag
        dx - movement of mouse in vector from last position
        dy - movement of mouse in vector from last position
        buttons - buttons defined in keyboard during drag
        modifiers - modifiers held down during the during drag

        parameters: int, int, int, int, int (32-bit), int (32-bit)
        """

        if self.disable:
            return

        if not self.check_collision(Point(x, y)):
            if not self.check_collision(self.last_press):
                return

        self.drag = True

        if self.check_collision(Point(x, y)):
            self.dispatch_event("on_drag", x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x, y, sx, sy):
        """The user scrolled the mouse.

        x - x position of mouse during drag
        y - y position of mouse during drag
        scroll - scroll vector (positive being the mouse wheel up, negative the
                 mouse wheel down)

        parameters: int, int, Point
        """

        if self.disable:
            return

        if self.check_collision(Point(x, y)):
            if self.disable:
                return

            self.dispatch_event("on_scroll", x, y, Point(sx, sy))

    def on_text_motion_select(self, motion):
        """Some text in an pyglet.IncrementalTextLayout was selected. This is
        only used for entry widgets. See the entry widget on_text_select docs
        for more info.
        """

        self.dispatch_event("on_text_select", motion)

    def on_update(self, delta):
        """Update the widget. Only do collision checking and property updating
        here. Drawing goes in the draw function.

        delta - time elapsed since last this function was last called
        """

        self.frames += 1

        if self.component:
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

    def on_key(self, keys, modifiers):
        """The user pressed a key(s) on the keyboard. Note that this event is
        different from on_text, because on_text returns text typed as a string,
        though you can convert a key to a string by using some of the keyboard
        functions.

        When pressing Tab, the focus of the container switches to the next
        widget created. When a widget has focus, you can give it properties
        like if a button has focus, you can press Space to invoke its command.
        If you press Shift-Tab, the focus is moved back by one notch. Focus of
        a widget can be gotten with the focus property, and the on_focus event.

        You can use bit-wise to detect multiple modifiers:

        >>> if modifiers & SHIFT and \
                modifiers & CONTROL and \
                keys == A:
                # Do something

        keys - key pressed by the user. In pyglet, this can be called symbol.
        modifiers - modifiers held down during the key press.

        parameters: int (32-bit), int (32-bit)
        """

    def on_lift(self, keys, modifiers):
        """The user released a key(s) on the keyboard. Note that this event is
        different from on_text, because on_text returns text typed as a string,
        though you can convert a key to a string by using some of the keyboard
        functions.

        When pressing Tab, the focus of the container switches to the next
        widget created. When a widget has focus, you can give it properties
        like if a button has focus, you can press Space to invoke its command.
        If you press Shift-Tab, the focus is moved back by one notch. Focus of
        a widget can be gotten with the focus property, and the on_focus event.

        You can use bit-wise to detect multiple modifiers:

        >>> if modifiers & SHIFT and \
                modifiers & CONTROL and \
                keys == A:
                # Do something

        keys - key released by the user. In pyglet, this can be called symbol.
        modifiers - modifiers held down during the key press.

        parameters: int (32-bit), int (32-bit)
        """

    def on_hover(self, x, y, dx, dy):
        """The widget was hovered over by the mouse. Typically, for widgets,
        something should react to this, for example their background shadow
        becomes more intense, or their color changes. For most widgets their
        image changes or their color does.

        For the coordinates returned for this event, you can see which specific
        widget if it had subwidgets had the hover event. Hover states can be
        accessed with the hover property.
        
        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of mouse
        y - y position of mouse
        dx - movement of mouse in vector from last position
        dy - movement of mouse in vector from last position

        parameters: int, int, int, int
        """

    def on_press(self, x, y, buttons, modifiers):
        """The user pressed the widget with the mouse. When this happens, the
        widget gets the focus traversal. This event can be used with buttons,
        labels, and other widgets for cool special effects. This event is not
        called if the mouse is being dragged. This sets the press property to
        True.
        
        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of press
        y - y position of press
        buttons - buttons defined in keyboard pressed
        modifiers - modifiers held down during the press

        parameters: int, int, int (32-bit), int (32-bit)
        """

    def on_release(self, x, y, buttons, modifiers):
        """The user released the widget with the mouse. If the widget has an
        on_drag event, that event is canceled. For widgets, their state should
        be set to a hover state. This sets the drag and press properties to
        False.
        
        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of release
        y - y position of release
        buttons - buttons defined in keyboard releaseed
        modifiers - modifiers held down during the release

        parameters: int, int, int (32-bit), int (32-bit)
        """

    def on_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse, of which started over the widget. This
        is most used on text inputs and entries, where the user can select
        text, but can be on sliders and toggles and other widgets. There is no
        built-in way to get the starting position of the mouse, but that can be
        implemented. You could make a variable that gets the coordinates of each
        mouse press, then in the on_drag event, gets the last press coordinates.
        This sets the drag property to True.

        This event is only dispatched if the mouse started on the widget. It is
        not cancelled if the mouse moves outside of the widget, for as long as
        it starts in it, it works. You can get the start point with the
        last_press property.
        
        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of mouse during drag
        y - y position of mouse during drag
        dx - movement of mouse in vector from last position
        dy - movement of mouse in vector from last position
        buttons - buttons defined in keyboard during drag
        modifiers - modifiers held down during the during drag

        parameters: int, int, int, int, int (32-bit), int (32-bit)
        """

    def on_scroll(self, x, y, scroll):
        """The user scrolled the mouse on the widget. This should be
        implemented in all widgets that change values, like spinboxes. Widgets
        that only have two values (like toggles) should not use this event, as
        it is impractical.
        
        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of mouse during drag
        y - y position of mouse during drag
        scroll - scroll vector (positive being the mouse wheel up, negative the
                 mouse wheel down)

        parameters: int, int, Point
        """

    def on_focus(self):
        """The widget recieves focus from the container. Two widgets cannot
        have focus simultaneously. When a widget has focus, you should
        implement events that give it more features. For example, in a spinbox
        widget, if it has focus, the user can press the Up or Down keys to
        increase or decrease the value. The focus property can be accessed.

        This may or may not be used for shapes. It vastly depends if how the
        widget gains focus. If it is pressed, then you may use this for certian
        shapes, but if it focused with Tab, then you may use this for all
        shapes.
        
        See https://en.wikipedia.org/wiki/Focus_(computing)
        """


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
        """Create an Image widget. This is a simple widget used as the main
        component in many other widgets. It is not suitable to create vast
        numbers of these, because you must create a texture every single time.
        Use this for any sort of Image you are going to draw if you want to
        draw it efficiently.

        image - filepath of the image
        x - x position of image
        y - y position of image
        scale - scale of image. See arcade.sprite.Sprite for details.
        """

        Widget.__init__(self, image=image, scale=scale)

        self.image = image

        self.x = x
        self.y = y

        self.normal_image = image
        self.hover_image = load_texture(image)
        self.press_image = load_texture(image)
        self.disable_image = load_texture(image)

        widgets_list.append(self)

    def _get_x(self):
        """Get the x position of the image.

        returns: int
        """

        return self.center_x

    def _set_x(self, x):
        """Set the x position of the image.

        x - new x position of image

        parameters: int
        """

        self.center_x = x

    def _get_y(self):
        """Get the y position of the image.

        returns: int
        """

        return self.center_y

    def _set_y(self, y):
        """Set the y position of the image.

        y - new y position of image

        parameters: int
        """

        self.center_y = y

    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)

    def update(self):
        pass
        # if self.hover:
        #     self.texture = self.hover_image
        # if self.press:
        #     self.texture = self.press_image
        # if self.disable:
        #     self.texture = self.disable_image
        # elif not self.hover and \
        #     not self.press and \
        #     not self.disable:
        #     self.image = self.normal_image


class Label(Widget):
    """Label widget to draw and display HTML text.
    """

    UPDATE_RATE = 7

    def __init__(self, text, x, y, frame=None,
                 colors=[BLACK, (COOL_BLACK, DARK_SLATE_GRAY, DARK_GRAY)],
                 font=DEFAULT_FONT, title=False,
                 justify=LEFT, width=0, multiline=False,
                 command=None, parameters=[],
                 outline=None, location=None,
                ):

        """Create a Label widget to display efficiently and advanced HTML text.
        Note that this uses pyglet's HTML decoder, so formats are limited. See
        the full list of formats at:

        https://pyglet.readthedocs.io/en/latest/programming_guide/text.html#html

        text - text to be displayed on the label
        x - x position of label
        y - y position of label
        colors - colors of the text. This is specified in a format
                 [normal, (hover, press, disable)], which are its states and
                 the appropiate colors displayed. Defaults to
                 [BLACK, (COOL_BLACK, DARK_SLATE_GRAY, DARK_GRAY)]. Their RGB
                 values can be found in the color module.
        font - font of the label. This can be a object-oriented font or just a
               tuple containing the font description in (family, size).
               Defaults to DEFAULT_FONT.
        title - the label is drawn as a title. This has long since been
                deprecated.
        justify - horizontal justification of the Label. Its avaliable options
                  are "center", "left", or "right". Defaults to "right".
        width - width of the label. This needs only to be used if the label is
                multiline. Defaults to 0.
        multiline - text is drawn multiline. If this is set to true then the
                    width must be set to a value greater than zero, as this
                    will be the length each line for wrap.
        command - command called when the label is pressed
        parameters - parameters of the command
        outline - outline of the label as a rectangle. This is specified as
                  (color, padding, width). Defaults to None.

        Because this is object-oriented, nearly all of the values can be
        changed later by changing its properties. The update rate of the label
        defaults to once every sixty frames. This can be modified by setting
        the UPDATE_RATE property. The lower it is set, the higher the update
        rate is. If the update rate is too low (once every frame), then you
        will notice a massive performance drop. You can force the label to set
        text using force_text.

        See https://pyglet.readthedocs.io/en/latest/programming_guide/text.html
        for details regarding text specification and drawing.
        """

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
            text = " "

        if not justify in (LEFT, CENTER, RIGHT):
            raise WidgetsError(f"Invalid label justification \"{justify}\""
                                "Must be \"left\", \"center\", or \"right\".")

        if multiline and not width:
            raise WidgetsError(f"When the parameter \"multiline\" is set to "
                                "True, the parameter \"width\" must be set to a "
                                "value greater than 0. See the documentation "
                                "for more details.")

        self.label = HTMLLabel(f"{text}", location, x, y,
                               anchor_x=LEFT, anchor_y=CENTER,
                               width=width, multiline=multiline,
                               )

        Widget.__init__(self, frame=frame)

        self.x = x + self.frame.x
        self.y = y + self.frame.y

        if self.frame.direction == TOP:
            self.x = self.frame.x - x
            self.y = self.frame.y - y

        self.colors = colors
        self.font = font
        self.title = title
        self.justify = justify
        self._width = width
        self.multiline = multiline
        self.command = command
        self.parameters = parameters
        self.outline = outline

        self.force_text(text)

        self.bindings = []

        self.length = 0

    def _get_x(self):
        """Get the x position of the label.

        returns: int
        """

        return self.label.x

    def _set_x(self, x):
        """Set the x position of the label.

        x - new x position of the label

        parameters: int
        """

        self.label.x = x

    def _get_y(self):
        """Get the y position of the label.

        returns: int
        """

        return self.label.y

    def _set_y(self, y):
        """Set the y position of the label.

        y - new y position of the label

        parameters: int
        """

        self.label.y = y

    def _get_text(self):
        """Get the text of the Label.

        returns: str
        """

        return self.document.text

    def _set_text(self, text):
        """Set the text of the label. It is not recommended to call this
        repeatedly with a high update rate, as this can cause the fps to drop.

        text - new text of the label

        parameters: str
        """

        if self.frames % self.UPDATE_RATE:
            return

        if self.label.text == text:
            return

        if not text:
            text = " "

        self.label.begin_update()

        self.label.text = text

        self.label.end_update()

    def _get_document(self):
        """Get the document of the label.

        returns: str
        """

        return self.label.document

    def _set_document(self, document):
        """Set the document of the label. This is far less efficient than
        modifying the current document, as relayout and recalculating glyphs
        is very costly.

        document - new document of the Label

        parameters: pyglet.text.document.HTMLDocument
        """

        self.label.document = document

    def _get_width(self):
        """Get the content width of the label. This property cannot be set.

        returns: int
        """

        return self.label.content_width

    def _get_height(self):
        """Get the content height of the label. This property can not be set.

        returns: int
        """

        return self.label.content_height

    text = property(_get_text, _set_text)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    document = property(_get_document, _set_document)
    width = property(_get_width)
    height = property(_get_height)

    def bind(self, *keys):
        """Bind some keys to the label. Invoking these keys activates the
        label. If the Enter key was binded to the lutton, pressing Enter will
        invoke its command and switches its display to a pressed state.

        >>> label.bind(ENTER, PLUS)
        [65293, 43]

        *keys - keys to be binded

        parameters: *int (32-bit)
        returns: list
        """

        self.bindings = [*keys]
        return self.bindings

    def unbind(self, *keys):
        """Unbind keys from the label.

        >>> label.bind(ENTER, PLUS, KEY_UP, KEY_DOWN)
        [65293, 43, 65362, 65364]
        >>> label.unbind(PLUS, KEY_UP)
        [65293, 65364]

        parameters: *int(32-bit)
        returns: list
        """

        for key in keys:
            self.bindings.remove(key)
        return self.bindings

    def invoke(self):
        """Invoke the label. This switches its text to a pressed state and
        calls the its associated command with the specified parameters. If the
        label is disabled this has no effect.
        """

        if self.disable or not self.command:
            return

        self.press = True

        if self.parameters:
            self.command(self.parameters)
        else:
            self.command()

    def force_text(self, text):
        """Force the label to set the text. This should only be used with
        caution, because if used excessively, will cause a performance drop.
        The update rate is completely ignored.

        text - new text of the label

        parameters: str
        """

        if self.text == text:
            return

        if not text:
            text = " "

        self.label.text = text

    def draw_bbox(self, width=1, padding=0):
        """Draw the hitbox of the label. See Widget.bbox for more details.
        This overrides the Widget.bbox because of its left anchor_x.
        """

        draw_rectangle_outline(
            self.x + self.width / 2,
            self.y, self.width + padding,
            self.height + padding, RED, width
        )

    draw_hitbox = draw_bbox
    draw_hit_box = draw_bbox

    def draw(self):
        if self.outline:
            draw_rectangle_outline(
                self.x + self.width / 2, self.y,
                self.width + self.outline[1],
                self.height + self.outline[1],
                self.outline[0], self.outline[2]
            )

        if self.text:
            if not self._left == self.x - self.width / 2 or \
                not self._right == self.x + self.width / 2 or \
                not self._top == self.y + self.height / 2 or \
                not self._bottom == self.y - self.height / 2:
                self._left = self.x - self.width / 2
                self._right = self.x + self.width / 2
                self._top = self.y + self.height / 2
                self._bottom = self.y - self.height / 2

    def on_key(self, keys, modifiers):
        if isinstance(self.bindings, list):
            if keys in self.bindings:
                self.invoke()

        else:
            if self.bindings == keys:
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
        processing time is much faster. And with batches, things are more
        efficient and speed is even greater.

        With no other widgets, you can draw 10,000 or more labels before the
        fps drops below 60.
        """

        self.length = len(self.text)

        if "<u" in self.text or "<\\u>" in self.text:
            # ValueError: Can only assign sequence of same size
            return

        # States
        if self.hover:
            self.document.set_style(0, self.length,
                                    {"color" : four_byte(self.colors[1][1])})
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
    """Button widget to invoke and call commands. Pressing on a button invokes
    its command, which is a function or callable.
    """

    keys = []

    def __init__(
                 self, text, x, y, command=None, parameters=[],
                 link=None,
                 colors=["yellow", BLACK], font=default_font,
                 callback=SINGLE
                ):

        """Initialize a button. A button has two components: an Image and a
        Label. You can customize the button's images and display by changing
        its normal_image, hover_image, press_image, and disable_image
        properties, but it is recommended to use the Pushable widget.

        text - text to be displayed on the button
        x - x position of the button
        y - y position of the button
        command - command to be invoked when the button is called. Defaults
                  to None.
        parameters - parameters of the callable when invoked. Defaults to [].
        link - website link to go to when invoked. Defaults to None.
        colors - colors of the button. Defaults to ("yellow", BLACK).
        font - font of the button. Defaults to the default font.
        callback - how the button is invoked:
                   SINGLE - the button is invoked once when pressed
                   DOUBLE - the button can be invoked multiple times in focus
                   MULTIPLE - the button can be invoked continuously

                   Defaults to SINGLE.

        parameters: str, int, int, callable, list, tuple, Font, str
        """

        # A two-component widget:
        #     - Image
        #     - Label

        if not callback in (SINGLE, DOUBLE, MULTIPLE):
            raise WidgetsError("Invalid callback for button. Must be 1, 2, or "
                               "3. Refer to the class documentation for more "
                               "information."
                              )

        self.image = Image(widgets[f"{colors[0]}_button_normal"], x, y)
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

        self.bindings = []

        # Find a way to fit to 80 chars

        self.normal_image = load_texture(widgets[f"{colors[0]}_button_normal"])
        self.hover_image = load_texture(widgets[f"{colors[0]}_button_hover"])
        self.press_image = load_texture(widgets[f"{colors[0]}_button_press"])
        self.disable_image = load_texture(
            widgets[f"{colors[0]}_button_disable"])

    def _get_text(self):
        """Get the text of the button.

        returns: str
        """

        return self.label.text

    def _set_text(self, text):
        """Set the text of the button. Unlike a label, the text is not forced,
        so it may not be the most updated.

        parameters: str
        """

        self.label.text = text

    def _get_x(self):
        """Get the x position of the button.

        returns: int
        """

        return self.image.x

    def _set_x(self, x):
        """Set the x position of the button.

        x - new x position of the button

        parameters: int
        """

        self.image.x = self.label.x = x

    def _get_y(self):
        """Get the y position of the button.

        returns: int
        """

        return self.image.y

    def _set_y(self, y):
        """Set the y position of the button.

        y - new y position of the button

        parameters: int
        """

        self.image.y = self.label.y = y

    text = property(_get_text, _set_text)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)

    def bind(self, *keys):
        """Bind some keys to the button. Invoking these keys activates the
        button. If the Enter key was binded to the button, pressing Enter will
        invoke its command and switches its display to a pressed state.

        Currently, binding modifiers with keys is not supported, though this is
        quite easy to implement by yourself.

        >>> button.bind(ENTER, PLUS)
        [65293, 43]

        *keys - keys to be binded

        parameters: *int (32-bit)
        returns: list
        """

        for key in keys:
            self.bindings.append(key)
        return self.bindings

    def unbind(self, *keys):
        """Unbind keys from the button.

        >>> button.bind(ENTER, PLUS, KEY_UP, KEY_DOWN)
        [65293, 43, 65362, 65364]
        >>> button.unbind(PLUS, KEY_UP)
        [65293, 65364]

        parameters: *int(32-bit)
        returns: list
        """

        for key in keys:
            self.bindings.remove(key)

        return self.bindings

    def invoke(self):
        """Invoke the button. This switches its image to a pressed state and
        calls the its associated command with the specified parameters. If the
        button is disabled this has no effect.
        """

        if self.disable or not self.command:
            return

        self.press = True

        if self.parameters:
            self.command(self.parameters)
        else:
            self.command()

        if self.link:
            open_new(self.link)

    def draw(self):
        """Draw the button. The component of the button is the image, which takes
        all of the collision points.

        1. Image - background image of the button
        2. Label - text of the button
        """

        # Update Label properties

        # self.label.text = self.text

        if not self.label.colors[0] == self.colors[1] or \
            not self.label.font == self.font or \
            not self.label.x == self.x - self.label.label.content_width / 2:
            self.label.colors[0] = self.colors[1]
            self.label.font = self.font
            self.label.x = self.x - self.label.label.content_width / 2

        self.component = self.image

    def on_press(self, x, y, buttons, modifiers):
        """The button is pressed. This invokes its command if the mouse button
        is the left one.

        TODO: add specifying proper mouse button in settings

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if buttons == MOUSE_BUTTON_LEFT:
            self.invoke()

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the
        button has focus.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int (32-bit), int (32-bit)
        """

        if keys == SPACE and self.focus:
            self.invoke()

        if isinstance(self.bindings, list):
            if keys in self.bindings:
                self.invoke()

        else:
            if self.bindings == keys:
                self.invoke()

    def update(self):
        """Update the button. This registers events and updates the button
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

        double = False

        for key in self.keys:
            for binding in self.bindings:
                if key == binding:
                    double = True
                    break
                # else:
                #     continue
            break

        multiple = double # Haha

        if self.callback == DOUBLE and self.focus and double:
            self.invoke()

        if self.callback == MULTIPLE:
            if self.press or multiple:
                self.invoke()

        # .update is not called for the Label, as it is uneccessary for the
        # Label to switch colors on user events.


class Slider(Widget):
    """Slider widget to display slidable values.

    FIXME: even knob moves when setting x property
    TODO: add keyboard functionality

    https://github.com/eschan145/Armies/issues/20
    """

    _value = 0
    destination = 0

    def __init__(self, text, x, y, colors=BLACK, font=DEFAULT_FONT,
                 default=0, size=10, length=200, padding=50, round=0):
        """Initialize a slider."""

        self.bar = Image(slider_horizontal, x, y)
        self.knob = Image(knob, x, y)
        self.label = Label(text, x, y, font=font)

        Widget.__init__(self)

        self.text = text
        self.colors = colors
        self.font = font
        self.size = size
        self.length = length
        self.padding = padding
        self.round = round

        self.value = default

        self.x = x
        self.y = y

        self.knob.left = self.x - self.length / 2

    def _get_value(self):
        """Get the value or x of the slider.

        returns: int
        """

        return self._value

    def _set_value(self, value):
        """Set the value or x of the slider.

        value - new value to be set

        parameters: int
        """

        if self._value >= self.size:
            self._value = self.size
            return

        elif self._value <= 0:
            self._value = 0
            return

        max_knob_x = self.right # + self.knob.width / 2

        self._value = round(value, self.round)

        x = (max_knob_x - self.left) * value / self.size \
            + self.left + self.knob.width / 2
        self.knob.x = max(self.left, min(x - self.knob.width / 2, max_knob_x))

    def _get_x(self):
        """Get the x position of the slider.

        returns: int
        """

        return self.bar.x

    def _set_x(self, x):
        """Set the x position of the slider.

        x - new x position of the slider

        parameters: int
        """

        self.bar.x = x
        self.label.x = self.bar.left - self.padding
        self.knob.left = self.x - self.length / 2

    def _get_y(self):
        """Get the y position of the slider.

        returns: int
        """

        return self.bar.y

    def _set_y(self, y):
        """Set the y position of the slider.

        y - new y position of the slider

        parameters: int
        """

        self.bar.y = self.knob.y = self.label.y = y

    value = property(_get_value, _set_value)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)

    def update_knob(self, x):
        """Update the knob and give it a velocity when moving. When calling
        this, the knob's position will automatically update so it is congruent
        with its size.

        x - x position of the position

        parameters: int
        """

        self.destination = max(self.left,
                               min(x - self.knob.width / 2, self.right))
        self._value = round(abs(((self.knob.x - self.left) * self.size) \
                      / (self.left - self.right)), self.round)

    def reposition_knob(self):
        """Update the value of the slider. This is used when you want to move
        the knob without it snapping to a certain position and want to update
        its value. update_knob(x) sets a velocity so the knob can glide.
        """

        self._value = round(abs(((self.knob.x - self.left) * self.size) \
                      / (self.left - self.right)), self.round)

    def draw(self):
        """Draw the slider. The component of the slider is the bar, which takes
        all of the collision points.

        1. Bar (component)
        2. Knob
        3. Label
        """

        if not self.text:
            self.text = "Label"

        self.label.text = self.text

        if not self.label.font == self.font or \
            not self.label.colors[0] == self.colors or \
            not self.bar.width == self.length:
            self.label.font = self.font
            self.label.colors[0] = self.colors
            self.bar.width = self.length

        self.component = self.bar

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the slider
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
            self.value -= 1
            # self.reposition_knob()
        elif keys == KEY_LEFT:
            self.value += 1
            # self.reposition_knob()

    def on_press(self, x, y, buttons, modifiers):
        """The slider is pressed. This updates the knob to the x position of the
        press.

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        self.update_knob(x)

    def on_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse when it was pressed. This updates the knob
        to the x position of the press.

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        self.update_knob(x)

    def on_scroll(self, x, y, mouse):
        """The user scrolled the mouse wheel. This will change the knob's
        position and adjust its x position.

        x - x position of the mouse scroll
        y - y position of the mouse scroll
        mouse - movement in vector from the last position (x, y)
        direction - direction of mouse scroll

        parameters: int, int, tuple (x, y), float
        """

        self.value += mouse.y

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
                
            if self.knob.right > self.destination and \
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


class Toggle(Widget):
    """Toggle widget to switch between true and false values. This uses
    a special effect of fading during the switch.

    FIXME: even knob moves when setting x property
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
                 default=True, padding=160,
                 callback=SINGLE
                ):

        """Initialize a toggle. A toggle is a widget that when pressed, switches
        between True and False values.

        text - text to be displayed alongside the toggle
        x - x position of the toggle
        y - y position of the toggle
        colors - text color of the Label
        font - font of the Label
        default - default value of the toggle
        padding - padding of the Label and the toggle
        callback - how the toggle is invoked:
                   SINGLE - toggle is invoked once when pressed
                   MULTIPLE - toggle can be invoked continuously

                   Defaults to SINGLE.

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

        if not callback in (SINGLE, DOUBLE, MULTIPLE):
            raise WidgetsError("Invalid callback for toggle. Must be 1, 2, or "
                               "3. Refer to the class documentation for more "
                               "information."
                              )

        self.bar = Image(image, x, y)
        self.knob = Image(knob, x, y)

        self.label = Label(knob, x, y, font=font)

        Widget.__init__(self)

        self.text = text
        self.colors = colors
        self.font = font
        self.padding = padding
        self.callback = callback

        self.x = x
        self.y = y

        self.knob.left = self.bar.left + 2

    def _get_x(self):
        """Get the x position of the toggle.

        returns: int
        """

        return self.bar.x

    def _set_x(self, x):
        """Set the x position of the toggle.

        x - new x position of the toggle

        parameters: int
        """

        self.bar.x = x
        self.label.x = self.bar.left - self.padding

    def _get_y(self):
        """Get the y position of the toggle.

        returns: int
        """

        return self.bar.y

    def _set_y(self, y):
        """Set the y position of the toggle.

        y - new y position of the toggle

        parameters: int
        """

        self.bar.y = self.knob.y = self.label.y = y

    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)

    def draw(self):
        """Draw the toggle. The component of the toggle is the bar, which takes
        all of the collision points.

        1. Bar (component)
        2. Knob
        3. Label
        """

        self.label.text = self.text

        if not self.label.colors[0] == self.colors or \
            not self.label.font == self.font:
            self.label.colors[0] = self.colors
            self.label.font = self.font

        self.component = self.bar

    def on_press(self, x, y, buttons, modifiers):
        """The toggle is pressed. This switches between True and False values. If
        the Control key is held down during this, this will have no effect.

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if not modifiers & CONTROL:
            self.switch = True

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the toggle
        has focus. If the Space or Enter key is pressed, the toggle will be
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

        if self.callback == MULTIPLE:
            if self.keys[SPACE]:
                self.switch = True
                
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

        if self.knob.hover:
            self.knob.scale = KNOB_HOVER_SCALE
        else:
            self.knob.scale = 1


_Caret = Caret

class Caret(_Caret):
    """Caret used for pyglet.text.IncrementalTextLayout."""

    BLINK_INTERVAL = 0.5

    def __init__(self, layout):
        """Initalize a caret designed for interactive editing and scrolling of
        large documents and/or text.
        """

        _Caret.__init__(self, layout)

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
        """Update the caret. This is used internally for the entry widget.

        line - current line of the caret
        update_ideal_x - x position of line is updated

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

        y += self._layout.y + self._layout.height / 2 + 2

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
           entry taking up much CPU

    TODO
    1. Add rich text formatting (use pyglet.text.document.HTMLDocument)
    2. Add show feature for passwords
    3. Add copy, paste, select all, and more text features (COMPLETED)
    4. Add undo and redo features
    5. Enable updates for the layout for smoother performance. This raises
       AssertionError, one that has been seen before.
    6. Finish up scrolling of history. This is incomplete, and if text is
       added before the history's index, then the index is not changed.

    https://github.com/eschan145/Armies/issues/11

    Last updated: August 4th 2022
    """

    blinking = True
    length = 0
    max = MAX
    _validate = printable
    _document = None
    _placeholder = None

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

    def __init__(self, x, y, text="", font=default_font, color=BLACK,
                 history=True):

        """Initialize the entry. Typically a widget will push events
        automatically, but because there are custom named events, they have
        to be defined here.

        An entry is a widget where text input can be returned. Typing into
        an entry appends some text, which can be used for usernames,
        passwords, and more. Text can be removed by many keys.

        x - x position of the entry
        y - y position of the entry
        text - default text of the entry
        font - font of the text in the entry
        color - color of the text in RGB as a tuple of three ints

        history - the user can press Alt Left or Alt Right to go back and forth
                  between history. History can be marked when the user presses
                  the entry and the position of the caret is changed.

        properties:
            document - document of the IncrementalTextLayout
            layout - internal IncrementalTextLayout for efficient rendering
            caret - caret of the entry
            image - image displayed to give the entry a graphical look

            x - x position of the entry
            y - y position of the entry
            default - default text of the entry (changing this has no effect)
            font - font of the entry

            blinking - caret is visible or not visible

            length - length of the text in the entry
            max - maximum amount of characters in the entry

            text - displayed text of the entry
            selection - selected text of the entry
            layout_colors - layout colors of the entry
            validate - validation of the characters in the entry
            index - index of the caret (position)
            view - view vector of the entry

        methods:
            blink - blink the caret and switch its visibility
            insert - insert some text in the entry
            delete - delete some text from the entry
        """

        self._document = decode_text(text)

        self.layout = IncrementalTextLayout(self._document, 190, 24, batch=batch)

        self.image = Image(entry_normal, x, y)
        self.caret = Caret(self.layout)

        Widget.__init__(self)

        self.x = x
        self.y = y
        self.font = font
        self.default = text

        self.layout.anchor_x = LEFT
        self.layout.anchor_y = CENTER

        self.history = []
        self._history_index = 0
        self._history_enabled = history

        self._document.set_style(0, len(text), dict(font_name=DEFAULT_FONT[0],
                                                    font_size=DEFAULT_FONT[1],
                                                    color=four_byte(color)))

        self.window.push_handlers(
            self.on_text,
            self.on_text_motion
        )

    def _get_document(self):
        """Get the current document of the entry.

        returns: pyglet.text.document.UnformattedDocument
        """

        return self.layout.document

    def _set_document(self, document):
        """Set the document of the entry. This is far less efficient than
        modifying the current document, as relayout and recalculating glyphs
        is very costly.

        document - new document of entry

        parameters: pyglet.text.document.UnformattedDocument
        """

        self.layout.document = document

    def _get_text(self):
        """Return the text of the entry.

        returns: str
        """

        return self.document.text

    def _set_text(self, text):
        """Set the text of the entry.

        text - new text to be displayed. This can be a string or a tuple
        change_index - index is changed after text input. If True, the index
                       is set to the end of the entry.

        parameters: str or tuple
        """

        text = text or ""

        if isinstance(text, Tuple):
            # self.document._delete_text(0, self.max)
            # self.document._insert_text(0, text[0], None)
            self.document.text = text

            if text[1]:
                # Put the caret to the end
                self.index = self.max

            return

        # self.document._delete_text(0, self.max)
        # self.document._insert_text(0, text, None)
        self.document.text = text

    def _get_x(self):
        """Get the x position of the entry.

        returns: int
        """

        return self.image.x

    def _set_x(self, x):
        """Set the x position of the entry.

        x - new x position of the entry

        parameters: int
        """

        self.layout.x = x - self.layout.width / 2
        self.image.x = x

    def _get_y(self):
        """Get the y position of the entry.

        returns: int
        """

        return self.image.y

    def _set_y(self, y):
        """Set the y position of the entry.

        y - new y position of the entry

        parameters: int
        """

        self.layout.y = y - 5
        self.image.y = y

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

    def _get_mark(self):
        """Return the mark of the caret within the document.

        returns: int
        """

        return self.caret.mark

    def _set_mark(self, mark):
        """Set the mark of the caret within the document.

        An interactive text selection is determined by its immovable end (the
        caret's position when a mouse drag begins) and the caret's position,
        which moves interactively by mouse and keyboard input.

        This property is None when there is no selection. It should not be set
        to zero, because that would just set the selection start index in the
        first position.

        mark - new mark of the caret position. See above for details

        parameters: int
        """

        self.caret.mark = mark

    def _get_selection(self):
        """Get the selection indices of the entry, with the start and end as
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
        """Set the selection indices of the entry, which are defined with
        the property layout_colors.

        selection - tuple of selection indices (start, end)

        parameters: tuple
        """

        self.mark = selection[1]

        self.layout.selection_start = selection[0]
        self.layout.selection_end = selection[1]

    def _get_layout_colors(self):
        """Get the layout colors of the entry. This will return a tuple of
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
        """Set the layout colors of the entry.

        colors - tuple of three colors. The first item is the background
                 color of the selection, while the second item is the caret
                 color. The third item is the color of the text selected.

        parameters: tuple (selection, caret, text)
        """

        self.layout.selection_background_color = colors[0]
        self.layout.selection_color = colors[2]

        self.caret.color = colors[1]

    def _get_validate(self):
        """Get the validation of the entry.

        returns: str
        """

        return self._validate

    def _set_validate(self, validate):
        """Set the validation of the entry. This is a string containing all
        of the characters the user is able to type. Common charsets cam be
        found in the string module.

        validate - validation to set

        parameters: str
        """

        self._validate = validate

    def _get_placeholder(self):
        """Get the placeholder text of the entry.

        returns: str
        """

        return self._placeholder

    def _set_placeholder(self, placeholder):
        """Set the placeholder text of the entry. This is just "default" text,
        but it is removed when you press the entry. When the entry loses focus,
        the placeholder text is added again.

        placeholder - placeholder or untypable text

        parameters: str
        """

        self._placeholder = placeholder

    def _get_view(self):
        """Get the view vector of the entry.

        returns: tuple (x, y)
        """

        return (
                self.layout.view_x,
                self.layout.view_y
        )

    def _set_view(self, view):
        """Set the view vector of the entry.

        view - vector of x and y views as a Point

        parameters: Point
        """

        self.layout.view_x = view.x
        self.layout.view_y = view.y

    text = property(_get_text, _set_text)
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    document = property(_get_document, _set_document)
    index = property(_get_index, _set_index)
    mark = property(_get_mark, _set_mark)
    selection = property(_get_selection, _set_selection)
    layout_colors = property(_get_layout_colors, _set_layout_colors)
    validate = property(_get_validate, _set_validate)
    placeholder = property(_get_placeholder, _set_placeholder)
    view = property(_get_view, _set_view)

    def blink(self, delta):
        """The caret toggles between white and black colors. This is called
        every 0.5 seconds, and only when the caret has focus.

        delta - delta time in seconds since the function was last called.
                This varies about 0.5 seconds give or take, because of
                calling delay, lags, and other inefficiencies.

        parameters: float
        """

        if not self.caret._list.colors[3] or \
            not self.caret._list.colors[7]:
            alpha = 255
        else:
            alpha = 0

        self.caret._list.colors[3] = alpha
        self.caret._list.colors[7] = alpha

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
        change_index - index is updated to the end of the addition. This value
                       usually just needs to be left where it is. Defaults to
                       True.

        parameters: int, str, bool
        """

        # self.text = insert(index, self.text, text)

        self.document._insert_text(index, text, None)

        if change_index:
            self.index = self.index + len(text)

    def delete(self, start, end):
        """Delete some text at a start and end index, one character after the
        start position and a character after the end position.

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

    def clear(self, text=False, mark=0, index=0):
        """Clear the text in the entry and remove all of its caret properties.
        This is just a shortcut for setting the index, text, and mark to None.

        text - clear the text in the entry
        mark - reset the mark in the entry
        index - move the index of the caret to the first position

        parameters: bool or str, int, int
        """

        self.text = text or None
        self.mark = mark
        self.index = index

    def draw(self):
        """Draw the entry. The layout is drawn with pyglet rendering.

        1. Image component
        2. Layout

        FIXME: there is a bug here. The anchor_x and anchor_y properties of the
               layout have to be set again and again. This makes performance
               deadly slow.
        """

        self.layout.begin_update()

        self.layout.anchor_x = LEFT
        self.layout.anchor_y = CENTER

        self.layout.end_update()

        self.component = self.image

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts.

        Control + A     Select all of the text
        Control + V     Paste the clipboard's latest text
        Control + C     Copy the selected text and add it to the clipboard
        Control + X     Cut the selected text and add it to the clipboard. This
                        is essentially copying and deleting text, useful for
                        moving incorrectly placed text.

        If history is enabled, the user can hold Alt and press Left and Right
        to scroll back history.

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

        if modifiers & ALT and self._history_enabled:
            # This code is a little messy...

            if keys == KEY_LEFT:
                try:
                    self._history_index -= 1
                    self.index = self.history[self._history_index]

                except IndexError:
                    # Get the first item in the history
                    index = 0

                    self._history_index = index
                    self.index = self.history[index]

            if keys == KEY_RIGHT:
                try:
                    self._history_index += 1
                    self.index = self.history[self._history_index]

                except IndexError:
                    # Get the last item in the history
                    index = len(self.history) - 2 # Compensate for added index

                    self._history_index = index
                    self.index = self.history[index]

    def on_focus(self):
        """The entry has focus, activating events. This activates the caret
        and stops a few errors.
        """

        if self.text == self.default:
            self.clear()

    def on_text(self, text):
        """The entry has text input. The entry adds text to the end.
        Internally, the entry does a few things:

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
        """The entry has caret motion. This can be moving the caret's
        position to the left with the Left key, deleting a character
        previous with the Backspace key, and more.

        This filters out Alt key and the Left or Right key is being pressed,
        as this is used for history.

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

                 You can get the list of all text motions with motions_string()
                 in the keyboard module. You can also get their keyboard
                 combinations with motions_combinations().

        parameters: int (32-bit)
        """

        if not self.focus:
            return

        if self.keys[ALT]:
            if motion == MOTION_LEFT or \
                motion == MOTION_RIGHT:
                return

        self.caret.on_text_motion(motion)

    def on_text_select(self, motion):
        """Some text in the entry is selected. When this happens, the
        selected text will have a blue background to it. Moving the caret
        with a text motion removes the selection (does not remove the text).

        NOTE: this is not called with caret mouse selections. See on_press.

        motion - motion used by the user. These can be made with the user.

                 SHIFT + LEFT               SHIFT + RIGHT
                 SHIFT + UP                 SHIFT + DOWN
                 CONTROL + SHIFT + LEFT     CONTROL + SHIFT + RIGHT

        parameters: int (32-bit)
        """

        if not self.focus:
            return

        self.caret.on_text_motion_select(motion)

    def on_press(self, x, y, buttons, modifiers):
        """The entry is pressed. This will do a number of things.

            - The caret's position is set to the nearest character.
            - The history will add the caret's position.
            - If text is selected, the selection will be removed.
            - If the Shift key is being held, a selection will be created
              between the current caret index and the closest character to
              the mouse.
            - If two clicks are made within 0.5 seconds (double-click), the
              current word is selected.
            - If three clicks are made within 0.5 seconds (triple-click), the
              current paragraph is selected.
            - If there is a placeholder text, the text is removed.

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        _x, _y = x - self.layout.x, y - self.layout.y

        if self.text == self.placeholder:
            self.text = None

        index_before = self.index

        self.caret.on_mouse_press(x, y, buttons, modifiers)

        index_after = self.index

        self.mark = None

        if index_before is not index_after:
            # Add history
            self.history.append(index_after)

        if self.keys[SHIFT]:
            indices = sorted((index_before, index_after))

            self.selection = indices
            self.mark = max(index_before, index_after)


    def on_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse when it was pressed. This can create
        selections on entries and move the knob in sliders.

        x - x position of the current position
        y - y position of the current position
        dx - movement in x vector from the last position
        dy - movement in y vector from the last position

        buttons - buttons that were dragged with the mouse
        modifiers - modifiers being held down

        parameters: int, int, float, float, int (32-bit), int (32-bit)
        """

        _x, _y = x - self.layout.x, y - self.layout.y

        if self.press:
            self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

            self.index = self.caret.position
        else:
            if self.focus:
                self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

                self.index = self.caret.position

    def update(self):
        """Update the caret and entry. This schedules caret blinking and
        keeps track of focus.
        """

        if not self.length == len(self.text):
            self.length = len(self.text)

        if self.focus:
            if not self.blinking:
                schedule(self.blink, ENTRY_BLINK_INTERVAL)

                self.blinking = True

        else:
            self.index = 0
            self.mark = None
            self.blinking = False

            unschedule(self.blink)


class Combobox(Widget, EventDispatcher):

    _display = []
    _view = None
    displayed = False
    last_text = None
    scroller = None

    def __init__(self, x, y, options, color="yellow", default=0):

        self.entry = Entry(x, y)
        self.button = Pushable(None, x, y, self.reset_display,
                               images=(widgets[f"{color}_button_square_normal"],
                                       widgets[f"{color}_button_square_hover"],
                                       widgets[f"{color}_button_square_press"])
                               )
        self.button.image.scale = 0.5

        self.buttons = []

        Widget.__init__(self)

        self.x = x
        self.y = y
        self.options = options
        self.display = options

        _widgets.append(self.entry.image)
        _widgets.append(self.button.image)

    def _get_text(self):
        return self.entry.text

    def _set_text(self, text):
        self.entry.text = text

    def _get_x(self):
        """Get the x position of the Combobox.

        returns: int
        """

        return self.entry.x

    def _set_x(self, x):
        """Set the x position of the Combobox.

        x - new x position of the Combobox

        parameters: int
        """

        self.entry.x = x

    def _get_y(self):
        """Get the y position of the Combobox.

        returns: int
        """

        return self.entry.y

    def _set_y(self, y):
        """Set the y position of the Combobox.

        y - new y position of the Combobox

        parameters: int
        """

        self.entry.y = y

    def _get_view(self):
        """Get the vertical view of the Combobox.

        returns: int
        """

        return self._view

    def _set_view(self, view):
        """Set the vertical view of the Combobox.

        view - vertical view of the Combobox

        parameters: int
        """

        self._view = view
        self.display = self.display[view : view + 3]

    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    view = property(_get_view, _set_view)

    def _get_display(self):
        return self._display

    def _set_display(self, display):
        self.buttons.clear()

        identifier = 1

        for option in display:
            identifier += 1

            if identifier == 2: image = (combobox_top_normal, combobox_top_normal)
            elif identifier == len(display) + 1: image = (combobox_bottom_normal, combobox_bottom_normal)
            else: image = (combobox_middle_normal, combobox_middle_normal)

            button = Pushable(
                      option, 0,
                      Y,
                      images=image,
                      command=self.switch,
                      parameters=identifier
                      )

            button.y = (self.x - 70) - 24 * identifier

            self.buttons.append(button)
            _widgets.append(button)

    text = property(_get_text, _set_text)
    display = property(_get_display, _set_display)

    def switch(self, identifier):
        if len(self.buttons) > 1:
            self.text = self.buttons[identifier - 2].text
        elif len(self.buttons) == 1:
            self.text = self.buttons[0].text

    def reset_display(self):
        self.display = self.options

    def draw(self):
        self.button.x = self.right - 16

        for button in self.buttons:
            button.image.left = self.left
            button.label.x = self.left + 10

        self.component = self.entry

        if not self.displayed:
            self.display = self.options[:3]
            self.displayed = True

        if self.last_text is not self.entry.text and \
            self.entry.text:

            if self.entry.text == "" and \
                self.display is not self.options:
                self.display = self.options[:3]
                return

            self.display = []
            self.increment = (0, 0)
            # If filter removed show all data

            filtered_data = list()
            for item in self.options:
                if self.entry.text in item:
                    filtered_data.append(item)

            self.display = filtered_data[:3]
            self.last_text = self.entry.text


class Pushable(Widget):
    """Pushable widget to invoke and call commands. This is an extended version
    of the button and allows more modifications.

    TODO: add specifying border properties (left, right, top, bottom)
    """

    def __init__(
                 self, text, x, y, command=None, parameters=[],
                 images=(), font=default_font,
                 **kwargs
                ):

        """Initialize a button. A button has two components: an image and a
        label. You can customize the button's images and display by changing
        its normal_image, hover_image, press_image, and disable_image
        properties, but it is recommended to use the CustomButton widget.

        text - text to be displayed on the button
        x - x position of the button
        y - y position of the button
        command - command to be invoked when the button is called
        parameters - parameters of the callable when invoked
        image - image of the button as an image
        font - font of the button

        The last parameter is for parameters of the image.

        parameters: str, int, int, callable, list, tuple, Font, str
        """

        # A two-component widget:
        #     - Image
        #     - Label

        self.image = Image(images[0], x, y)
        self.label = Label(text, x, y, font=font)

        Widget.__init__(self)

        self.text = text
        self.x = x
        self.y = y
        self.command = command
        self.parameters = parameters
        self.font = font

        self.normal_image = load_texture(images[0])
        self.hover_image = load_texture(images[1])
        self.press_image = load_texture(images[1])
        self.disable_image = load_texture(images[1])

    def _get_x(self):
        """Get the x position of the button.

        returns: int
        """

        return self.image.x

    def _set_x(self, x):
        """Set the x position of the button.

        x - new x position of the button

        parameters: int
        """

        self.image.x = x

    def _get_y(self):
        """Get the y position of the button.

        returns: int
        """

        return self.image.y

    def _set_y(self, y):
        """Set the y position of the button.

        y - new y position of the button

        parameters: int
        """

        self.image.y = self.label.y = y

    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)

    def invoke(self):
        """Invoke the button. This switches its image to a pressed state
        calls the command with the specified parameters. If the button is
        disabled this will do nothing.
        """

        if self.disable or not self.command:
            return

        self.press = True

        if self.parameters:
            self.command(self.parameters)
        else:
            self.command()

    def draw(self):
        """Draw the button. The component of the button is the image, which takes
        all of the collision points.

        1. Image - background image of the button
        2. Label - text of the button
        """

        # Update Label properties

        self.label.text = self.text
        self.label.colors[0] = BLACK
        self.label.font = self.font

        self.component = self.image

    def on_press(self, x, y, buttons, modifiers):
        """The button is pressed. This invokes its command if the mouse button
        is the left one.

        TODO: add specifying proper mouse button in settings

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if buttons == MOUSE_BUTTON_LEFT:
            self.invoke()

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the
        button has focus.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int (32-bit), int (32-bit)
        """

        if keys == SPACE and self.focus:
            self.invoke()

        if isinstance(self.bindings, list):
            if keys in self.bindings:
                self.invoke()

        else:
            if self.bindings == keys:
                self.invoke()

    def update(self):
        """Update the button. This registers events and updates the button
        image.
        """

        self.image.normal_image = self.normal_image
        self.image.hover_image = self.hover_image
        self.image.press_image = self.press_image

        if self.disable:
            self.image.texture = self.disable_image

        # .update is not called for the Label, as it is uneccessary for the
        # Label to switch colors on user events.

        self.image.update()


class Shape(Widget):
    """Primitive drawing Shape. This is subclassed by all shapes. You may or
    may not want to subclass this."""

    def __init__(self):
        """Initialize a shape. When using a shape, be sure to create vertex
        lists from pyglet.graphics.vertex_list(), then draw them with pyglet
        rendering. Refer to the pyglet.shapes module for more information.

        A shape should not need an update function. Instead, put all of the
        properties as function-defined ones. This saves time and GPU. Also,
        instead of having x and y properties seperately, use a Point or a
        Pointlist. These are much faster performance-wise and more neater.

        A shape should look like one from the pyglet.shapes module, but should
        be drawn with pyglet rendering. It should subclass a widget or a shape,
        but that is not necessary. If you do, however, keep in mind that the
        events of a widget will be dispatched, like draw and update. You can
        also add the shape's vertex list to a pyglet.graphics.Batch() for
        faster performance and draw the batch instead of drawing the vertex
        list.

        You can use pyglet rendering like this:

        with arcade.get_window().ctx.pyglet_rendering():
            # Do something

        Alternatively the arcade.get_window() part can be replaced with the
        window property of the widget. This can save time.

        See https://pyglet.readthedocs.io/en/latest/modules/graphics/index.html
        """

        Widget.__init__(self)

    def draw(self):
        """Draw the shape with pyglet rendering. You may need to override this
        when creating your custom shapes.

        This was deprecated in favor of pyglet batching.
        """

        # with self.window.ctx.pyglet_rendering():
        #     self.shape.draw()

    def _get_alpha(self):
        """Get the alpha or transparency of the shape. You may need to override
        this if creating your own custom shapes. An alpha of zero is completely
        transparent and invisible. An alpha of 255 is completely opaque.

        returns: int
        """

        return self.shape.opacity

    def _set_alpha(self, alpha):
        """Set the alpha or transparency of the shape. You may need to override
        this if creating your own custom shapes. An alpha of zero is completely
        transparent and invisible. An alpha of 255 is completely opaque.

        alpha - new alpha

        parameters: int
        """

        if alpha > 255: alpha = 255
        if alpha < 0: alpha = 0

        self.shape.opacity = alpha

    alpha = property(_get_alpha, _set_alpha)

    def delete(self):
        """Delete the shape and its events. The shape is not drawn. You may
        need to override this if creating your own custom shapes.
        """

        self.shape.delete()


_Circle = Circle
_Ellipse = Ellipse
_Sector = Sector
_Line = Line
_Triangle = Triangle
_Star = Star
_Polygon = Polygon
_Arc = Arc


class Rectangle(Shape):
    """A rectangular shape."""

    def __init__(self, x, y, width, height, border=1,
                 colors=(WHITE, BLACK), label=None):

        """Create a rectangle.

        x - x position of rectangle
        y - y position of rectangle
        width - width of rectangle
        height - height of rectangle
        border - border width. The bigger this value is, the more three
                 dimensional effect there will be. If set to 0 there will be no
                 effect.
        colors - color of the rectangle in RGB as a tuple of three ints. There
                 are two tuples in a list, the first one for the shape fill and
                 the second one for the outline color. The default for this is:
                 [(255, 255, 255), (0, 0, 0)]
        label - draw a label over the rectangle. This must be a Label, not a
                string of its text.

        parameters: int, int, int, int, int, list [(RGB), (RGB)], Label
        """

        self.shape = BorderedRectangle(
                            x, y, width, height,
                            border, colors[0], colors[1],
                            batch=batch
                        )

        Shape.__init__(self) # Do this after defining self.shape

        self._point = Point(x, y)
        
        self.width = width
        self.height = height
        self.border = border
        self.colors = colors
        self.label = label
        
    def _get_point(self):
        """Get the Point of the rectangle.
        
        returns: Point
        """
        
        return self._point

    def _set_point(self, point):
        """Set the Point of the rectangle.
        
        point - new Point
        
        parameters: Point
        """
        
        self._point = point
        
        self.shape.x = point.x - self.width / 2
        self.shape.y = point.y - self.height / 2
        
        self.shape.height = self.height
        self.shape.color = self.colors[0]
        self.shape.border_color = self.color[1]
        self.shape.border = self.border

        if self.label:
            self.label.x = self.x + self.width / 2
            self.label.y = self.y + self.height / 2


class Circle(Shape):
    """A circular shape."""

    def __init__(self, x, y, radius, segments=None, color=BLACK):
        """Create a circle.

        x - x position of the circle
        y - y position of the circle
        radius - radius of the circle (see _set_radius)
        segments - number of segments of the circle. This is the number of
                   distinct triangles should the circle be formed from. If not
                   specified it is calculated with

                   max(14, int(radius ÷ 1.25))
        color - color of the circle in RGB as a tuple of three ints

        parameters: int, int, int, int, tuple (RGB)
        """

        if not segments:
            segments = max(14, int(radius / 1.25))

        self.shape = _Circle(x, y, radius, segments, color, batch=batch)

        Shape.__init__(self)

        self._point = Point(x, y)
        self.radius = radius
        self.color = color

    def _get_point(self):
        """Get the Point of the Circle.

        returns: Point
        """

        return self._point

    def _set_point(self, point):
        """Set the Point of the Circle. A Point and its documentation can be
        found at the geometry file.

        >>> circle.point = Point(3, 5)

        point - new Point

        parameters: int
        """

        self.shape.x = point.x
        self.shape.y = point.y

        self._point = point

    def _get_radius(self):
        """Get the radius of the circle (the distance from the center to the
        edge). The radius is the same throughout the whole circle.

        returns: int
        """

        return self.shape.radius

    def _set_radius(self, radius):
        """Set the radius of the circle (the distance from the center to the
        edge). The radius is the same throughout the whole circle.

        radius - new radius

        parameters: int
        """

        self.shape.radius = radius

    def _get_segments(self):
        """Get the number of segments in the circle. This is the number of
        distinct triangles that the circle is made from. On default, it is
        calculated by:

        max(14, int(radius ÷ 1.25))

        Note this must be used because you cannot draw a perfect circle on a
        pixeled monitor.

        returns: int
        """

        return self.shape._segments

    point = property(_get_point, _set_point)
    radius = property(_get_radius, _set_radius)
    segments = property(_get_segments)


class Ellipse(Shape):
    """An elliptical shape."""

    def __init__(self, x, y, a, b, color=BLACK):
        """Create a ellipse. This can also be called Oval.

        x - x position of the ellipse
        y - y position of the ellipse
        a - semi-major axes of the ellipse. If this and height are equal, a
            circle will be drawn. To draw a circle, set the a and b equal and
            divide their desired width and height by two for the radius.
        b - semi-minor axes of the ellipse. See a for more information.
        color - color of the ellipse in RGB as a tuple of three ints

        parameters: int, int, int, int, tuple (RGB)

        """

        self.shape = _Ellipse(x, y, a, b, color, batch=batch)

        Shape.__init__(self)

        self._point = Point(x, y)
        self.a = a
        self.b = b

    def _get_point(self):
        """Get the Point of the Ellipse.

        returns: Point
        """

        return self._point

    def _set_point(self, point):
        """Set the Point of the Ellipse.

        >>> self.ellipse.point = Point(5, 3)

        point - new Point

        parameters: Point
        """

        self.shape.x = point.x
        self.shape.y = point.y

        self._point = point

    def _get_a(self):
        """Get the semi-major axes of the ellipse.

        returns: int
        """

        return self.shape.a

    def _set_a(self, a):
        """Set the semi-major axes of the ellipse.

        a - new semi-minor axes

        parameters: int
        """

        self.shape.a = a

    def _get_b(self):
        """Get the semi-minor axes of the ellipse.

        returns: int
        """

        return self.shape.b

    def _set_b(self, b):
        """Set the semi-minor axes of the ellipse.

        b - new semi-minor axes

        parameters: int
        """

        self.shape.b = b

    def _set_ab(self, ab):
        """Set the width and height of the ellipse as a tuple.

        This is equivalant to:

        >>> ellipse.a = a
        >>> ellipse.b = b

        ab - new width and height

        parameters: tuple (width, height)
        """

        self.a = ab[0]
        self.b = ab[1]

    point = property(_get_point, _set_point)
    a = property(_get_a, _set_a)
    b = property(_get_b, _set_b)


Oval = Ellipse


class Sector(Shape):
    """A sector or pie slice of a circle."""

    def __init__(self, x, y, radius, segments=None,
                 angle=tau, start=0, color=BLACK):

        """Create a sector. A sector is essentially a slice of a circle. The
        sector class was created from the arc class in pyglet.

        x - x position of the sector
        y - y position of the sector
        radius - radius of the sector (see _set_radius)
        segments - number of segments of the sector. This is the number of
                   distinct triangles should the sector be formed from. If not
                   specified it is calculated with

                   max(14, int(radius ÷ 1.25))
        angle - angle of the sector in radians. This defaults to tau, which
                is approximately equal to 6.282 or 2π
        start - start angle of the sector in radians

        parameters: int, int, int, int, int
        """

        self.shape = _Sector(x, y, radius, segments, angle, start, color, batch=batch)

        Shape.__init__(self)

        self._point = Point(x, y)
        self.radius = radius
        self.segments = segments
        self.rotation = angle
        self.start = start
        self.color = color

    def _get_point(self):
        """Get the Point of the sector.

        returns: Point
        """

        return self._point

    def _set_point(self, point):
        """Set the Point of the sector.

        >>> sector.point = Point(5, 3)

        point - new Point

        parameters: Point
        """

        self._point = point

        self.shape.x = point.x
        self.shape.y = point.y

    def _get_radius(self):
        """Get the radius of the sector. This is the distance from the center of
        the circle to its edge.

        returns: int
        """

        return self.shape.radius

    def _set_radius(self, radius):
        """Set the radius of the sector. This is the distance from the center of
        the circle to its edge.

        radius - new radius

        parameters: int
        """

        self.shape.radius = radius

    def _get_start(self):
        """Get the start angle of the sector.

        returns: int
        """

        return self.shape.start_angle

    def _set_start(self, start):
        """Set the start angle of the sector.

        start - new start angle

        parameters: int
        """

        self.shape.start = start

    def _get_segments(self):
        """Get the number of segments in the sector. This is the number of
        distinct triangles that the sector is made from.

        returns: int
        """

        return self.shape._segments

    def _set_segments(self, segments):
        """Set the number of segments in the sector. This is the number of
        distinct triangles that the sector is made from. On default, it is
        calculated by:

        max(14, int(radius ÷ 1.25))

        Note this must be used because you cannot draw a perfect sector on a
        pixeled monitor.

        parameters: int
        """

        self.shape._segments = segments
        self.shape._update_position()

    point = property(_get_point, _set_point)
    radius = property(_get_radius, _set_radius)
    start = property(_get_start, _set_start)
    segments = property(_get_segments, _set_segments)


class Line(Shape):
    """A line shape."""

    def __init__(self, point1, point2, width=1, color=BLACK):
        """Create a line. Unlike other shapes, a line has a start point and an
        endpoint.

        point1 - first start coordinate pair of line
        point2 - second end coordinate pair of line
        width - width, weight or thickness
        color - color of the line in RGB in a tuple of three ints

        parameters: Point, Point, int, tuple (RGB)
        """

        # Normally we don't format like this. But it makes it neater and more
        # consistent when we use three lines instead of one.

        self.shape = _Line(point1.x, point1.y,
                           point2.x, point2.y,
                           width, color, batch=batch)

        Shape.__init__(self)

        self._point1 = point1
        self._point2 = point2
        self.width = width
        self.color = color

    def _get_point1(self):
        """Get the first Point of the line.

        returns: Point
        """

        # We can't return thea new Point, as it would have a different id

        return self._point1

    def _set_point1(self, point1):
        """Set the first Point of the line.

        point1 - new Point

        parameters: Point
        """

        self._point1 = point1

        self.shape.x1 = point1.x
        self.shape.y1 = point1.y

    def _get_point2(self):
        """Get the second Point of the line.

        returns: Point
        """

        # We can't return thea new Point, as it would have a different id

        return self._point2

    def _set_point2(self, point2):
        """Set the second Point of the line.

        point1 - new Point

        parameters: Point
        """

        self._point2 = point2

        self.shape.x2 = point2.x
        self.shape.y2 = point2.y

    def _get_width(self):
        """Get the width of the line.

        returns: int
        """

        return self.shape._width

    def _set_width(self, width):
        """Set the width of the line. This has an alias called thickness and
        another called weight.

        width - new width

        parameters: int
        """

        self.shape._width = width

    point1 = property(_get_point1, _set_point1)
    point2 = property(_get_point2, _set_point2)
    width = property(_get_width, _set_width)

    # Alias
    thickness = width
    weight = width


class Triangle(Shape):
    """A triangular shape."""

    def __init__(self, points, color=BLACK):
        """Create a triangle.

        points - pointlist of the triangle
        color - color of of the triangle in RGB as a tuple of three ints

        parameters: Pointlist, tuple (RGB)
        """

        self.shape = _Triangle(*points, color, batch=batch)

        Shape.__init__(self)

        self._points = PointList(points)
        self.color = color

    def _get_points(self):
        """Get the points of the triangle. This is listed as point1, point2,
        and point3, which each have their x and y coordinates.

        returns: Pointlist
        """

        return self._points

    def _set_points(self, points):
        """Set the points of the triangle. This is listed as point1, point2,
        and point3, which each have their x and y coordinates.

        Asserts that the pointlist is correct.

        points - new pointlist of triangle

        parameters: Pointlist
        """

        assert len(points) > 3, (
            "The points of the Pointlist specified must be labeled as point1,"
            "point2, and point3."
        )

        self._points = points

        self.shape.x1 = points[0].x
        self.shape.y1 = points[0].x
        self.shape.x2 = points[1].x
        self.shape.y2 = points[1].x
        self.shape.x3 = points[2].x
        self.shape.y3 = points[2].x

    points = property(_get_points, _set_points)


class Star(Shape):

    def __init__(
                 self, x, y, outer, inner, spikes=5,
                 rotation=0, color=BLACK, opengl_error=True
                ):
        """Create a star.

        x - x position of star
        y - y position of star
        outer - outer diameter of spike
        inner - inner diameter of spike
        spikes - number of spikes. Defaults to 5 (a plain star).
        rotation - rotation of the star in degrees. A rotation of 0 degrees
                   will result in one spike lining up with the x axis in
                   positive direction.
        color - color of the star in RGB as a tuple of three ints. Defaults to
                BLACK.
        opengl_error - checks whether or not the outer diameter is greater
                       than the inner diameter. This is not supposed to be like
                       this, but results in interesting patterns. Defaults to
                       True.

        parameters: int, int, int, int, int, int, tuple (RGB), bool
        """

        if opengl_error:
            assert outer > inner, (
                "The outer diameter of the star must be greater than its inner "
                "diameter. You can turn this off by setting the opengl_error "
                "parameter to False. Switching this off is programmatically "
                "incorrect, but results in interesting patterns."
            )

        self.shape = _Star(x, y, outer, inner, spikes, rotation, color, batch=batch)

        Shape.__init__(self)

        self.x = x
        self.y = y
        self.outer = outer
        self.inner = inner
        self.spikes = spikes
        self.rotation = rotation
        self.color = color

    def _get_outer(self):
        """Get the outer diameter of each spike in the star.

        returns: int
        """

        return self.shape.outer_radius

    def _set_outer(self, diameter):
        """Set the outer diameter of each spike in the star.

        parameters: int
        """

        self.shape.outer_radius = diameter

    def _get_inner(self):
        """Get the inner diameter of each spike in the star.

        returns: int
        """

        return self.shape.inner_radius

    def _set_inner(self, diameter):
        """Set the inner diameter of each spike in the star.

        parameters: int
        """

        self.shape.inner_radius = diameter

    def _get_inner(self):
        """Get the number of spikes in the star. This typically should be set
        to five.

        returns: int
        """

        return self.shape.num_spikes

    def _set_spikes(self, spikes):
        """Set the number of spikes in the star.

        parameters: int
        """

        self.shape.num_spikes = spikes

    outer = property(_get_outer, _set_outer)
    inner = property(_get_inner, _set_inner)
    spikes = property(_get_inner, _set_inner)

    def update(self):
        self.shape.x = self.x
        self.shape.y = self.y
        # self.shape.num_spikes = self.spikes
        self.shape.rotation = self.rotation
        self.shape.color = self.color


class Polygon(Shape):

    def __init__(self, *coordinates, color=BLACK):
        self.shape = _Polygon(*coordinates, color, batch=batch)

        Shape.__init__(self)

        self.coordinates = list(coordinates)
        self.color = color

    def update(self):
        self.shape.coordinates = self.coordinates
        self.shape.color = self.color


class Arc(Shape):

    def __init__(self, x, y, radius, segments=None,
                 angle=tau, start=0, closed=False, color=BLACK):

        self.shape = _Arc(x, y, radius, segments, angle, start, closed, color, batch=batch)

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
            self, width, height, title
        )

        from pyglet.image import load

        from file import blank1, blank2

        global shapes

        shapes = ShapeElementList()

        self.set_icon(load(blank1), load(blank2))
        self.set_exclusive_keyboard()

        container.window = self

        self.label = Label(
            "<b>Bold</b>, <i>italic</i>, and <u>underline</u> text.",
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
            command=self.click,
            link="office.com")

        self.toggle = Toggle(
            "Show fps",
            250,
            350)

        self.slider = Slider(
            None,
            250,
            300,
            size=100)

        self.entry = Entry(
            300,
            160,
        )
            #["apple", "banana", "mango", "orange"])

        # self.circle = Star(
        #     100,
        #     150,
        #     30,
        #     1000,
        #     10000,
        #     color=BLUE_YONDER,
        #     opengl_error=False)

        self.circle = Star(
            100, 150,
            50, 29000000000000005,
            spikes=6, color=BLUE_YONDER,
            opengl_error=False
        )
        for i in range(1, 10):
            Label(
            None,
            10,
            80)

        self.button.bind(ENTER)

        self.background_color = (255, 255, 255, 50)

    def click(self):
        self._label.text = self.entry.text

    def on_draw(self):
        self.clear()
        self.set_caption(f"{int(get_fps())} fps")

        container.draw()

        self.label.UPDATE_RATE = self.slider.value + 1 # Compensate for zero

        if self.toggle.value:
            self.label.text = f"{int(get_fps())} fps"
        else:
            self.label.text = "<b>Bold</b>, <i>italic</i>, and <u>underline</u> text in <font color='red'>HTML</font>."

        self.slider.text = str(int(self.slider.value))


if __name__ == "__main__":
    window = MyWindow(" ", 500, 400)

    from pyglet.app import run
    run(1/2000)
