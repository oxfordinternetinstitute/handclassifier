#!/usr/bin/python2
"""A quick-and-dirty python GUI for facilitating hand-classifying text and
HTML content into arbitrary categories.

This is still rudimentary and the API should not be considered stable.

The basic framework is to use a Tkinter gui window to present the possible
classes for each document, with the document itself presented in another
window:

* ManualTextClassifierSingle presents text in a Tkinter window
* ManualBrowserClassifierSingle uses the system web browser to render content
* ManualWaybackClassifierSingle looks up the wanted document by URL in an
  OpenWayback installation (http://www.netpreserve.org/openwayback) using the
  system web browser
* ManualWaybackPlusMongoDBClassifierSingle is equivalent to the Wayback
  classifier, but adds a fallback "Load from MongoDB" button to pull the text
  from a MongoDB instance

This code is largely by Tom Nicholls, based upon earlier work by Jonathan
Bright. 

Copyright 2013-2015, Tom Nicholls and Jonathan Bright
"""

#Params, imports
import Tkinter
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
    """Hand classify a set of text items using Tkinter.

    items -- a list of 2+-tuples containing an identifier (such as a
        URL) for the output, the content itself, and any number of optional
        additional fields to be stored in the output csv. This could 
        usefully include, for example, Content-Type if it is wanted to
        preserve this in the output to help train a classifier. 
    labels -- a list of classification options to select from (default: [0,1])
    output -- an output file handle (default: stdout)
    winx -- the desired width of the classification window in pixels (default:
        1280). Currently not used. 
    winy -- the desired height of the classification window in pixels (default:
        880).
    nprevclass -- the number of previously classified objects (in case
        of batch operation) (default: 0)
    callback -- a function to be called (with parameters identifier,
        classification) once a determination is made (default: None).  

    This class is also used as the base class for other classifiers in this
    module."""
    def __init__(self, items, labels=[0,1], output=sys.stdout,
                 winx=1280, winy=880, nprevclass=0, callback=None):
        self.output = output
        self.items = items
        self.idx = -1
        self.numclassified = {}
        self.nprevclass = nprevclass
        self._callback = callback
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
                    command= lambda j=label: self._on_button_click(j)))
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
        """Set the size of the root classifier window.

        FIXME: Currently ignores winx and uses an alternative algorithm to lay
            out the window.

        winx -- width (px)
        winy -- height (px)
        """
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
        """Set the content window title.

        t -- title"""
        self.text_title.config(text=t)

    def clear_content(self):
        """Clear the content window."""
        self.content.delete(1.0, Tkinter.END)

    def set_content(self):
        """(Indirectly) fill the content window with the next item."""
        self._set_text_content()

    def _set_text_content(self):
        self.clear_content
        self.content.insert(Tkinter.INSERT, self.items[self.idx][1])

    def update_content(self):
        """Update the content window with the next item to be classified."""
        self.idx += 1
        try:
            self.set_title(self.items[self.idx][0])
            self.set_content()
        except IndexError:
            print "Finished!"
            self.root.destroy()
            self.root.quit()

    def write_result(self, item, result, sep=','):
        """Write a hand classification to the output file as a CSV line.

        The written line is of the form:
            item[0],result,[item[2][item[3][...]]] (though with the separator
            given by sep)
        The output stream is flushed to prevent lost classifications.

        item -- one element of the items list passed to the class constructor.
            This will be a 2+-tuple containing an identifier (such as a
            URL) for the output, the content itself, and any number of optional
            additional fields to be stored in the output csv. This could 
            usefully include, for example, Content-Type if it is wanted to
            preserve this in the output to help train a classifier. 
        result -- a textual category
        sep -- the CSV separator (default: ',')
        """
        if self.nprevclass > 0:
            print self.idx, '/', self.idx+self.nprevclass, self.items[self.idx][0]
        else:
            print self.idx, self.items[self.idx][0]
 
        self.output.write(item[0])
        self.output.write(sep)
        self.output.write(result)
        if len(item) > 2:
            for o in item[2:]:
                self.output.write(sep)
                self.output.write(str(o))
        self.output.write("\n")
        self.output.flush()
    def _on_button_click(self, result):
        """Handle a click on one of the result buttons.

        Normally run as a callback, writes the new result and triggers the
        content window to be updated with the next item of content. Also calls
        the callback function given to the class constructor if present.

        result -- the category to apply to the current item
        """ 
        print result
        itemlabel = self.items[self.idx]
        self.write_result(itemlabel, result)
        if self._callback:
            self._callback(itemlabel, result)
        self.update_content()


