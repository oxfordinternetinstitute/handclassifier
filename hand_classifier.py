#!/usr/bin/python
#NER Project
#Hand classifier
#This program takes a fixed number of stories, at random
#from a fixed date range within the dataset, also chosen at random
#the interface presents each article next to each other article once
#and asks for human judgment about whether or not the articles are related

#GUI
def OnButtonClick(result):
    global total
    global articles
    global i
    global j
    global text1
    global text2

    print result
    print i
    print j

    #set all the rest of the js to unrelated
    if result == "Unrelated to all":

        while(j < total):

            output.write(articles[i]["Link"])
            output.write(",")
            output.write(articles[j]["Link"])
            output.write(",")
            output.write(result)
            output.write("\n")
            j = j + 1
            print i
            print j

        i = i + 1
        j = i + 1
        text1.delete(1.0, END)
        text1.insert(INSERT, articles[i]["Text"])
        text2.delete(1.0, END)
        text2.insert(INSERT, articles[j]["Text"])
    else:

        if j == total - 1:
            i = i + 1
            j = i + 1

            text1.delete(1.0, END)
            text1.insert(INSERT, articles[i]["Text"])
            
            if i == total - 1:
                print "Finished"
        else:
            j = j + 1

        text2.delete(1.0, END)
        text2.insert(INSERT, articles[j]["Text"])

        output.write(articles[i]["Link"])
        output.write(",")
        output.write(articles[j]["Link"])
        output.write(",")
        output.write(result)
        output.write("\n")
    

def initialize(master, first_text="stuff", second_text="things"):

    global articles
    global i
    global j

    #Text boxes displaying articles to classify
    text_title1 = Label(master,text="", anchor="w",fg="black", justify="left", font=("Helvetica", 16))
    text_title1.grid(column=0,row=0, sticky='EW', padx=10)

    text1 = Text(master, wrap=WORD)
    text1.grid(column=0,row=1,rowspan=20,sticky='EW', padx=10)
    text1.insert(INSERT, articles[i]["Text"])

    scrollbar = Scrollbar(master, command=text1.yview)
    scrollbar.grid(row=1, column=0, rowspan=20, sticky='NSE')
    text1.config(yscrollcommand=scrollbar.set)

    #Text boxes displaying articles to classify
    text_title2 = Label(master,text="", anchor="w",fg="black", justify="left", font=("Helvetica", 16))
    text_title2.grid(column=1,row=0, sticky='EW', padx=10)

    text2 = Text(master, wrap=WORD)
    text2.grid(column=1,row=1,rowspan=20,sticky='EW', padx=10)
    text2.insert(INSERT, articles[j]["Text"])

    scrollbar = Scrollbar(master, command=text2.yview)
    scrollbar.grid(row=1, column=1, rowspan=20, sticky='NSE')
    text2.config(yscrollcommand=scrollbar.set)

    button1 = Button(master, text="Related", command= lambda j="Related": OnButtonClick(j))
    button1.grid(column=1, row=23, sticky="W", padx=10)

    button2 = Button(master, text="Unrelated", command= lambda j="Unrelated": OnButtonClick(j))
    button2.grid(column=1, row=24, sticky="W", padx=10)

    button3 = Button(master, text="Unrelated to all", command= lambda j="Unrelated to all": OnButtonClick(j))
    button3.grid(column=1, row=25, sticky="W", padx=10)


    return text1, text2
        

#Params, imports
import utils
from datetime import datetime
from Tkinter import *

infiles = ("mail-out.txt", "sun-out.txt",
           "bbc-out.txt", "telegraph-out.txt",
           "mirror-out.txt", "express-out.txt",
           "guardian-out.txt")


strFormat="%Y-%m-%dT%H:%M:%SZ"
#start date chosen by hand though without any real reason
start_date = datetime.strptime("2013-04-27T12:00:00Z", strFormat)

master = Tk()

#Load all the articles into memory first
print "Loading articles"
path = "V:/Research/News Politics (Nicholls)/Papers/NER/"
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

    #read article into memory if it is in the window
    if dt > start_date and (dt - start_date).days <= 0 and (dt - start_date).seconds <= 14400:
        info = {}
        info["Date"] = cells[2].strip()
        info["Title"] = cells[1].strip()
        info["Link"] = cells[0].strip()
        info["Text"] = cells[3].strip()
        total = total + 1
        articles.append(info)

    #2013-05-02T03:07:45Z

master_list.close()
print total, "articles selected for pairing"
num_pairs = ((total * total) - total) / 2
print "This will be %s classifications" % num_pairs

index1 = 0
index2 = 1

try:
    output = open(path + "story_pairs.csv", "r")
    #first check how many pairs have already been done
    completed = 0
    for line in output:
        completed = completed + 1

    output.close()
    print completed, "articles already completed"

    #we want to start on the next article
    completed = completed + 1

    #turn this into the correct index
    index1 = int(completed / total)
    index2 = completed % total
except:
    print "Nothing classified yet"

#Now we are ready to classify
output = open(path + "story_pairs.csv", "a")
i = index1
j = index2

#Initialise and run the GUI
text1, text2 = initialize(master)
mainloop()
output.close()

        
