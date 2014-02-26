#!/usr/bin/python
# Categorise news content

import Tkinter
import hand-classifier
import datetime

categories = ("CrappyCat1",
              "MediocreCat2",
              "CompetentCat3",
              "MagnificentCat4")


strFormat="%Y-%m-%dT%H:%M:%SZ"
#start date chosen by hand though without any real reason
start_date = datetime.strptime("2013-04-27T12:00:00Z", strFormat)

#master = Tk()

#Load all the articles into memory first
print "Loading articles"
path = ''
articles = []
master_list = open(path + "articles_list_large.csv", "r")
total = 0

for line in master_list:
    cells = line.split(",")
 
    
    try:
        dt = datetime.strptime(cells[2].strip(), strFormat)
    #some noise in this field
    except:
        continue

    #read article into memory if it is in the window (4 hours)
    if dt > start_date and (dt - start_date).days <= 0 and (dt - start_date).seconds <= 14400:
        articles.append( (cells[1].strip(), cells[3].strip()) )

print "There are", len(articles), "objects to classify."

try:
    output = open(path + "story_pairs.csv", "r")
    #first check how many pairs have already been done
    completed = 0
    for line in output:
        completed = completed + 1

    output.close()
    print completed, "articles already completed"

    articles = articles[completed:]

except:
    print "Nothing classified yet"

#Now we are ready to classify
output = open(path + "story_pairs.csv", "a")

#Initialise and run the GUI
classifier = ManualHTMLClassifierSingle(articles, categories, output)
Tkinter.mainloop()
output.close()

        
