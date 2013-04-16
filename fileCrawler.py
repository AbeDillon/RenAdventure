
import os
import Q2logging
import quoteCrawler
import twitterCrawler
import siteConverter
import time
import Queue


"""

this code looks at the media folder, finds new files and figures out what type of files they are,
and sends them to either TwitterCrawler or to the siteConverter/quoteCrawler

"""

#===================================================================================================

"""
to do:

logging
pass the extension to getFullinfo

"""

logger = Q2logging.out_file_instance("logs\\fileCrawler\\fileCrawler")


oldNames = set()

# this assumes that the file names for the quotes stuff is like this ch0008323.imdb.
# ch0008323 is the imdb "character ID" that we can insert into a url to get the quotes page.

# Sets up queue for twitter and inits twitterCrawler
twitQueue = Queue.Queue()
twitThread = twitterCrawler.twitterThread(twitQueue)
twitThread.start()

# Sets up queue for quotes and inits quoteCrawler
quoteQueue = Queue.Queue()
qThread = quoteCrawler.quoteThread(quoteQueue)
qThread.start()


while 1:

    filelist = os.listdir(os.getcwd() + "\\twitterfeeds")
    fileset = set(filelist)

    newNames = fileset - oldNames
    oldNames |= newNames

    for name in newNames:

            time.sleep(1)

            item = name.split('.')
            uniqueID = item[:-1]
            uniqueID = '.'.join(uniqueID)
            ext = item[-1]

            if ext == "twitter":

                twitQueue.put(uniqueID)
                logger.write_line('Sent %s to twitQueue' % uniqueID)

            if ext == "imdb":

                quoteQueue.put(siteConverter.getFullinfo(uniqueID, ext))
                logger.write_line('Sent %s to quoteQueue' % uniqueID)