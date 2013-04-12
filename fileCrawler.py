
import os
import Q2logging
import quoteCrawler
import TwitterCrawler


"""

this code looks at the media folder, finds new files and figures out what type of files they are,
and sends them to either the quoteCrawler or TwitterCrawler

"""

logger = Q2logging.out_file_instance('logs\\fileCrawler\\fileCrawler')


#===================================================================================================

oldnames = {}

newnames = {}

Names =

# this assumes that the file names for the quotes stuff is like this ch0008323.imdb.
# ch0008323 is the imdb "character ID" that we can insert into a url to get the quotes page.

filelist = os.listdir(os.getcwd() + "\\mediafiles")
filelist = set(filelist)

tempSet = set(os.listdir(os.getcwd() + "\\mediafiles"))
new_set = tempSet - Names
Names |= new_set
# for name in new_names
for filename in filelist:
    if filename in oldnames:
        pass



    if ext == "twitter":
        file = filename.split('.')
        name = file[0]
        ext = file[1]
        if name not in oldnames:
            # this goes away
            TwitterCrawler.Names.append(name)
            TwitterCrawler.newNamesQ.put(name)

    if ext == "imdb":
        url = "http://www.imdb.com/character/%s/quotes" % name




## Abe's example:
# tempSet = set(getnames())
# new_set = temp_set - Names
# Names |= new_set
# for name in new_names

# # unused crap
#     file = filename.split('.')
#     name = file[0]
#     ext = file[1]