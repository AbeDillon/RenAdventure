
import time
import twitter
import Queue
import Q2logging
import threading
import os

"""
to do:

If TRY in run(self) returns false, delete the file from the media folder.

"""

class feedGetter(threading.Thread):

    def __init__(self, user, api):
        """

        """
        threading.Thread.__init__(self)
        self.user = user
        self.api = api

    def run(self):
        """
        Scrapes twitter for (count) number of tweets.  It likely won't return that many.  They are returned as classes.
        """
        try:  # TRY added to prevent breakage on twitter handles that have disappeared or have been deleted
            statuses = self.api.GetUserTimeline(self.user, count=100, exclude_replies=True)
            self.twitterSave(statuses)
            logger.write_line("Init thread to get tweets for %s " % self.user)
        except:
            logger.write_line("Twitter object failed for %s" % self.user)
            pass
        
        return None

    # twitter.api returns the data as a class.  twitterSave strips out
    # the tweet, converts it to UTF-8 and saves it to a file.
    def twitterSave(self, statuses):
        fout = open("twitterFeeds\\" + self.user + ".twitter", 'w')
        for status in statuses:
            text = status.text
            text = text.encode("utf-8")
            text = text.replace("\n", "")
            fout.write(text)
            fout.write("\n")
        fout.close()

        logger.write_line("twitterFeeds file saved for %s" % self.user)


#==================================================================================================

logger = Q2logging.out_file_instance("logs\\twitterCrawler\\twitterCrawler")


def main():
    workQueue = Queue.Queue()
    twitThread = twitterThread(workQueue)
    twitThread.start()


class twitterThread(threading.Thread):
    def __init__(self, newNamesQ):
        threading.Thread.__init__(self)
        self.newNamesQ = newNamesQ
        self.oldNamesQ = Queue.Queue()
        self.api = twitter.Api()

    def run(self):
        """
        Looks at the two queues, pulls from newNamesQ first if available, and gets the twitter feed for that name.
        If there's nothing in the queues it looks in the "twitterFeeds" folder and adds those names to the newNamesQ queue.
        Each name gets spun off on it's own thread to get the tweets, new threads are spun off at no less than
        45 second intervals.
        """
        startTime = time.time()
        while 1:
            try:
                user = self.newNamesQ.get_nowait()
                logger.write_line("Looking for name in newNamesQ")
            except Queue.Empty:
                user = None
                logger.write_line("No name in newNamesQ")

            if user == None:
                try:
                    user = self.oldNamesQ.get_nowait()
                    logger.write_line("Looking for name in oldNamesQ")
                except Queue.Empty:
                    user = None
                    logger.write_line("No name in oldNamesQ")

            if user != None:
                self.oldNamesQ.put(user)
                logger.write_line("Appended %s to oldNamesQ" % user)

                feedGetterThread = feedGetter(user, self.api)
                feedGetterThread.start()
                logger.write_line("Sent name %s to feedGetter" % user)

                finishTime = time.time()
                loopTime = finishTime - startTime
                waitTime = 45 - loopTime
                waitTime = max(0, waitTime)
                time.sleep(waitTime)
                startTime = time.time()


if __name__ == "__main__":
    main()