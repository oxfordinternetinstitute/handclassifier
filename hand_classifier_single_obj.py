#!/usr/bin/python
#NER Project
#Hand classifier
#This program takes a fixed number of stories, at random
#from a fixed date range within the dataset, also chosen at random
#the interface presents each article next to each other article once
#and asks for human judgment about whether or not the articles are related
#
#Copyright 2013-2014, Jonathan Bright and Tom Nicholls


#Params, imports
#import utils
from datetime import datetime
import Tkinter
import TkHtml
import sys

#GUI

class ManualTextClassifier:
    def __init__(self, items, labels=[0,1], output=sys.stdout,
                 winx=1280, winy=880):
        # items is a list of 2-tuples containing an identifier (such as a URL)
        # for the output, and the HTML content itself
        # output is a file handle to output to
        # labels is a list of classification options to select from
        self.output = output
        self.items = items
        self.idx = -1
        self.numclassified = {}
        self.labels = labels
        if len(labels) < 2:
            raise Exception("ManualHTMLClassifier needs at least 2 labels")
        for label in labels:
            self.numclassified[label] = 0
        self.root = Tkinter.Tk()
        self.set_root_window_size(winx, winy)
        self.buttons = []

        # Article title / URL
        self.text_title = Tkinter.Label(self.root, text="", anchor="w",
                                    fg="black", justify="left",
                                    font=("Helvetica", 16),
                                    width=90)
        self.text_title.grid(column=0,row=0, sticky='EW', padx=10)

        self.content = self.make_content()
        self.content.grid(column=0, row=1, rowspan=20, sticky='NSEW', padx=10)

        self.update_content()

        self.scrollbar = Tkinter.Scrollbar(self.root,
                                           command=self.content.yview)
        self.scrollbar.grid(column=0, row=1, rowspan=20, sticky='NSE')
        self.content.config(yscrollcommand=self.scrollbar.set)

        for i, label in enumerate(labels):
            self.buttons.append(
                Tkinter.Button(
                    self.root,
                    text=label,
                    command= lambda j=label: self.on_button_click(j)))
            self.buttons[-1].grid(column=1, row=1+i, sticky="SW", padx=10)

    def make_content(self):
        self.content = Tkinter.Text(self.root, wrap=Tkinter.WORD)

    def set_root_window_size(self, winx, winy):
        # FIXME: This is all a horrible hack.
#        self.root.geometry(''+str(winx)+'x'+str(winy))
        self.root.rowconfigure(1, minsize=30)
        allocated = 30
        for i in range(2, 1+len(self.labels)):
            self.root.rowconfigure(i, minsize=20)
            allocated += 20
        size = (winy - allocated) / (20 - len(self.labels))
        print "row size =", size
        for i in range(1+len(self.labels),21):
            self.root.rowconfigure(i, minsize=size)

    def clear_content(self):
        self.content.delete(1.0, Tkinter.END)

    def set_content(self):
        self.clear_content
        self.content.insert(Tkinter.INSERT, self.items[self.idx][1])

    def update_content(self):
        self.idx += 1
        try:
            print self.idx, self.items[self.idx][0]
            self.text_title.config(text=self.items[self.idx][0])
            self.set_content()
        except IndexError:
            print "Finished!"
            self.root.destroy()

    def write_result(self, identifier, result):
        self.output.write(identifier)
        self.output.write(",")
        self.output.write(result)
        self.output.write("\n")
       
    def on_button_click(self, result):
        print result
        self.write_result(self.items[self.idx][0], result)
        self.update_content()


class ManualHTMLClassifier(ManualTextClassifier):
    def make_content(self):
        return TkHtml.Html(self.root)

    def clear_content(self):
        self.content.clear()

    def set_content(self):
        new_content = self.items[self.idx][1]
        self.clear_content()
        # FIXME: Fairly grotty hack to handle non-HTML content
        if '<html>' not in new_content.lower():
            self.content.parse('<html><body>'+new_content+'</html></body>')
        else:
            self.content.parse(new_content)

#####
#MAIN
#####    
if __name__ == "__main__":
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
    classifier = ManualHTMLClassifier(articles, categories, output)
    Tkinter.mainloop()
    output.close()

            
