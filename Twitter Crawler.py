
import os
import pickle
import time
import twitter


# Stole this off the interwebs.  It converts a class to a dictionary.
def class2dict(o):
    """Return a dictionary from object that has public
       variable -> key pairs
    """
    dic = {}
    #Joy: all the attributes in a class are already in __dict__
    for elem in o.__dict__.keys():
        if elem.find("_" + o.__class__.__name__) == 0:
            continue
            #We discard private variables, which are automatically
            #named _ClassName__variablename, when we define it in
            #the class as __variablename
        else:
            dic[elem] = o.__dict__[elem]
    return dic


#===============================================entry==============================================

api = twitter.Api()

handles = []

tempList = []


# Creates the directory "twitterfeeds" if it.'s not already there.  Probably don't need this.
directories = os.listdir(os.getcwd())
if 'twitterfeeds' not in directories:
    os.mkdir('twitterfeeds')


# gets list of handles from the names of the text files and appends the "handles" list
filelist = os.listdir(os.getcwd() + "\\twitterfeeds")
for filename in filelist:
    name = filename.split('.')
    name = name[0]
    handles.append(name)


# Gets the info from twitter based on the "handles" list.  Takes the twitter info (it's returned as a class) and
# converts it to a dictionary. Saves that dictionary to the text file named after the twitter handle.
# Loop runs (twitter info for next handle) every 45 seconds.
while(1):
        for user in handles:
            allInfo = api.GetUserTimeline(user, count=100, exclude_replies=True)
            allInfoDicts = []
            for item in allInfo:
                dic = class2dict(item)
                allInfoDicts.append(dic)
            twitTimeline = open('twitterfeeds\\' + user + ".txt", 'w')
            pickle.dump(allInfoDicts, twitTimeline)
            twitTimeline.close()
            time.sleep(45)
