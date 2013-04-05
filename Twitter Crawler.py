
import os
import pickle
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

        """
        print 'getting ' + self.user + '\'s status!'
        statuses = self.api.GetUserTimeline(self.user, count=100, exclude_replies=True)
        twitTimeline = open('twitterfeeds\\' + self.user + ".txt", 'w')
        pickle.dump(statuses, twitTimeline)
        twitTimeline.close()
        return None

#===============================================entry==============================================


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
    # Need to update below note!

    # Gets the info from twitter based on the "handles" list.  Takes the twitter info (it's returned as a class) and
    # converts it to a dictionary. Saves that dictionary to the text file named after the twitter handle.
    # Loop runs (twitter info for next handle) every 45 seconds.
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


        tempList = getNames(os.listdir(os.getcwd() + "\\twitterfeeds"))
        for name in tempList:
            if name not in Names:
                Names.append(name)
                newNamesQ.put(name)


if __name__ == "__main__":
    main()