# -*-mode: tcl; fill-column: 75; tab-width: 8; coding: iso-latin-1-unix -*-
#
#	$Id$
#

"""TkHtml

Wrapper for the TkHtml widget from http://www.hwaci.com.
"""

import Tkinter

__require__ = 1
__tk_call__ = None

# This function is not implemented yet.
token_append_implemented = 0

def __setup_globals(master):
    global __require__, __tk_call__
    if __require__:
        master.tk.call("package","require","Tkhtml")
        __tk_call__ = master.tk.call
        __require__ = None

def reformat(from_, to, text):
    "Reformat a string to another representation: plain, http, url, html"
    if __require__: __setup_globals(Tkinter._default_root)
    return __tk_call__("html", "reformat", from_, to, text)

def uri_join(scheme, authority, path, query, fragment):
    "Join the five components of the URI together."
    if __require__: __setup_globals(Tkinter._default_root)
    return __tk_call__("html", "urljoin", scheme, authority, path, query, fragment)

def uri_split(uri):
    "Takes an URI and splits it into it's five main components."
    if __require__: __setup_globals(Tkinter._default_root)
    return __tk_call__("html", "urlsplit", uri)

class Html(Tkinter.Widget):
    """Html widget"""
    def __init__(self, master=None, cfg={}, **kw):
        master.tk.call("package", "require", "Tkhtml")
        Tkinter.Widget.__init__(self, master, 'html', cfg, kw)

    def parse(self, text):
        """Add the given HTML-TEXT to the end of any text previously
        received through the parse command and parses as much of the
        text as possible into tokens.

        Afterwards, the display is updated to show the new tokens, if
        they're visible.
        """
        self.tk.call(self._w, "parse", text)

    def clear(self):
        "Clear the widget."
        self.tk.call(self._w, "clear")

    def href(self, x, y):
        "Returns the href at coordinates X, Y"
        return self.tk.call(self._w, "href", x, y)

    def index(self, index, count=None, units=None):
        "Translates 'index' into it's cannonical form."
        cmd = (index,)
        if count and units:
            cmd = cmd + (count,units)
        return self.tk.call(self._w, "index", *cmd)

    def insert(self, index):
        """Causes insertion point to be position immediately
        after the character at 'index'."""
        return self.tk.call(self._w, "insert", index)

    def names(self):
        """This command causes the widget to scan the entire text of
        the document looking for tags of the form:

            <a name=...>

        It returns a list of values of the 'name=...' fields.

        The vertical position of the widget can  be moved to any of
        these names using the 'WIDGET yview NAME' command described below.
        """
        return self.tk.call(self._w, "names")

    def resolver(self, *args):
        """The resolver specified by the -resolvercommand option is called
        with the base URI of the document followed by the remaining
        arguments to this command. The result of this command is the
        result of the -resolvercommand script.
        """
        return self.tk.call(self._w, "resolver", *args)

    def selection(self, subcommand, *args):
        """The selection() widget command is used to control the selection.

        WIDGET selection clear
            Clear the current selection.

        WIDGET selection set START END
            Change the selection to the text between the START and
            END indices.
        """
        return self.tk.call(self._w, "selection", *args)

    def selection_clear(self):
        "Clear the current selection."
        return self.selection("clear")

    def selection_set(self, start, end):
        "Set the selection to the text between start and end indices."
        return self.selection("set", start, end)

    def text(self, *args):
        """There are several token commands. They all have the common
        property that they directly manipulate the text which is currently
        displayed. This could be used to build a WYSIWYG html editor.
        """
        return self.tk.call(self._w, "text", *args)

    def text_ascii(self, index1, index2):
        """Returns plain ascii text that represents all characters
        between index1 and index2. Formatting tags are omitted.
        The index1 character is included but index2 is excluded.
        """
        return self.text("ascii", index1, index2)

    def text_delete(index1, index2):
        """All text from index1 up to --but not including-- index2 is
        removed and the display is updated accordingly.
        """
        return self.text("delete", index1, index2)

    def text_html(index1, index2):
        """Returns HTML text that represents all characters and formatting
        tags between index1 and index2, excluding the character at index2.
        """
        return self.text("html", index1, index2)

    def text_insert(self, index, text):
        """Inserts one or more characters immediately before the character
        whose index is given.
        """
        return self.text("insert", index, text)

    def token(self, subcommand, *args):
        """There are several token commands. They all have the common
        property that they involve the list of tokens into which the HTML
        text is parsed.

        Some of the following subcommands make use of indices. The character
        number of these indices is ignored, since these commands only deal
        with tokens.
        """
        return self.tk.call(self._w, "token", subcommand, *args)

    def token_append(self, tag, *args):
        "The token is appended to the current list of tokens."
        return self.token("append", tag.upper(), *args)

    def token_delete(self, index1, index2=None):
        """The token at the given index is deleted; if the second index
        is specified, then the range of tokens is deleted (second index
        inclusive).
        """
        if index2: return self.token("delete", index1, index2)
        return self.token("delete", index1)

    def token_find(self, tag):
        """Locats all tokens with the given tag and returns a list of
        them all. Each element of the list contains the index of the
        token and the token's arguments.
        """
        return self.token("find", tag)

    def token_get(self, index1, index2=None):
        """Returns a list of tokens in the range index1 through index2;
        each element of the list consists of the token tag followed
        by it's arguments.
        """
        if index2: return self.token("get", index1, index2)
        return self.token("get", index1)

    def token_handler(self, tag, handler=None):
        """This command allows special processing to occur for selected
        tokens in the HTML input stream. The tag argument is either "Text"
        or "Space", or the name of an HTML tag ("H3", "/A", etc).

        If a none-None function is specified for the handler, then when
        instances of that tag are encountered by the parser, the parser calls
        the corresponding function instead of appending the token to the
        end of the token list. Before calling the function, two arguments
        are appended:
        
            1. The tag (ex: "H3", "/TABLE", etc)
            2. A list of name/value pairs describing all tag arguments.

        An empty handler causes the default processing to occur for the tag.
        If the function argument is ommitted altogether, then the current
        value for the token handler for the given tag is returned.

        Only one handler for each token type may be defined. If a new handler
        for a given tag is set, then the previous handler is replaced.
        """
        if not handler: return self.token("handler", tag)
        if handler in ("", "{}"):
            # Delete the current handler for this tag.
            return self.token("handler", tag, handler)
        elif callable(handler):
            name = self.register(handler)
            self.token("handler", tag, name)
        else:
            raise ValueError("handler must be None, '' or callable.")

    def token_handler_delete(self, tag):
        "Deletes a handler for a token type."
        return self.token("handler", tag, "{}")

    def token_insert(self, index, tag, *arguments):
        """Inserts a single token given by tag and arguments into the
        token list immediately before the token given by index.
        """
        return self.token("insert", index, *arguments)

    def xview(self, *args):
        "Used to control horizontal scrolling."
        if args: return self.tk.call(self._w, "xview", *args)
        coords = map(float, self.tk.call(self._w, "xview").split())
        return tuple(coords)

    def xview_moveto(self, fraction):
        """Adjusts horizontal position of the widget so that fraction
        of the horizontal span of the document is off-screen to the left.
        """
        return self.xview("moveto", fraction)

    def xview_scroll(self, number, what):
        """Shifts the view in the window according to number and what;
        number is an integer, and what is either 'units' or 'pages'.
        """
        return self.xview("scroll", number, what)

    def yview(self, *args):
        "Used to control the vertical position of the document."
        if args: return self.tk.call(self._w, "yview", *args)
        coords = map(float, self.tk.call(self._w, "yview").split())
        return tuple(coords)

    def yview_name(self, name):
        """Adjust the vertical position of the document so that the tag
        <a name=NAME...> is visible and preferably near the top of the window.
        """
        return self.yview(name)

    def yview_moveto(self, fraction):
        """Adjust the vertical position of the document so that fraction of
        the document is off-screen above the visible region.
        """
        return self.yview("moveto", fraction)

    def yview_scroll(self, number, what):
        """Shifts the view in the window up or down, according to number and
        what. 'number' is an integer, and 'what' is either 'units' or 'pages'.
        """
        return self.yview("scroll", number, what)

