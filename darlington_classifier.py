#!/usr/bin/python
# Categorise Darlington web content

import Tkinter
import handclassifier
import datetime
import random
import os
from collections import defaultdict
# This can be installed with 'pip install warctools'. Beware that there are
# several old versions floating around under different names in the index.
from hanzo.warctools import WarcRecord
from warcresponseparse import *

categories = ("1 - Information transmission",
              "2 - Service delivery",
              "3 - Participation and collaboration",
              "4 - Interactive democracy",
              "X - Exclude",
              "? - Unable to determine")

dirname = 'dton-test-3'
outfn = 'dton-hand-classifications.csv'

# Due to an error in lis.darlington.gov.uk/robots.txt, we have a lot of pages
# in our set which should not have been collected. Let's drop them.
discardurls = ('http://lis.darlington.gov.uk/profiles/',
               'http://lis.darlington.gov.uk/dataviews/',
               'http://lis.darlington.gov.uk/advancedprofiles/',
               'http://lis.darlington.gov.uk/advanceddataviews/',
               'http://lis.darlington.gov.uk/explorer/',
               'http://lis.darlington.gov.uk/map/',
               'http://lis.darlington.gov.uk/cache/',
               'http://lis.darlington.gov.uk/ajax/')

# HTTP status codes which represent a record successfully returned - these
# are all we are interested in sampling
successcodes = (200, 201, 202, 203, 206)

# Total number of items is ~612k
proptoclassify = 0.002

r = random.Random()
r.seed(1818118181) # Arbitrary

content = []
rejects = defaultdict(int)

#Load all the objects into memory first
print "Loading content"
for fn in os.listdir(dirname):
    if not fn.endswith('.warc.gz'):
        continue
    wf = WarcRecord.open_archive(dirname+'/'+fn, mode='rb')
    try:
        for record in wf:
            if not record.type in [WarcRecord.RESPONSE,
                                   WarcRecord.RESOURCE,
                                   WarcRecord.CONVERSION]:
                continue
            if record.type == WarcRecord.RESPONSE:
                ccode, cmime, cbody = parse_http_response(record)
                if ccode not in successcodes:
                    continue
            else:
                ccode = None
                cmime = record.content[0]
                cbody = record.content[1]
            # This could be 'None' if there is no Content-Type field in the header.
            if not cmime.startswith(('text','application/xhtml','None')):
    #            print "Rejecting", cmime, "\n\tfor", record.type, record.url
                rejects[cmime] += 1
                continue
            if cmime.startswith(('text/csv','text/css')):
    #            print "Rejecting", cmime, "\n\tfor", record.type, record.url
                rejects[cmime] += 1
                continue
            if record.url.startswith(discardurls):
    #            print "Rejecting", record.url
                rejects['discardurls'] += 1
                continue
            rval = r.random()
            if rval > proptoclassify:
    #            print "Not selecting ("+str(rval)+")", record.url
                rejects['not sampled'] += 1
                continue
    #        print "Adding:", ccode, cmime, record.url
            # Read article into memory
            # TODO: Could make this a FilePart or similar to vastly
            # reduce the memory load if this is a problem.
            # TODO: Could change interface to pass the mimetype - maybe
            # make it easier to send to an appropriate program, or to name
            # the file correctly when it's sent to a web browser?
            content.append((record.url,cbody))
    except IOError as e:
        print e
    wf.close()

print "There are", len(content), "objects to classify."
print "Rejects:", rejects

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

# TODO: Check for records which are recorded as "? - Unable to determine",
# remove them from the output file and add them to the end of the content
# list to try again

#Now we are ready to classify
output = open(outfn, 'a')

#Initialise and run the GUI
classifier = handclassifier.ManualWaybackClassifierSingle(content,
                                                          categories,
                                                          output)
Tkinter.mainloop()
output.close()

