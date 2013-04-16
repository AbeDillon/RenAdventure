
import urllib2
import Queue
import Q2logging
import threading
import time
import os


"""

This works by being given a unique character ID number from a "quotes" page and the
file extension which is the site the quotes came from, i.e. imdb.

This supports IMDB only at this time.

"""

translation = {"&#x27;": "'",
               "&#x22;": "\"",
               "[<i>": "[",
               "</i>]": "]",
               "&amp;": "&"}

#================================================xxxxxxxxxxxxxxxxxxxx===============================================

"""
Need to:

    add logging
    add extension dictionary to getFullinfo()

"""

# Creates the directory "twitterCrawler" if it.'s not already there.
# directories = os.listdir(os.getcwd())
# if "logs\\quoteCrawler\\quoteCrawler" not in directories:
#     os.mkdir((os.getcwd() + "\\logs\\quoteCrawler\\quoteCrawler"))

logger = Q2logging.out_file_instance("logs\\quoteCrawler\\quoteCrawler")


def main():
    workQueue = Queue.Queue()
    qThread = quoteThread(workQueue)
    qThread.start()


class quoteThread(threading.Thread):
    def __init__(self, newNamesQ):
        threading.Thread.__init__(self)
        self.newNamesQ = newNamesQ
        self.oldNamesQ = Queue.Queue()

    # takes in imdb id number and character name from the queue
    def run(self):

        while 1:

            time.sleep(1)

            try:
                quoteInfo = self.newNamesQ.get_nowait()
                logger.write_line('Received quoteInfo from the newNames queue to process.')
                # log stuff
            except Queue.Empty:
                quoteInfo = None
                # log stuff

            if quoteInfo == None:
                try:
                    quoteInfo = self.oldNamesQ.get_nowait()
                    logger.write_line('Received quoteInfo from the oldNames queue to process.')
                    # log stuff
                except Queue.Empty:
                    quoteInfo = None

            if quoteInfo != None:

                uniqueID, characterName = quoteInfo
                logger.write_line('Processing quoteInfo .')

                self.oldNamesQ.put(quoteInfo)

                quotes = []

                # these are used to isolate the quotes we are after
                prefix = characterName + "</a></i>:"
                suffix = "<br/>"

                # format for inserting the imdb character number into the url
                url = "http://www.imdb.com/character/%s/quotes" % uniqueID

                # opens the site and breaks out quotes by prefix
                site = urllib2.urlopen(url)
                logger.write_line('Opened %s' % url)
                siteHtml = site.read()
                logger.write_line('Read %s' % url)
                chunks = siteHtml.split(prefix)
                chunks = chunks[1:]

                # takes the quotes and removes the suffix
                for chunk in chunks:
                    line = chunk.split(suffix)
                    line = line[0]
                    quotes.append(line)

                # cleans up quotes and writes them to a .imdb file
                qout = open('twitterFeeds\\' + uniqueID + ".imdb", "w")
                logger.write_line('Opened the IMDB file to write quotes')

                for quote in quotes:

                    quote = quote.encode('utf-8')

                    for word in translation.keys():
                        quote = quote.replace(word, translation[word])

                    qout.write(quote)
                    qout.write('\n')
                    logger.write_line('Quotes have been processed.')
                qout.close()
                logger.write_line('Closed the IMDB file. Moving to the next file in the queue.')

if __name__ == "__main__":
    main()