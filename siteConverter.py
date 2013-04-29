
import urllib2
import Q2logging
import os


"""
This will receive requests from multiple areas and return
a unique ID and character name from the (extension) quote site.

This supports IMDB only at this time.  More to come...

"""

"""
to to:

add extension dictionary

"""


#==============================================================================================

logger = Q2logging.out_file_instance("logs\\siteConverter\\siteConverter")


# siteRef = {imdbUrl: "http://www.imdb.com/character/%s/quotes",
#            imdbPrefix: "<title>",
#            imdbSuffix: " (Character)  - Quotes</title>",
#            # first %s is the first letter of the last name of the character
#            brainyquoteUrl: "http://www.brainyquote.com/quotes/authors/%s/%s.html",
#            # first %s is the first letter of the first name,
#            # the second is the name (no spaces) followed by a 6 digit number.
#            brainyquotePrefix: "quotes/%s/%s.html",
#            brainyquoteSuffix: "</a></span><br>",
#            # xx is a 2 digit number different for each character
#            saidwhatUrl: "http://www.saidwhat.co.uk/characterquotes/%s_xx",
#            # this will miss the first quote
#            saidwhatPrefix: "</span><br /><br />",
#            saidwhatSuffix: "<br/>"}

# get the unique ID from the (extension) quote site
def getFullinfo(uniqueID, ext):

    # format for inserting the imdb character number into the url
    url = "http://www.imdb.com/character/%s/quotes" % uniqueID

    # first we get the character name from the url aboveDatabase.py
    prefix = "<title>"
    suffix = " (Character)  - Quotes</title>"

    # opens the site and breaks out the character name by prefix
    site = urllib2.urlopen(url)
    logger.write_line("Opened %s" % url)
    siteHtml = site.read()
    logger.write_line("Read %s" % url)
    chunks = siteHtml.split(prefix)
    chunks = chunks[1:]

    for chunk in chunks:
        line = chunk.split(suffix)
        characterName = line[0]

    # returns the unique ID and the character name
    logger.write_line("Returning %s" % uniqueID)
    return uniqueID, characterName