__author__ = 'AYeager'

import Q2logging
import requests, twitter # for validating web URL and Twitter handles

#### ++++++++++++++++++++FILE WIDE NOTES+++++++++++++++++++++++++++++++++++++++
##  self contains the attributes of builder class object being "constructed" in Builder.py
##  These functions are for retuning values to set the related attributes of the object being created in Builder.py


def name(self):
    """function for adding name attribute to object has no validation that name is Unique as previous builder required
    self contains all attributes of the Builder Object in builder.py"""

    text = 'What would you like to name this %s' % self.type

    send_message_to_player(text)
    name = get_cmd_from_player()

    return name

def description(self):
    """
    function for adding a general description
    obj_type = type of object being worked on (portal, item, etc...)
    """
    #log.write_line('entered description function')
    text = 'Enter a description for the %s' % self.type
                                
    send_message_to_player(text)
    desc = get_cmd_from_player()
    
    #self.logger.write_line('exiting description func returned = %s' % desc)

    return desc

def inspect_description(self):
    """    Function for adding Inspection Description    """

    #self.logger.write_line('entered addInspectionDescription function')
    text = 'Enter an inspection description for the %s' % self.type

    send_message_to_player(text)
    i_desc = get_cmd_from_player()
    
    #self.logger.write_line('exit inspection description')
    return i_desc

def getBool(self):
    """
    function for defining a bool attribute of a object
    Returns true or false
    """
    text = 'This %s can be %s.  Do you want to make it so?' % (self.type, self.attr)
    send_message_to_player(text)
    ans = get_cmd_from_player()

    if ans in ['yes', 'y', 'Yes', 'YES']:
        return True
    elif ans in ['no', 'n', 'No', 'NO']:
        return False
    else:
        send_message_to_player("Your answer needs to be yes or no.  Try again.")
        getBool(self)

def textID(self):

     #self.logger.write_line('enter getTextID function')

    text = 'Do you want to have a twitter feed or IMDB Qoutes associated with this %s?  yes or no' % self.type
    send_message_to_player(text)
    ans = get_cmd_from_player()

    if ans in ['no', 'n', 'NO', 'N']:
        return "not_provided"
    if ans in ['yes', 'y', 'Y', "YES"]:
        while True:
            send_message_to_player('Enter the twitter handle or IMDB characterID.')
            ans = get_cmd_from_player()

            if ans[0] == '@': #Looks like, smells like twitter but does it taste like twitter?
                if validateTwitter(ans) == True:
                    # must be twitter
                    textFile = ans+'.twitter'
                    break
                else:
                    send_message_to_player('That does not appear to be a valid twitter handle.')

                # looks and smells like IMDB
            elif len(ans) == 9 and ans[0:2] == 'ch':
                if validateIMDB(ans) == True:
                    #must be IMDB qoutes page
                    textFile = ans+'.imdb'
                    break
                else:
                    send_message_to_player('We could not find a IMDB qoutes page for that character ID')
            else:
                send_message_to_player('That is not a valid twitter handle or IMDB characterID')
    else:
        send_message_to_player('You must answer yes or no.')
        textID(self)

    return textFile

        #self.logger.write_line('exiting getTextID function')pass

def validateIMDB(self, ID):

    #self.logger.write_line('enter validateIMDB function')
    r = requests.get('http://www.imdb.com/character/%s/quotes' % ID)
    if r.status_code == 200: # yes exists
        #self.logger.write_line('found site return true exit function')
        return True
    else:
        #self.logger.write_line('site not found return false exit function')
        return False

def validateTwitter(self, handle):
    """ Function to validate Twitter handle passed in """

    #self.logger.write_line('entered getTwitter function')

    try:  # twitter api throws error if name does not exist
        api = twitter.Api()
        api.GetUser(handle)
        #self.logger.write_line('%s validated as twitter handle' % handle)
        return True
    except:
        #self.logger.write_line('%s does not validate with twitter' % handle)
        return False

    #self.logger.write_line('exiting getTwitter function')

def dontBreak(self):

    send_message_to_player('This attribute "%s" has been passed. Functionality coming soon.' % self.attr)
    pass

def send_message_to_player(message):

    print '\n%s\n' % str(message)
    
def get_cmd_from_player():

    cmd = raw_input('>>>   ')

    if cmd == 'help':
        print "I can't give you any help I am to dumb right now...."
        pass
    if cmd == 'quit':
        send_message_to_player('Are you sure you want to Quit the Builder?')
        quitTrue = get_cmd_from_player()
        if quitTrue == 'yes':
            print 'yes quit'
        else:
            pass
    else:
        return cmd