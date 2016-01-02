#!/usr/bin/python2
# Categorise govUK web content

from __future__ import print_function
import Tkinter
import handclassifier
import pymongo
import datetime
import random
import os
import csv
from collections import defaultdict

categories = ("SI - Service Informational",
              "ST - Service Transactional",
              "DI - Democracy Informational",
              "DT - Democracy Transactional",
              "D - Data not for browsing",
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

# Shuffle content so it's not in alphabetical order for classifying
r.shuffle(content)

print("There are", len(content), "objects to classify.")
print("Rejects:", rejects)

completed = 0
try:
    with open(outfn, 'r') as output:
        #first check how many classifications have already been done
        for line in output:
            completed = completed + 1
    print(completed, "classifications already completed")
    content = content[completed:]
    output = open(outfn, 'ba')
except IOError:
    print("Nothing classified yet")
    output = open(outfn, 'ba')
    output.write("URL;Classification\r\n")

if len(content) == 0:
    exit("Nothing to classify. Exiting.")

# TODO: Check for records which are recorded as "? - Unable to determine",
# remove them from the output file and add them to the end of the content
# list to try again


#Initialise and run the GUI
classifier = handclassifier.ManualWaybackPlusMongoDBClassifierSingle(
                'warctext', 'url_to_text',
                client=pymongo.mongo_client.MongoClient(host='192.168.1.103'),
                items=content, labels=categories, output=output,
                wburl=wburl, nprevclass=completed)
Tkinter.mainloop()
output.close()