##
##  FINIS
##


class TestApp:
    def __init__(self):
        import Tkinter, tkFileDialog, TkHtml
        root = self._root = Tkinter.Tk()
        root.title("Html widget test")

        root["menu"] = mb = self._mb = Tkinter.Menu(root)
        file = self._file = Tkinter.Menu(mb)
        mb.add_cascade(menu=file, label="File", underline=0)

        html = self._html = TkHtml.Html(root)
        vsb = self._vsb = Tkinter.Scrollbar(root, orient="v", command=html.yview)
        html.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y", expand="yes")
        html.pack(side="left", fill="both", expand="yes")

        self._dialog = tkFileDialog.Open(root)

        # Bind some menu options.
        file.add_command(label="Default", underline=0, command=self.default)
        file.add_command(label="Open", underline=0, command=self.open)
        file.add_command(label="Clear", underline=0, command=html.clear)
        file.add_separator()
        file.add_command(label="Quit", underline=0, command=root.destroy)

        # Create some image placeholders.
        biggray = Tkinter.PhotoImage(data="R0lGODdhPAA+APAAALi4uAAAACwAAA"
                        "AAPAA+AAACQISPqcvtD6OctNqLs968+w+G4kiW5omm6sq27g"
                        "vH8kzX9o3n+s73/g8MCofEovGITCqXzKbzCY1Kp9Sq9YrNFg"
                        "sAO///")

        smallgray = Tkinter.PhotoImage(data="R0lGODdhOAAYAPAAALi4uAAAACwA"
                        "AAAAOAAYAAACI4SPqcvtD6OctNqLs968+w+G4kiW5omm6sq2"
                        "7gvH8kzX9m0VADv/")

        nogifbig = Tkinter.PhotoImage(data="R0lGODdhJAAkAPEAAACQkADQ0PgAA"
                        "AAAACwAAAAAJAAkAAACmISPqcsQD6OcdJqKM71PeK15AsSJH"
                        "0iZY1CqqKSurfsGsex08XuTuU7L9HywHWZILAaVJssvgoREk"
                        "5PolFo1XrHZ29IZ8oo0HKEYVDYbyc/jFhz2otvdcyZdF68qe"
                        "Kh2DZd3AtS0QWcDSDgWKJXY+MXS9qY4+JA2+Vho+YPpFzSji"
                        "TIEWslDQ1rDhPOY2sXVOgeb2kBbu1AAADv/")

        nogifsm = Tkinter.PhotoImage(data="R0lGODdhEAAQAPEAAACQkADQ0PgAAA"
                        "AAACwAAAAAEAAQAAACNISPacHtD4IQz80QJ60as25d3idKZd"
                        "R0IIOm2ta0Lhw/Lz2S1JqvK8ozbTKlEIVYceWSjwIAO///")

        tl = Tkinter.Toplevel(root)
        for img in (biggray, smallgray, nogifbig, nogifsm):
            Tkinter.Label(tl, image=img).pack()

    def default(self):
        self._html.clear()
        self._html.parse(open(r"tkhtml-spec.html").read())

    def open(self):
        file = self._dialog.show()
        if file:
            self._html.clear()
            self._html.parse(open(file).read())

if __name__ == "__main__":
    test = TestApp()

