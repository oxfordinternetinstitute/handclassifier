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
              "X - Uncertain")

dirname = '../warctika/scratch/test'
outfn = 'dton-hand-classifications.csv'

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
    for record in wf:
        # This could be 'None' if there is no Content-Type field in the header.
        # Fortunately, str(None) doesn't match 'text/'.
        try:

            if 'text/html' not in record.get_underlying_mimetype():
                print "Rejecting", record.get_underlying_mimetype()
                continue
            if r.random() > proptoclassify:
                continue
            # Read article into memory
            # TODO: Could make this a FilePart or similar to vastly
            # reduce the memory load if this is a problem.
            content.append((record.url,record.get_underlying_content()))
        except Exception:
            # May well be no actual content (e.g. metadata record), excepting
            # either from get_underlying_mimetype() or _content().
            continue
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
classifier = handclassifier.ManualHTMLClassifierSingle(content,
                                                       categories,
                                                       output)
Tkinter.mainloop()
output.close()

