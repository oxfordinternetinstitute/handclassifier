#!/usr/bin/python
#NER Project
#Hand classifier
#FIXME: Outdated
#This program takes a fixed number of stories, at random
#from a fixed date range within the dataset, also chosen at random
#the interface presents each article next to each other article once
#and asks for human judgment about whether or not the articles are related
#
#Copyright 2013-2014, Jonathan Bright and Tom Nicholls
#
# TODO: Open viewport on HTML widget starting at a header?
# TODO: Keyboard control: Numbers to select categories, pgup/dn, arrows
# TODO: Strip comments/JS/Nonsense before giving to the HTML widget?

#Params, imports
import Tkinter
# This is a local wrapper, not a published library
import TkHtml
import sys
# These needed for the browser version
import webbrowser
import tempfile
import atexit

#GUI

class ManualTextClassifierSingle:
    def __init__(self, items, labels=[0,1], output=sys.stdout,
                 winx=1280, winy=880):
        # items is a list of 2-tuples containing an identifier (such as a URL)
        # for the output, and the content itself
        # output is a file handle to output to
        # labels is a list of classification options to select from
        self.output = output
        self.items = items
        self.idx = -1
        self.numclassified = {}
        self.labels = labels
        if len(labels) < 2:
            raise Exception("Classifier needs at least 2 labels")
        for label in self.labels:
            self.numclassified[label] = 0
        self.root = Tkinter.Tk()
        self.set_root_window_size(winx, winy)
        self.buttons = []

        self._setup_content()
        self.update_content()

        for i, label in enumerate(labels):
            self.buttons.append(
                Tkinter.Button(
                    self.root,
                    text=label,
                    command= lambda j=label: self.on_button_click(j)))
            self.buttons[-1].grid(column=1, row=1+i, sticky="SW", padx=10)

    def _setup_content(self):
        # Article title / URL label
        self.text_title = Tkinter.Label(self.root, text="", anchor="w",
                                    fg="black", justify="left",
                                    font=("Helvetica", 16),
                                    width=90)
        self.text_title.grid(column=0,row=0, sticky='EW', padx=10)
        # Main box with content to classify
        self.content = self._get_content_object()
        self.content.grid(column=0, row=1, rowspan=20, sticky='NSEW', padx=10)
        self._add_scrollbar()
        self.scrollbar = Tkinter.Scrollbar(self.root,
                                           command=self.content.yview)
        self.scrollbar.grid(column=0, row=1, rowspan=20, sticky='NSE')
        self.content.config(yscrollcommand=self.scrollbar.set)

    def _get_content_object(self):
        return Tkinter.Text(self.root, wrap=Tkinter.WORD)

    def set_root_window_size(self, winx, winy):
        # FIXME: This is all a horrible hack.
        # self.root.geometry(''+str(winx)+'x'+str(winy))
        self.root.rowconfigure(1, minsize=30)
        allocated = 30
        for i in range(2, 1+len(self.labels)):
            self.root.rowconfigure(i, minsize=20)
            allocated += 20
        size = (winy - allocated) / (20 - len(self.labels))
        print "row size =", size
        for i in range(1+len(self.labels),21):
            self.root.rowconfigure(i, minsize=size)

    def set_title(self, t):
        self.text_title.config(text=t)
        

    def clear_content(self):
        self.content.delete(1.0, Tkinter.END)

    def set_content(self):
        self.clear_content
        self.content.insert(Tkinter.INSERT, self.items[self.idx][1])

    def update_content(self):
        self.idx += 1
        try:
            print self.idx, self.items[self.idx][0]
            self.set_title(self.items[self.idx][0])
            self.set_content()
        except IndexError:
            print "Finished!"
            self._shutdown_classifier()

    def write_result(self, identifier, result):
        self.output.write(identifier)
        self.output.write(",")
        self.output.write(result)
        self.output.write("\n")
       
    def on_button_click(self, result):
        print result
        self.write_result(self.items[self.idx][0], result)
        self.update_content()

    def _shutdown_classifier(self):
        


class ManualHTMLClassifierSingle(ManualTextClassifierSingle):
    def _get_content_object(self):
        return TkHtml.Html(self.root)

    def clear_content(self):
        self.content.clear()

    def set_content(self):
        new_content = self.items[self.idx][1]
        self.clear_content()
        # FIXME: Fairly grotty hack to handle non-HTML content
        if '<body' not in new_content.lower():
            print "<body not found."
            print new_content
            self.content.parse('<html><body>'+new_content+'</html></body>')
        else:
            self.content.parse(new_content)


class ManualBrowserClassifierSingle(ManualTextClassifierSingle):
    def _get_content_object(self):
        # No window object in that sense
        raise NotImplementedError

    def _setup_content(self):
        self.content = webbrowser.get()
        self._tempfns = []

    def set_title(self, t):
        # No title
        pass

    def clear_content(self):
        raise NotImplementedError

    def set_content(self):
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as fh:
            self._tempfns.append(fh.name)
            fh.write(self.items[self.idx][1])
            url = 'file://'+fh.name
        self.content.open(url, autoraise=False)

    @atexit.register
    def _close_tempfiles(self):
        for fn in self._tempfns:
            try:
                os.unlink(fn)
            except OSError:
                print "File", fn, "already deleted."