class ManualBrowserClassifierSingle(ManualTextClassifierSingle):
    """Hand classify a set of web items using Tkinter and the system web
    browser.

    This is a subclass of ManualHTMLClassifierSingle. It overrides
    set_content() to display web content in the system browser rather than
    in a TkHtml window.

    It does not provide clear_content(), as this is not possible using
    python's webbrowser interface, and has a null implementation of
    set_title() for similar reasons."""
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
        """Silently fails to change the content window title -- this is not
        possible through a web browser as we do not control the title."""
        pass

    def clear_content(self):
        """Not implemented -- cannot do this with a web browser"""
        raise NotImplementedError

    def set_content(self):
        """(Indirectly) load the web browser with the next item."""
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
    """Hand classify a set of HTML items using an OpenWayback installation,
    Tkinter and the system web browser.

    This is a subclass of ManualBrowserClassifierSingle. It overrides
    set_content() to retrieve the HTMl content from OpenWayback rather than
    the items list passed to the constructor. As a result, the content
    part of the items tuple is irrelevant and can be None to save
    memory if desired.

    wburl -- the URL of the OpenWayback installation to be used (default:
        http://localhost:8080/wayback/
    """
    def __init__(self, wburl='http://localhost:8080/wayback/', *args, **kw):
        self.wburl = wburl
        super(ManualWaybackClassifierSingle, self).__init__(*args, **kw)

    def set_content(self):
        """(Indirectly) load the web browser with the next item."""
        self._set_wayback_content()

    def _set_wayback_content(self):
        # XXX: Make this configurable (via __init__?)
        url = self.items[self.idx][0]
#        url = re.sub(r'^https?://', '', url)
        url = self.wburl+url
        self.content.open(url, new=0, autoraise=False)

class ManualWaybackPlusMongoDBClassifierSingle(ManualWaybackClassifierSingle):
    """Hand classify a set of web items using an OpenWayback installation,
    a MongoDB database containing alternative textual content, Tkinter and
    the system web browser.

    This is a subclass of ManualWaybackClassifierSingle. It adds an
    additional button to the classification window to retrieve text from
    a MongoDB database if needed. This is useful to allow a fallback in
    case the OpenWayback instance does not have (or cannot handle) the
    page required. It was implemented to handle WARC 'conversion' records
    with plain text versions of PDF/Word documents, which are not currently
    handled by OpenWayback.

    mongodb -- the name of the MongoDB database
    collection -- the name of the MongoDB collection
    client -- a pymongo client (default: pymongo.mongo_client.MongoClient()
        which by default tries to connect to the local machine)
    """
    def __init__(self, mongodb, collection,
        client=pymongo.mongo_client.MongoClient(), *args, **kw):
        self.mongoclient = client
        self.db = pymongo.database.Database(self.mongoclient, mongodb)
        self.collection = pymongo.collection.Collection(self.db, collection)

        super(ManualWaybackPlusMongoDBClassifierSingle, self).__init__(*args, **kw)
        self.fallbackbutton = Tkinter.Button(self.root,
                    text='Load from MongoDB',
                    command=self._set_mongo_content)
        self.fallbackbutton.grid(column=1, row=len(self.buttons)+1,
                                 sticky="SW", padx=10)
    
    def _set_mongo_content(self):
        """ Get fallback content from MongoDB and load it into the web browser.

        Runs on callback from the 'Load from MongoDB' button. Uses the
        configured pymongo client, database and collection to get text with
        a key matching the object we're currently classifying. 
        """
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


