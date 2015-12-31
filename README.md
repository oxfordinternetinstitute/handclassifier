handclassifier
==============

A quick-and-dirty python GUI for facilitating hand-classifying text and
HTML content into arbitrary categories.

This is still rudimentary and the API should not be considered stable.

The basic framework is to use a Tkinter gui window to present the possible
classes for each document, with the document itself presented in another
window:

* ManualTextClassifierSingle presents text in a Tkinter window
* ManualHTMLClassifierSingle renders HTML in a Tkinter window
* ManualBrowserClassifierSingle uses the system web browser to render HTML
* ManualWaybackClassifierSingle looks up the wanted document by URL in an
  OpenWayback installation (http://www.netpreserve.org/openwayback) using the
  system web browser
* ManualWaybackPlusMongoDBClassifierSingle is equivalent to the Wayback
  classifier, but adds a fallback "Load from MongoDB" button to pull the text
  from a MongoDB instance

The repository also contains a number of scripts which use the handclassifier
GUI to deliver particular specific jobs, which might be interesting as examples.

Copyright 2013-2015, Tom Nicholls and Jonathan Bright

contact: tom.nicholls@oii.ox.ac.uk
