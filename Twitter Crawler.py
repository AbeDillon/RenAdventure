
"""
add logging
    logger.write_line('Initializing game state from save state %d' % save_state) ###TEST
update comments
"""

import os
import time
import twitter
import Queue
import Q2logging
import threading

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
        statuses = self.api.GetUserTimeline(self.user, count=100, exclude_replies=True)
        self.twitterSave(statuses)

        return None

    # twitter.api returns the data as a class.  twittersave strips out
    # the tweet, converts it to UTF-8 and saves it to a file.
    def twitterSave(self, statuses):
        fout = open('twitterfeeds\\' + self.user + ".txt", 'w')
        for status in statuses:
            text = status.text
            text = text.encode('utf-8')
            text = text.replace('\n', '')
            fout.write(text)
            fout.write('\n')
        fout.close()


#===============================================entry==============================================


# logger = Q2logging.out_file_instance('logs/TwitterCrawler/TwitterCrawler')


def getNames(path):
    # gets list of handles from the names of the text files and appends the "handles" list
    fileList = path
    handles = []

    for filename in fileList:
        name = filename.split('.')
        name = name[0]
        handles.append(name)
    return handles


def main():
    api = twitter.Api()

    Names = []

    newNamesQ = Queue.Queue()

    oldNamesQ = Queue.Queue()

    # Looks at the two queues, pulls from newNamesQ first if available, and gets the twitter feed for that name.
    # If there's nothing in the queues it looks in the "twitterfeeds" folder and adds those names to the newNamesQ queue.
    # Each name gets spun off on it's own thread to get the tweets, new threads are spun off at no less than
    # 45 second intervals.
    startTime = time.time()
    while(1):
        try:
            user = newNamesQ.get_nowait()
        except Queue.Empty:
            user = None

        if user == None:
            try:
                user = oldNamesQ.get_nowait()
            except Queue.Empty:
                user = None

        if user != None:
            oldNamesQ.put(user)

            feedGetterThread = feedGetter(user, api)
            feedGetterThread.start()

            finishTime = time.time()
            loopTime = finishTime - startTime
            waitTime = 45 - loopTime
            waitTime = max(0, waitTime)
            time.sleep(waitTime)
            startTime = time.time()


        # Opens "twitterfeeds" folder, parses names and adds them to the newNamesQ queue.
        tempList = getNames(os.listdir(os.getcwd() + "\\twitterfeeds"))
        for name in tempList:
            if name not in Names:
                Names.append(name)
                newNamesQ.put(name)


if __name__ == "__main__":
    main()