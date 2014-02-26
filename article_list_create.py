#!/usr/bin/python
infiles = ("mail-out.txt", "sun-out.txt",
           "bbc-out.txt", "telegraph-out.txt",
           "mirror-out.txt", "express-out.txt",
           "guardian-out.txt")

#from a file handle get an article and associated meta info
def get_article(handle):

    #Cycle through any garbage until the next header or EOF
    while True:
        line = handle.readline()
        
        if not line:
            return "EOF", "EOF"

        if line[0:4] == "####":
            break

    #Now read the header
    #Format: http://www.express.co.uk/news/showbiz/392805/Victoria-Beckham-celebrates-turning-39-with-a-trip-to-Nobu-with-her-children;http://www.express.co.uk/;Victoria Beckham celebrates turning 39 with a trip to Nobu with her children | Showbiz | News | Daily Express;2013-04-18T16:49:37Z;2013-04-18T16:49:37Z
    line = handle.readline()
    cells = line.split(";")

    header = {}
    header["Link"] = cells[0]
    header["Site"] = cells[1]
    header["Title"] = cells[2]
    header["Date"] = cells[3]

    #Next line should be four hashes
    line = handle.readline()
    if not "####" in line:
        print "Four hash check failed with", line

    #Next line is the article
    article = handle.readline()

    return article, header

master_list = open("articles_list_large.csv", "w")
print "Creating master list"
for infile in infiles:

    handle = open(infile, "r")

    while(True):

        article, header = get_article(handle)

        if article == "EOF":
            break

        master_list.write(header["Link"])
        master_list.write(",")
        master_list.write(header["Title"].replace(",", ""))
        master_list.write(",")
        master_list.write(header["Date"])
        master_list.write(",")
        master_list.write(article.replace(",", ""))
        master_list.write("\n")

    handle.close()
master_list.close()
##print "Created"
