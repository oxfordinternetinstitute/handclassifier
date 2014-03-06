#!/usr/bin/python
# Categorise Darlington web content

import Tkinter
import handclassifier
import datetime
import random
import warctika
import os

categories = ("1 - Information transmission",
              "2 - Service delivery",
              "3 - Participation and collaboration",
              "4 - Interactive democracy",
              "X - Exclude")

dirname = 'dton-warcs'
outfn = 'dton-hand-classifications.csv'

# Due to an error in list.darlington.gov.uk/robots.txt, we have a lot of pages
# in our set which should not have been collected. Let's drop them.
discardurls = ('http://lis.darlington.gov.uk/profiles/',
               'http://lis.darlington.gov.uk/dataviews/',
               'http://lis.darlington.gov.uk/advancedprofiles/',
               'http://lis.darlington.gov.uk/advanceddataviews/',
               'http://lis.darlington.gov.uk/explorer/',
               'http://lis.darlington.gov.uk/map/',
               'http://lis.darlington.gov.uk/cache/',
               'http://lis.darlington.gov.uk/ajax/')

proptoclassify = 0.1

r = random.Random()
r.seed(1818118181) # Arbitrary

content = []

#Load all the objects into memory first
print "Loading content"
for fn in os.listdir(dirname):
    if not fn.endswith('.warc.gz'):
        continue
    wf = warctika.WARCFile(dirname+'/'+fn, 'rb')
    try:
        for record in wf:
            if not record.type in ['response','resource','conversion']:
                continue
            # This could be 'None' if there is no Content-Type field in the header.
            if not str(record.get_underlying_mimetype()).startswith(
                    ('text','application/xhtml','None')):
                print "Rejecting", record.get_underlying_mimetype(), "\n\tfor", record.url
                continue
            if str(record.get_underlying_mimetype()).startswith(
                    ('text/csv','text/css')):
                print "Rejecting", record.get_underlying_mimetype(), "\n\tfor", record.url
                continue
            if record.url.startswith(discardurls):
    #            print "Rejecting", record.url
                continue
            rval = r.random()
            if rval > proptoclassify:
    #            print "Not selecting ("+str(rval)+")", record.url
                continue
            print "Adding:", record.url
            # Read article into memory
            # TODO: Could make this a FilePart or similar to vastly
            # reduce the memory load if this is a problem.
            # TODO: Could change interface to pass the mimetype - maybe
            # make it easier to send to an appropriate program, or to name
            # the file correctly when it's sent to a web browser?
            content.append((record.url,record.get_underlying_content()))
    except IOError as e:
        print e
    wf.close()

print "There are", len(content), "objects to classify."

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

#Now we are ready to classify
output = open(outfn, 'a')

#Initialise and run the GUI
classifier = handclassifier.ManualBrowserClassifierSingle(content,
                                                          categories,
                                                          output)
Tkinter.mainloop()
output.close()

