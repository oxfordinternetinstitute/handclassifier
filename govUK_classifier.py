#!/usr/bin/python3
# Categorise govUK web content

import Tkinter
import handclassifier
import datetime
import random
import os
import csv
from collections import defaultdict
# This can be installed with 'pip install warctools'. Beware that there are
# several old versions floating around under different names in the index.
from hanzo.warctools import WarcRecord
from warcresponseparse import *

categories = ("1 - Information transmission",
              "2 - Electronic service delivery",
              "3 - Participation and collaboration",
              "D - Data, not for browsing",
              "X - Exclude",
              "? - Unable to determine")

nodemapfn = 'nodemap-sorted-filtered.tsv'
outfn = 'govUK-hand-classifications.csv'
# Base URL of the Wayback Machine (or OpenWayback) instance being used to
# supply the raw pages
wburl = 'http://192.168.1.103:8080/'

# Total number of items is ~15.2m, so this generates
# ~6000 hand classifications
proptoclassify = 0.0004

r = random.Random()
r.seed(1818118181) # Arbitrary

rejects = defaultdict(int)
content = []

#Load all the objects into memory first
with open(nodemapfn, 'rb') as f:
    reader = csv.reader(f, dialect='excel-tab')
    for row in reader:
        if r.random() > proptoclassify:
#            print "Not selecting ("+str(rval)+")", record.url
            rejects['not sampled'] += 1
            continue
#        print "Adding:", ccode, cmime, record.url
        # Read article URL into memory. Don't need the article body with
        # the Wayback classfier as it's fetched through the Wayback index.
        # Not sending it through here as the second part of the tuple
        # saves a good deal of memory.
        # TODO: Could make this a FilePart or similar to vastly
        # reduce the memory load if this is a problem.
        # TODO: Could change interface to pass the mimetype - maybe
        # make it easier to send to an appropriate program, or to name
        # the file correctly when it's sent to a web browser?
        content.append((row[0],None))

print("There are", len(content), "objects to classify.")
print("Rejects:", rejects)

try:
    output = open(outfn, 'r')
    #first check how many classifications have already been done
    completed = 0
    for line in output:
        completed = completed + 1
    output.close()
    print completed, "classifications already completed"
    content = content[completed:]
except:
    print "Nothing classified yet"

if len(content) == 0:
    exit("Nothing to classify. Exiting.")

# TODO: Check for records which are recorded as "? - Unable to determine",
# remove them from the output file and add them to the end of the content
# list to try again

#Now we are ready to classify
output = open(outfn, 'a')

#Initialise and run the GUI
classifier = handclassifier.ManualWaybackClassifierSingle(items=content,
                                                          labels=categories,
                                                          output=output,
                                                          wburl=wburl)
Tkinter.mainloop()
output.close()

