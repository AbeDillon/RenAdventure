
import urllib2
import os
import re



"""

This works by being given a character name and the link to the IMDB "quotes" page for the character,
NOT the actor playing said character.

"""


# Creates the directory "saves" if it.'s not already there.
directories = os.listdir(os.getcwd())
if "saves" not in directories:
    os.mkdir("saves")


#================================================xxxxxxxxxxxxxxxxxxxx===============================================

"""
Need to:
    arguments to das_Quotemaker will change from url, charactername to imdb character ID number, imdb(extension)

    clean up quotes
    save quotes to file that was given to me


"""


siteRef = {'imdb.com': ("%s</a></i>:", "<br/>")}


def getPrefixSuffix(url):

    siteRef = {'imdb.com': ("%s</a></i>:", "<br/>")}

    for site in siteRef:
        if site in url:
            return siteRef[site]
    print "This site is not in our database."


# takes in url and character name
def das_Quotemaker(url, characterName):

    quotes = []

    prefix, suffix = getPrefixSuffix(url)
    prefix = prefix % characterName
    print prefix
    site = urllib2.urlopen(url)
    siteHtml = site.read()
    chunks = siteHtml.split(prefix)
    chunks = chunks[1:]

    for chunk in chunks:
        line = chunk.split(suffix)
        line = line[0]
        quotes.append(line)
    print quotes


if __name__ == "__main__":
    das_Quotemaker("http://www.imdb.com/character/ch0008323/quotes", "Max Fischer")
    das_Quotemaker("http://www.imdb.com/character/ch0000177/quotes", "Batman")
    das_Quotemaker("http://www.imdb.com/character/ch0000216/quotes", "Dick Grayson")