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
import string
import atexit
import os
import re
import urllib
# And this for the pymongo version
import pymongo

#GUI

class ManualTextClassifierSingle(object):
    def __init__(self, items, labels=[0,1], output=sys.stdout,
                 winx=1280, winy=880):
        # items is a list of 2+-tuples containing an identifier (such as a
        # URL) for the output, the content itself, and any number of optional
        # additional fields to be stored in the output csv. This could 
        # usefully include, for example, Content-Type if it is wanted to
        # preserve this in the output to help train a classifier. 
        # output is an output file handle
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
        self.buttons = []

        self._setup_root_window(winx, winy)
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

    def _setup_root_window(self, winx, winy):
        self.set_root_window_size(winx, winy)
        self.root.wm_title("Classifier")

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
        self._set_text_content()

    def _set_text_content(self):
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
            self.root.destroy()
            self.root.quit()

    def write_result(self, item, result):
        self.output.write(item[0])
        self.output.write(",")
        self.output.write(result)
        if len(item) > 2:
            for o in item[2:]:
                self.output.write(",")
                self.output.write(str(o))
        self.output.write("\n")
    def on_button_click(self, result):
        print result
        self.write_result(self.items[self.idx], result)
        self.update_content()


class ManualHTMLClassifierSingle(ManualTextClassifierSingle):
    def _get_content_object(self):
        return TkHtml.Html(self.root)

    def clear_content(self):
        self.content.clear()

    def set_content(self):
        self._set_html_content()

    def _set_html_content(self):
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
    def __init__(self, *args, **kw):
        self._tempfns = []
        atexit.register(self._close_tempfiles)
        super(ManualBrowserClassifierSingle, self).__init__(*args, **kw)

    def _get_content_object(self):
        # No window object in that sense
        raise NotImplementedError

    def _setup_root_window(self, winx, winy):
        (super(ManualBrowserClassifierSingle,self).
            _setup_root_window(winx, winy))
        # As we'll keep spawning web browser windows, stay on top
        self.root.attributes("-topmost", True)

    def _setup_content(self):
        self.content = webbrowser.get()

    def set_title(self, t):
        # No title
        pass

    def clear_content(self):
        raise NotImplementedError

    def set_content(self):
        self._set_browser_content()

    def _set_browser_content(self, origurl = None, page_content=None):
        if not origurl:
            origurl=self.items[self.idx][0]
        if not page_content:
            page_content= self.items[self.idx][1]
        # Mangle URL into filename, so it shows up in the titlebar.
        # Take the first 100 characters, to avoid hitting OS limits.
        trantab = string.maketrans('/#* ','____')
        suf= '__'+urllib.unquote(origurl).translate(trantab)[:100]+'.html'
        with tempfile.NamedTemporaryFile(suffix=suf, delete=False) as fh:
            self._tempfns.append(fh.name)
            fh.write(page_content.encode('utf-8'))
            url = 'file://'+fh.name
            self.content.open(url, new=0, autoraise=False)

    def _close_tempfiles(self):
        for fn in self._tempfns:
            try:
                os.unlink(fn)
            except OSError:
                print "File", fn, "already deleted."

class ManualWaybackClassifierSingle(ManualBrowserClassifierSingle):
    """ Same as ManualBrowserClassifier, but uses a local Wayback Machine
        installation to do the display of content. As a result, the content
        part of the items tuple is irrelevant and can be None to save
        memory if desired."""
    def __init__(self, wburl='http://localhost:8080/wayback/', *args, **kw):
        self.wburl = wburl
        super(ManualWaybackClassifierSingle, self).__init__(*args, **kw)

    def set_content(self):
        self._set_wayback_content()

    def _set_wayback_content(self):
        # XXX: Make this configurable (via __init__?)
        url = self.items[self.idx][0]
#        url = re.sub(r'^https?://', '', url)
        url = self.wburl+url
        self.content.open(url, new=0, autoraise=False)

class ManualWaybackPlusMongoDBClassifierSingle(ManualWaybackClassifierSingle):
    """ Same as Manual WaybackClassifier, but with a MongoDB instance as a
        fallback source of data."""
    def __init__(self, mongodb, collection,
        client=pymongo.mongo_client.MongoClient(), *args, **kw):
        self.mongoclient = client
        self.db = pymongo.database.Database(self.mongoclient, mongodb)
        self.collection = pymongo.collection.Collection(self.db, collection)

        super(ManualWaybackPlusMongoDBClassifierSingle, self).__init__(*args, **kw)
        self.fallbackbutton = Tkinter.Button(self.root,
                    text='Load from MongoDB',
                    command=self._set_mongo_content)
        self.fallbackbutton.grid(column=1, row=len(self.buttons)+1, sticky="SW", padx=10)
    
    def _set_mongo_content(self):
        # Get fallback content from MongoDB
        url = self.items[self.idx][0]
        try:
            # This is a bit horrid.
#            page_content = u'<html><body><pre>'+unicode(self.collection.find_one(url)['value'], errors='ignore')+u'</pre></body></html>'
            page_content = ((u'<html><head><meta http-equiv="Content-Type" '
                             u'content="text/html;charset=UTF-8"><head>'
                             u'<body><pre>')+
                             self.collection.find_one(url)['value']+
                             u'</pre></body></html>')
        except Exception as e:
            page_content = "Unable to fetch text from MongoDB for "+url+"."
            raise e
        finally:
            self._set_browser_content(page_content=page_content)


