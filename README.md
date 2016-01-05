handclassifier
==============
A quick-and-dirty python GUI for facilitating hand-classifying text and
web content into arbitrary categories.

This is still rudimentary and the API should not be considered stable.

The basic framework is to use a tkinter gui window to present the possible
classes for each document, with the document itself presented in another
window:

* ManualTextClassifierSingle presents text in a tkinter window
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
contact: tom.nicholls@oii.ox.ac.uk

This work is available under the terms of the GNU General Purpose Licence
This program is free software: you can redistribute it and/or modify
it under the terms of version 2 of the GNU General Public License as published
by the Free Software Foundation.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

