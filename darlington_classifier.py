#!/usr/bin/python
# Categorise Darlington web content

import Tkinter
import handclassifier
import datetime
import random
import warctika

categories = ("1 - Information transmission",
              "2 - Service delivery",
              "3 - Participation and collaboration",
              "4 - Interactive democracy")

dirname = 'xxx'
outfn = 'dton-hand-classifications.csv'

r = random.Random()
r.seed(1818118181) # Arbitrary

#Load all the objects into memory first
print "Loading content"
content = []

for fn in os.listdir(dirname):
    if not fn.endswith('.warc.gz'):
        continue
    for record in WARCFile(fn, 'rb'):
        if (record.get_underlying_mimetype().startswith('text/') and
                r.random() <= 0.1): # Take 10%
            # Read article into memory
            # TODO: Could make this a FilePart or similar to vastly
            # reduce the memory load if this is a problem.
            try:
                content.append(record.get_underlying_content())
            except Exception:
                # May well be no actual content (e.g. metadata record)
                continue

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
classifier = ManualHTMLClassifierSingle(htmlpages, categories, output)
Tkinter.mainloop()
output.close()

