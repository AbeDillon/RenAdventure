import threading
import textwrap
import Queue
import time
import copy
import engine
import Q2logging
import twitter
import os


class BuilderThread(threading.Thread):
    """
    Room builder thread
    """

    def __init__(self, type_of_object, cmd_queue, msg_queue, game_cmd_queue, room_coords=None, player_name=""):
        """
        Initialize a Room Builder thread
        """
        
        threading.Thread.__init__(self)
        self.type = type_of_object # being built
        self.cmd_queue = cmd_queue
        self.msg_queue = msg_queue
        self.game_cmd_queue = game_cmd_queue
        self.room_coords = room_coords
        self.player_name = player_name
        self.prototype = {}
        self.logger = Q2logging.out_file_instance('logs/builder/'+player_name)
        if self.type == "room":
            self.prototype["name"] = room_coords
        
        
        
    def run(self):
        """
        
        """
        self.logger.write_line( 'Builder Initiated, Type = '+ self.type)
        if self.type == "room":
            self.buildRoom()
        elif self.type == "portal":
            self.buildPortal()
        elif self.type == "item":
            self.buildItem()
        elif self.type == "npc":
            self.buildNPC()
        else:
            pass # replace with error logging
            
    def buildRoom(self):
        
        text = textwrap.fill('In this module you will be building a "room" or "area" to your liking with some limits of course.  '
                        'We will walk you through the process of building and populating the room with things like Portals, '
                        'Containers, Items, and some other stuff.  So lets get started.', width=100).strip()
        self.logger.write_line('Entered build room Function.')               
        self.send_message_to_player(text)
        self.logger.write_line('Sent to addDescription Function.')
        self.addDescription()
        self.logger.write_line('Sent to addPortals Function.')
        self.addPortals()
        self.logger.write_line('Sent to addItems Function.')
        self.addItems()
        self.logger.write_line('skips adding NPC WE NEED BUIDLER/SELECTOR.')
        #add functionality for placing NPCs
        self.logger.write_line('Sent to reviewObject function.')
        self.reviewObject()
        self.logger.write_line('Sent to makeRoom function.')
        self.makeRoom()
        self.logger.write_line('Exited room builder.')
    
    def buildPortal(self):
        """
        function to build a portal step by step.  Direction has been predetermined from room builder function.
        """
        self.logger.write_line('Arrived buildPortal function')
        self.logger.write_line('Send to addName')
        
        # Name Portal 
        self.addName()
        self.logger.write_line('Send to addDescription')
        
        # Description
        self.addDescription()
        self.logger.write_line('Send to addInspectionDescription')
        
        # Inspection Description
        self.addInspectionDescription()
        self.logger.write_line('Send to getDirection function')
        
        # Direction
        direction = self.getDirection()
        self.logger.write_line('Send to assignCoords function w/ direction = '+direction)
        
        # Coords        
        self.assignCoords(direction)
        self.logger.write_line('Send to isLocked function.')
        
        # Locked        
        self.isLocked()
        self.logger.write_line('Send to addKey function.')
            
        # Key        
        self.addKey()
        self.logger.write_line('Send to isHidden function.')
        
        # Hidden        
        self.isHidden()
        self.logger.write_line('Send to buildScripts Function')
        
        # Scripts        
        self.buildScripts()        
        self.logger.write_line('Send to reviewObject Function')
        
        #review object
        self.reviewObject()
        self.logger.write_line('Send to makePortal Function.')
        
        #make portal
        self.makePortal()
        
        self.logger.write_line('exit buildPortal function')
        
    def buildItem(self):
        """
        function to build items
        """
        self.logger.write_line('arrive buildItem function')
        self.logger.write_line('send to addName function')
        #Name Item
        self.addName()
        self.logger.write_line('send to addDescription function')
        
        #Item Description
        self.addDescription()
        self.logger.write_line('send to addInspectionDescription function')
        
        #Inspection Description
        self.addInspectionDescription()
        self.logger.write_line('send to buildScripts function')
        
        #Scripts
        self.buildScripts()
        self.logger.write_line('send to isPortable function')
        
        #Portable
        self.isPortable()
        self.logger.write_line('send to isHidden function')
        
        #Hidden
        self.isHidden()
        self.logger.write_line('send to isContainer function')
        
        #Container
        self.isContainer()

        if self.prototype['container'] == True:
            #locked
            self.logger.write_line('send to isLocked function')
            self.isLocked()
            self.logger.write_line('send to addKey function')
            #key
            self.addKey()
            self.logger.write_line('send to addItems function')
            #items in item
            self.addItems()
        else:
            self.prototype['locked'] = False
            self.prototype['key'] = None
            self.prototype['items'] = []
            self.logger.write_line('container = False so prototype locked = False, key = none, items = [] values set')
        self.logger.write_line('send to reviewObject function')
        
        #review object    
        self.reviewObject()
        self.logger.write_line('send to makeItem function')
        
        #review makeItem
        self.makeItem()
        
        self.logger.write_line('exit buildItem function')
        
    def buildNPC(self):
        """
        Function for Building Non Player Characters
        name = 
        coords = 
        affiliation = 
        twitter feed = 
        """
        self.logger.write_line('entered build NPC function')
        self.logger.write_line('send to addName function')
        # name NPC
        self.addName()
        self.logger.write_line('send to getValidCoords function')
        
        # Get starting coords
        self.getValidCoords()
        self.logger.write_line('send to getTwitter function')
        
        #Twitter handle
        self.getTwitter()
        self.logger.write_line('send to getAffiliation function')
        
        # affiliation
        self.getAffiliation()
    
    def buildScripts(self):
        """
        Function to build out Action scripts for Items and Portals
        """
        self.logger.write_line('entered buildScripts Function')
        
        # list of valid verbs (populate when builder is run) from engine
        valid_verbs = ['take', 'drop', 'move']  # this list needs to be made dynamic
        scripts = {}
        
        intro_text = '\n' +textwrap.fill('You can [b]uild a script for this '+self.type+', e[x]it scripts, or get [h]elp?  What is your preference?', width=100).strip()
        valid_responses = (('build', 'b'), ('exit', 'x'), ('help', 'h'))
        #get user input
        ans = self.get_valid_response(intro_text, validResponses=valid_responses)
        self.logger.write_line('user input recieved = '+ str(ans))
        while ans != 'exit':
            if ans == 'build':
               self.logger.write_line('entered build script get valid verb')
               # get verb
               while 1:
                   verb_text = '\n'+textwrap.fill('Enter the verb you wish to replace.')
                   self.send_message_to_player(verb_text)
                   verb = self.get_cmd_from_player()
                   self.logger.write_line('verb to replace, input recieved = '+str(verb))
                   if verb in valid_verbs:
                       self.logger.write_line(str(verb) + ' found in list & accepted')
                       break
                   else:
                       self.logger.write_line(str(verb) + ' not in list & rejected')
                       self.send_message_to_player('The verb must be in list of valid verbs try again.')
               # get actions
               self.logger.write_line('begin getting actions.')
               action_list = []
               self.send_message_to_player(action_list)
               action_text = '\n' + textwrap.fill('Enter the a action(s) you want to happen. Example - take apple 3 or take apple 3, take knife 0').strip()
               
               actions_complete = False
               while actions_complete == False:    
                   self.send_message_to_player(action_text)
                   actions = self.get_cmd_from_player().strip().split(', ')
                   self.logger.write_line('input recieved = ' +str(actions))
                   for action in actions:
                       self.logger.write_line(str(action)+ 'sent for validation')
                       valid_action = self.validateAction(action)
                       if valid_action != None:
                           action_list.append(valid_action)
                           self.logger.write_line('action appended to list.  List now looks like '+str(action_list))
                   done_action_text = '\n'+textwrap.fill('Do you want to [a]dd more action(s) for this verb or are you [d]one with actions?', width=100).strip()
                   done_valid_response = (('add', 'a'), ('done', 'd'))
                   ans = self.get_valid_response(done_action_text,validResponses=done_valid_response)
                   self.logger.write_line('get done response = ' + str(ans))
                   if ans == 'done':
                       actions_complete = True
                       self.logger.write_line('exit actions portion of script builder')        
               scripts[verb] = tuple(action_list)
               self.logger.write_line('scripts dict appended action list converted.  Now looks like  '+str(scripts))
               #prompt scripts again for another one
               ans = self.get_valid_response(intro_text, validResponses=valid_responses)
               self.logger.write_line('got input for scripts text. = '+str(ans))
            elif ans == 'help':
                # User wants help
                self.logger.write_line('send to scriptsHelp function')
                self.scriptsHelp()
                ans = self.get_valid_response(intro_text, validResponses=valid_responses)
                self.logger.write_line('got input for scripts text. = '+str(ans))
        
        self.prototype['scripts'] = scripts
        self.send_message_to_player(str(self.prototype['scripts']))
        self.logger.write_line('wrote scripts to prototype looks like '+str(scripts))
        self.logger.write_line('exit buildScripts function')
        
    def scriptsHelp(self):
        
        self.logger.write_line('arrive scriptsHelp function')
        help_text = '\n' +textwrap.fill('Scripts are commands that run in place of the command given on this '+self.type+'.   For example if you are '
                                        'making an apple you could make it so that if they say "take apple" you can have it open a portal in the room and/or '
                                        'reveal a chest.  Remember, if you do this and  you still want to have the player take the apple you have to include '
                                        'that in the list of actions to be performed.', width=100).strip()+'\n'
    
        help_text2 = '\n'+textwrap.fill('Here is how it works.  You give us a verb (the first word of a command) that you want to replace with another action or '
                                        'actions.  Then you give us the action(s) you want to happen along with a number that will represent '
                                        'a delay (in seconds) that will occur before that action happens. You can add an unlimited number of actions '
                                        'for each verb replaced.  Each action will be entered in a sentence type format with a space between each portion.  '
                                        'The standard format is verb object delay which could look like.... take apple 2 or drop red bucket 0.', width=100).strip()+ '\n'
        
        help_text3 = '\n'+textwrap.fill('Now a word about delays.  Delays will not start until all the delays before them have completed.  '
                                        'For example -  if you were to replace the verb "take" on the item "apple" with take apple 0, go north 3, drop apple 2 '
                                        'The player that issued the command "take apple" would instead take the apple immediately, wait 3 seconds and move north, '
                                        'wait another 2 seconds and drop the apple.  As you can see this could get rather interesting.',width=100) + '\n'
        
        help_text4 = '\n'+textwrap.fill('And finally, if you want to add multiple actions that happen you can enter each individual action seperated by a comma.  '
                                        'For example 3 actions would be entered like this take apple 0, drop apple 5, go north 3.  We hope that helps and you are '
                                        'well on your way to making this game extra fun for everyone!', width=100).strip() + '\n'
        
        self.send_message_to_player(str(help_text + help_text2 + help_text3 + help_text4))
                                    
        self.logger.write_line('exit scriptsHelp function')
        
    def validateAction(self, action):
        """  function to validate actions portion f a script 
        returns None for invalid action and tuple (verb, object, delay) for valid actions
        """
        self.logger.write_line('enter validateActions function w/action = '+str(action))
        print_action = action
        action = action.split(" ")    
        verb = action[0]
        object = str(action[1:-1]).strip('[]').replace("'", "").replace(",", "")
        delay = action[-1]
        
        if len(action) < 3:
            noAccept = '\n'+print_action+' was not accepted.  It must contain 3 parts verb object delay.'
            self.send_message_to_player(noAccept)
            self.logger.write_line('action rejected len < 3')
            return None
        else:
            try:
                delay = int(delay)
                self.logger.write_line('action accepted & returned ('+str(verb)+', '+str(object)+', '+str(delay)+')')
                return (verb, object, delay)
            except:
                noAccept = '\n'+print_action+' was not accepted.  The delay portion must be a whole number integer.'
                self.send_message_to_player(noAccept)
                slef.logger.write_line('action not accepted delay not integer.')
                return None
    
    def review_room():
        """
        
        """
        self.logger.write_line('entered reviewRoom function')
        self.logger.write_line('exiting reviewRoom function')
        
    def addName(self):
        """
        function for adding a name
        does not allow names that have already been used.
        """
        self.logger.write_line('enter addName function.  type of object = '+str(self.type))
        text = '\n' +textwrap.fill ('Enter a name for the ' + self.type , width=100).strip()
        accept_text = '\n' +textwrap.fill ('Name accepted for the ' + self.type , width=100).strip()
        deny = '\n' + textwrap.fill('That name has already been used try again.',  width=100).strip()
        self.send_message_to_player(text)
        name = self.get_cmd_from_player()
        # I tried using the check name function for all this validating but it would have required locking the objects 2 times once for search and
        # once for write.  I wanted to avoid that so I left as 2 different functions.  Cannot alter check name in such a way as to make it not append
        # write none types for names when adding items and keys by name.
        
        if self.type != 'npc':  # For Items (NPC's require seperate name validation) 
            self.logger.write_line('name input = '+str(name)+ ', validating as non NPC type')
            
            while True:
                exist_flag = False            
                engine._Characters_Lock.acquire()
                self.logger.write_line('characters list lock acquired')
                if name in engine._Characters:
                    exist_flag = True
                    engine._Characters_Lock.release()
                    self.send_message_to_player(deny)
                    self.logger.write_line('name in characters list, name denied , characters lock released')
                else:
                    engine._Characters_Lock.release()
                    self.logger.write_line('name not in characters list, Characters lock released')           
        
                if exist_flag == False:
                    engine._Objects_Lock.acquire()
                    self.logger.write_line('objects lock acquired')
                    if name not in engine._Objects:                        
                        engine._Objects[name] = None
                        engine._Objects_Lock.release()
                        self.logger.write_line('name not in list, _Objects[name] = none inserted, Objects lock released')
                        break                        
                    else:
                        engine._Objects_Lock.release()
                        self.send_message_to_player(deny)
                        self.write_line('name in _objects list, name denied, Objects lock released')
                #reprompt player
                self.send_message_to_player(text)
                name = self.get_cmd_from_player() 
                
        if self.type == 'npc':
            pass
            #  finish when we determine more about building npcs
        
        self.prototype['name'] = name
        self.logger.write_line(str(name)+' accepted written to '+str(self.type)+ ' prototype')
        
        self.send_message_to_player(str(self.prototype))
        self.logger.write_line('exiting addName function')

    def checkName(self):
        """
        function to take name and check if it exists or not returns tuple (name, T/F flag)       
        """
        self.logger.write_line('enter checkName function')
        # Get desired name
        text = '\n' +textwrap.fill ('Enter a name for the ' + self.type , width=100).strip()
        self.send_message_to_player(text)
        name = self.get_cmd_from_player()
        self.logger.write_line('input recieved = '+str(name))
        
        exist_flag = False
        self.logger.write_line('checking non NPC type')
        engine._Characters_Lock.acquire()
        self.logger.write_line('characters lock acquired')
        if name in engine._Characters:
            exist_flag = True
        engine._Characters_Lock.release()  
        self.logger.write_line('name checked characters lock released')          
        
        if exist_flag == False:
            engine._Objects_Lock.acquire()
            self.logger.write_line('objects lock acquired')
            if name in engine._Objects:            
                exist_flag = True                        
            engine._Objects_Lock.release()
            self.logger.write_line('name checked objects lock released')
        
        if exist_flag == True:
            self.logger.write_line('exiting checkName returned ('+str(name)+', True)')
            return (name,True)
        else:
            self.logger.write_line('exiting checkName returned ('+str(name)+', False)')
            return (name,False)
    
    def addDescription(self):
        """
        function for adding a general description
        """
        self.logger.write_line('entered addDescription function')
        text = '\n' +textwrap.fill ('Enter a description for the ' + self.type , width=100).strip()
                                    
        self.send_message_to_player(text)        
        desc = self.get_cmd_from_player()        
        self.logger.write_line('input rec = '+str(desc))
        
        self.prototype['description'] = desc
        self.send_message_to_player(str(self.prototype))
        self.logger.write_line('prototype[description] = '+str(self.prototype['description']+ ' exiting add description'))
 
    def addInspectionDescription(self):
        """
        Function for adding Inspection Description
        """
        self.logger.write_line('entered addInspectionDescription function')
        text = '\n' +textwrap.fill ('Enter an inspection (more detailed) description for the ' + self.type , width=100).strip()
                                    
        self.send_message_to_player(text)        
        i_desc = self.get_cmd_from_player()
        self.logger.write_line('input rec = '+str(i_desc))        
        
        self.prototype['inspection_description'] = i_desc
        self.send_message_to_player(str(self.prototype))
        self.logger.write_line('prototype[inspection_description] = '+str(self.prototype['inspection_description']+ ' exiting addInspectionDescription'))        
        
    def getAffiliation(self):
        """function to assign affilliatons for NPC.  Possible to use it for players also."""
        
        self.logger.write_line('enter getAffiliation function')
        entry_text = '\n'+textwrap.fill('We need you to place these 5 people in order of how well your %s likes these people.  1 will represent the '
                                        'person your %s likes the most 5 will be the one they like the least.  each number can only be used one time.'
                                        'Those people are...'%(self.type, self.type), width=100).strip()
        #set "table" with lists/dicts to work with
        affiliation = {}
        aff_list = ['Obama', 'Kanye', 'O''Rielly', 'Gotfried', 'Burbiglia']
        num_list = [1,2,3,4,5]
        #Entry text
        self.send_message_to_player(entry_text+'\n')
        for name in aff_list: #loop just to print 
            self.send_message_to_player(name)        
        #start ranking
        self.logger.write_line('begin affiliation ranking')
        for name in aff_list: # loop for input
            rank_text = '\n'+ textwrap.fill('Please rank %s from 1 to 5,  with 1 being your favorite and 5 your least favorite.'%name, width=100)
            self.send_message_to_player(rank_text)
            ans= self.get_cmd_from_player()
            self.logger.write_line('name = %s, ans = %d') % (name, ans)
            while ans not in num_list: #if answer not available
                self.send_message_to_player('Invlaid response.  Each number can only be used once.  Try again\n')                
                # message and prompt again
                self.send_message_to_player(rank_text)
                ans= self.get_cmd_from_player()
                self.logger.write_line('ans = %d, not valid or available prompt again.')%ans
            # answer is available write to dict remove answer so cannot be used again
            affiliation[name] = ans
            num_list.remove(ans)
            self.logger.write_line('affiliation written = %s : %s')% (name, str(affiliation[name]))
        
        self.prototype['affiliation'] = affiliation   
        self.logger.write_line('getAffiliations complete exiting function with prototype[affiliations] = %s')% str(self.prototype['affiliations'])
    
    def getDirection(self):
        """
        function to get desired direction
        returns direction
        """
        
        self.logger.write_line('arrive getDirection function')
        dir_text = '\n' + textwrap.fill('Specify the direction the portal leads ([n]orth, [s]outh, [e]ast, [w]est, [u]p, [d]own, [i]n, or [o]ut).',  width=100).strip()
        valid_responses = (("north", "n"), ("south", "s"), ("east", "e"), ("west", "w"), ('up', 'u'), ('down', 'd'), ("in", "i"), ("out", "o"))
        
        direction = self.get_valid_response(dir_text, validResponses = valid_responses)
        
        self.prototype['direction'] = direction
        self.logger.write_line('response recieved = '+str(direction) + ' & assigned to protoype[direction]')
        self.logger.write_line('returning '+str(direction)+ ' exiting getDirection function')
        return direction

    def getTwitter(self):
        """ Function to get a valid Twitter user handle
        creates file for valid handle that crawler accesses and writes to """ 
        
        self.logger.write_line('entered getTwitter function')
        
        self.logger.write_line('make list of Twitter Handles we already crawl')
        path = (os.listdir(os.getcwd() + "\\twitterFeeds"))
        handles = []
        
        for filename in path:
            name = filename.lower().split('.')
            name = name[0]
            handles.append(name)
            self.logger.write_line('Appended the handle %s to the handles list' % name)
        self.logger.write_line('END OF HANDLES LIST')
        
        handle_text = '\n'+textwrap.fill('Enter a valid twitter handle for this Non Player Character.', width = 100)
        accept_text = '\n'+textwrap.fill('The Twitter handle ' +str(handle)+ ' has been validated and accepted.')
        deny_text = '\n'+textwrap.fill('The Twitter handle ' +str(handle)+ ' cannot be validated try again.')
        
        # get handle
        while True:    
            valid_handle = False
            self.send_message_to_player(handle_text)
            handle = self.get_cmd_from_player().lower() #twitter handles are all lower...itized  :-)
            if handle in handles:
                #name already being scraped break validation loop
                break
            if handle not in handles:
                #check twitter
                try:  # twitter api throws error if name does not exist
                    api = twitter.Api()
                    api.GetUser(str(handle))
                    self.logger.write_line(str(handle)+ ' validated as twitter handle')
                    valid_handle = True               
                except:
                    self.logger.write_line(str(handle)+ ' does not validate with twitter')
                    pass
                                            
            if valid_handle == True:
                # make file in \\twitterfeeds
                fout = open('twitterFeeds\\' + str(handle) + '.txt', 'a')
                self.logger.write_line('file created for crawler at twitterFeeds\\'+str(handle)+'.txt')
                fout.close()
                break

        self.prototype['twitter'] = str(handle)        
        self.send_message_to_player(accept_text)
        self.logger.write_line('exiting getTwitter function, prototype[twitter] = '+self.prototype['twitter'])
        
    def getValidCoords(self):
        """
        function to get valid Coords
        """
        self.logger.write_line('arrive getValidCoords function')
        ask_coords = '\n' + textwrap.fill('Enter your 4 part coordinates seperated by a space. For Example  - 4 3 12 5', width=100).strip()
        coords = self.get_cmd_from_player(ask_coords).split(" ")
        self.logger.write_line('input rec = '+ str(coords))
        
        valid_coords = False
        while valid_coords == False:
            if len(coords) != 4:
                deny_text = '\n' + textwrap.fill('Your input must be 4 whole numbers seperated by a space.')
                self.send_message_to_player(deny_text)
                self.logger.write_line('coords denied not valid length')
                # prompt again
                coords = self.get_cmd_from_player(ask_coords).split(" ")
                self.logger.write_line('new input = '+str(coords))
            else:
                try:
                    x, y, z, a = coords
                    (int(x), int(y), int(z), int(a))
                    self.prototype['coords'] = (x,y,z,a)
                    self.logger.write_line('coords validate prototype[coords] = '+str((x,y,z,a)))
                    self.send_message_to_player('\nYour coordinates have been accepted')
                    valid_coords = True
                except:
                    self.send_message_to_player(deny_text)
                    coords = self.get_cmd_from_player(ask_coords).split(" ")
                    self.logger.write_line('coords not integers.  new input = '+str(coords))
        
        self.logger.write_line('exiting getValidCoords function')
        
    
    def assignCoords(self, direction):    
        """ function to assign coordinates for item based upon 
        room coordinates and direction given.  Typical use portal
        destination assignment
        """
        self.logger.write_line('entering assignCoords with direction param = '+str(direction)+ ', room_coords = '+str(self.room_coords))
        
        coords = self.room_coords
        x,y,z,a = coords
        if direction == 'north':
            coords = (x, y+1, z, a) 
        elif direction == 'south':
            coords = (x, y-1, z, a)
        elif direction == 'west':
            coords = (x-1, y, z, a)
        elif direction == 'east':
            coords = (x+1, y, z, a)
        elif direction == 'up':
            coords = (x, y,z+1, a)
        elif direction == 'down':
            coords = (x,y,z-1, a)
        elif direction == 'in':
            coords = (x,y,z,a+1)
        elif direction == 'out':
            coords = (x,y,z,a-1)
    
        self.prototype['coords'] = coords
        self.send_message_to_player(str(self.prototype))
        self.logger.write_line('exiting assignCoords, prototype[coords] = '+str(self.prototype['coords']))
        
        
    def isLocked(self):
        """
        Function to define lock state
        """
        self.logger.write_line('entering isLocked function')
        lock_text = '\n' + textwrap.fill('This ' +self.type+ ' can be [l]ocked or [u]nlocked.  Which do you prefer?',  width=100).strip()
        valid_responses = (('unlocked', 'u'), ('locked', 'l'))
        
        lock_state = self.get_valid_response(lock_text, validResponses=valid_responses)
        self.logger.write_line('input recieved = '+str(lock_state))
        
        if lock_state == 'unlocked':
            self.prototype['locked'] = False
        else:
            self.prototype['locked'] = True
        
        self.logger.write_line('exiting isLocked, prototype[locked] = '+str(self.prototype['locked']))    
        self.send_message_to_player(str(self.prototype))        
    
    def addKey(self):
        """
        Function to add a key to items and portals
        """
        self.logger.write_line('entered addKey function')
        key_text = '\n' + textwrap.fill('This ' +self.type+ ' can have a key (any item).  Do you want to [n]ame a key, [b]uild a key,  or leave it [k]eyless?',  width=100).strip()
        valid_responses = (('name', 'n'), ('build', 'b'), ('keyless', 'k'))
        ans = self.get_valid_response(key_text, validResponses=valid_responses)
        self.logger.write_line('input rec = '+str(ans))
        
        key = None
        while ans != 'keyless':
            orig_type = self.type #capture type we are currently making
            self.type = 'key' #change type to key for proper wording in functions
            self.logger.write_line('type changed from '+str(orig_type)+ ' to '+str(self.type))
            if ans == 'name':
                # get key name
                self.logger.write_line(' Player provideing name of existing item sending to checkName function.')
                check_name = self.checkName() # check name returns Tuple (name, T/F)
                name = check_name[0]
                flag = check_name[1]
                self.logger.write_line('Check name parsed = ' +str(name)+ ' ' +str(flag))
                if flag == True: #name was accepted
                    key = name
                    self.prototype['key'] = key
                    accept = '\n' + textwrap.fill('The '+str(name)+ ' is now the key to your '+str(orig_type)+'.', width=100).strip()        
                    self.logger.write_line('name accepted prototype[key] = '+str(self.prototype['key']))
                    self.send_message_to_player(accept)
                    ans = 'keyless' #break loop
                else:
                    deny = '\n' +textwrap.fill('We cannot find '+str(name)+'.  You will have to try again.', width=100).strip()
                    self.send_message_to_player(deny)
                    self.logger.write_line('name not accepted.')
                    
            else:
                # copy dict we were working on before side tracking to the new object creator
                self.logger.write_line('user wants to build item as key')
                temp_prototype = copy.deepcopy(self.prototype)
                self.prototype = {} # open new dict for the new item
                self.logger.write_line('prototype copied and new prototype established.  Sending to buildItem')
                self.buildItem()
                self.logger.write_line('return to addKey from buildItem')
                # capture name of key
                key = self.prototype['name']
                self.logger.write_line('key name captured from item created = '+str(key))               
                # restore original prototype
                self.prototype = temp_prototype
                self.logger.write_line('original prototype restored')
                ans = 'keyless' #    break loop
        
            # reset temp type
            self.type = orig_type  # set type back to original type
            self.logger.write_line('self.type (original type) restored = '+ str(orig_type))
        # set value of original prototype key
        self.prototype['key'] = key
        self.logger.write_line('prototype[key] = '+ str(self.prototype['key']))
        self.send_message_to_player(str(self.prototype))
        
        
    def isPortable(self):
        """
        Function sets portability state
        """
        self.logger.write_line('entered isPortable function')
        portable_text = '\n' + textwrap.fill('Items can be [p]ortable or [n]on portable affecting players ability to pick them up.  Which do you prefer?',  width=100).strip()
        valid_responses = (('portable', 'p'), ('non portable', 'n'))
        
        portable_state = self.get_valid_response(portable_text, validResponses=valid_responses)
        self.logger.write_line('input recieved = '+portable_state)
        
        if portable_state == "portable":
            self.prototype['portable'] = True            
        else:
            self.prototype['portable'] = False
        
        self.logger.write_line('exiting isPortable with prototype[portable] = '+str(self.prototype['portable']))    
        self.send_message_to_player(str(self.prototype))
            
    def isHidden(self):
        """
        Function sets hidden state
        """
        self.logger.write_line('entered isHidden function')
        hidden_text = '\n' + textwrap.fill('This ' +str(self.type)+ ' can be [h]idden or [v]isible.  Which do you prefer?',  width=100).strip()
        valid_responses = (('hidden', 'h'), ('visible', 'v'))
        
        hidden_state = self.get_valid_response(hidden_text, validResponses=valid_responses)
        self.logger.write_line('input recieved = '+hidden_state)
        
        if hidden_state == "hidden":
            self.prototype['hidden'] = True
        else:
            self.prototype['hidden'] = False
        
        self.logger.write_line('exiting isHidden with prototype[hidden] = '+str(self.prototype['hidden']))    
        self.send_message_to_player(str(self.prototype))
    
    def isContainer(self):
        """
        Function sets Container flag (bool)
        """
        self.logger.write_line('entered isContainer function')
        container_text = '\n' + textwrap.fill('Items can be containers that hold other items. Do you want to make it a container?  [y]es or [n]o',  width=100).strip()
                
        container_state = self.get_valid_response(container_text)
        self.logger.write_line('input recieved = '+str(container_state))
        
        if container_state == "yes":
            self.prototype['container'] = True
        else:
            self.prototype['container'] = False
            
        self.logger.write_line('exiting isContainer with prototype[container] = '+str(self.prototype['container']))
        self.send_message_to_player(str(self.prototype))
            
    def addPortals(self):
        """
        
        """        
        self.logger.write_line('enter addPortals Function')
        portals = {}
        #  confirm they want to add portal(s)
        portal_text = '\n' + textwrap.fill('Portals (doors) can be added to your room. Do you want to add portal?  [y]es or [n]o',  width=100).strip()
        more_portal = '\n' + textwrap.fill('Do you want to add another Portal?  [y]es or [n]o')               
          
        # save the current room prototype because calling the buildPortal function will clobber it
        temp_prototype = copy.deepcopy(self.prototype)
        temp_type = copy.copy(self.type)
        self.logger.write_line('prototype & type copied as ' +str(temp_type) + ' & ' + str(temp_prototype))
        ans = self.get_valid_response(portal_text) # default is yes/no 
        
        while True: 
            if ans == 'yes':                             
                
                self.logger.write_line('make portal? input recieved =' +str(ans))
                self.type = "portal"
                self.prototype = {}
                # build a new portal
                self.logger.write_line('type = ' +self.type+ ' empty prototype established.  Send to buildPortal function')
                self.buildPortal()
                # get the portal's name
                name = self.prototype['name']
                self.logger.write_line('returned to addPortals from buildPortal captured name of portal created = '+name)
                #add to dict for room
                portals[name] = portals.get(name, 0) + 1
                self.logger.write_line('portals dict for room to now looks like ' + str(portals)+ ' Prompt again....')
                #prompt for more
                ans = self.get_valid_response(more_portal)
                self.logger.write_line('user prompted for adding more portals (y or n)')
            else:
                self.logger.write_line('make portal?  input recieved = '+str(ans))
                break
                
        # restore the prototype to the room prototype
        self.prototype = temp_prototype
        self.type = temp_type
        self.logger.write_line('begin exit from buildPortals Function.  Restored temp prototoype and type as self')
        # add the portals to the room prototype
        self.prototype['portals'] = portals
        self.logger.write_line('exiting addPortals with prototype[portals] = '+str(self.prototype['portals']))
        
    def addItems(self):
        """
        Function for adding items to a room or a container item.
        """
        self.logger.write_line('entered addItems function')
        items = {}
        
        #  confirm they want to add item(s)
        item_text = '\n' + textwrap.fill('Items can be added to your ' +self.type+ '.  Enter your choice add a [n]ew item, name an [e]xisting item, or e[x]it.',  width=100).strip()
        valid_responses = (("new", "n"), ("existing", "e"), ("exit", "x"))
        
        ans = self.get_valid_response(item_text, validResponses=valid_responses)
        self.logger.write_line('input to work with = '+str(ans))
        
        #ensure type to Item for proper dynamic printing
        temp_type = copy.copy(self.type)
        self.type = "item"
        self.logger.write_line('type copied as temp_type. self.type set to item')
        
        while ans != 'exit':
            # add an existing item by name
            if ans == "existing":
                # ask them item name
                self.logger.write_line('user desires to name existing item.  send to check name function')
                check_name = self.checkName() # check name returns Tuple (name, bool (T/F))
                name = check_name[0]
                flag = check_name[1]
                self.logger.write_line('input received and parsed name = '+str(name)+' flag = '+str(flag))
                if flag == True: #name was accepted
                    #append name to item dict
                    items[name] = items.get(name, 0) + 1
                    accept = '\n' + textwrap.fill('The '+str(name)+ ' has been added to your '+str(temp_type)+'.', width=100).strip()        
                    self.send_message_to_player(accept)
                    self.logger.write_line(name+' existed added to items dict which looks like... '+str(items))
                    ans = 'exit'
                else:
                    deny = '\n' +textwrap.fill('We cannot find the '+str(name)+', try again.', width=100).strip()
                    self.send_message_to_player(deny)
                    self.logger.write_line('name not found.')
                    
            # build an item
            else:                
                # save the current prototype because calling the buildItem function will clobber it
                temp_prototype = copy.deepcopy(self.prototype)
                # initialize the prototype for the buildItem function
                self.prototype = {}
                # build a new item
                self.logger.write_line('user says build item, copy current prototype as temp_prototype, establish empty prototype for new item, send to buildItem function')
                self.buildItem()
                # capture the item's name
                name = self.prototype["name"]
                self.logger.write_line('returned to addItems from buildItem, capture name = '+ str(name))
                # add that item to the list of items
                items[name] = items.get(name, 0) + 1
                self.logger.write_line('item added to Items dict which now looks like.... ' + str(items))
                item_text2 = '\n' +textwrap.fill('Your ' + str(self.type) + ' has been added to ' +str(temp_type)+ ' list. Now what do you want to do?', width= 100).strip()
                self.send_message_to_player(item_text2)
                # restore original prototype
                self.prototype = temp_prototype
                self.logger.write_line('original prototype restored.')
                ans = 'exit'                    
            
            # prompt the user again
            ans = self.get_valid_response(item_text, validResponses=valid_responses)
            self.logger.write_line('prompt again input = '+str(ans))
        self.type = temp_type
        # add the items to the prototype
        self.prototype['items'] = items
        self.logger.write_line('type restored to temp_type ('+str(temp_type)+'), items written to prototype[items] ='+str(self.prototype['items']) )
        
    def reviewObject(self):
        """
        function to display the object created and allow for the player to make edits.
        """
        self.logger.write_line('enter reviewObject function')
        self.send_message_to_player('Here is a look at the characteristics of your '+str(self.type)+'.')
        self.logger.write_line('send to printObject function')
        self.printObject()
        
        self.logger.write_line('exit reviewObject function')
        #I want to add editing capabilities here later hence the review object and print object functions
    
    def printObject(self):
        """
        Displays object in printable format.
        """
        self.logger.write_line('enter printObject function')
        
        text = ""
        for key in self.prototype:
            text += key + '=   ' + str(self.prototype[key]) + "\n"
            
        self.send_message_to_player(text)
        self.logger.write_line('exit printObject function')
        
    def makeRoom(self):
        """
        parses the current protoype dict and instantiates a room
        """
        self.logger.write_line('arrive makeRoom function')
        self.send_message_to_player('Your '+str(self.type)+' is being built.')
        
        desc = self.prototype['description']
        portals = self.prototype['portals']
        items = self.prototype['items']
        players = [] # updated only by engine
        npcs = []   # when NPC builder complete we need to have this list populated by builder.
        self.logger.write_line('prototype dict parsed to variables')
        
        room = engine.Room(desc, portals, items, players, npcs)
        self.logger.write_line(str(self.type) + ' instantiated @ ' +str(room)+ 'as ' + str(self.prototype))
        self.send_message_to_player("Your "+str(self.type)+" has been built.")
        
        #add room to list of rooms
        # NEED LOCKS OR QUEUE FOR THIS
        engine._Rooms[self.room_coords] = room
        self.logger.write_line('room object added to list of rooms')
        
        # send messsage to game_cmd_queue signaling done with builder.
        self.game_cmd_queue.put((self.player_name, 'done_building', []))
        self.logger.write_line('command sent to game queue to exit builder, exit makeRoom')
    
    def makePortal(self):
        """
        Parses the current Prototype dict and instantiates a portal
        """
        
        self.logger.write_line('arrive makePortal Function')
        self.send_message_to_player('Your '+self.type+' is now being built.')
        name = self.prototype['name']
        desc = self.prototype['description']
        i_desc = self.prototype['inspection_description']
        dir = self.prototype['direction']
        coords = self.prototype['coords']
        locked = self.prototype['locked']
        key = self.prototype['key']
        hidden = self.prototype['hidden']
        scripts = self.prototype['scripts']
        self.logger.write_line('prototype dict parsed to variables')
        
        # Build Portal
        portal = engine.Portal(name, dir, desc, i_desc, coords, scripts = scripts, locked = locked, hidden = hidden, key = key)
        self.logger.write_line(str(self.type) + ' instantiated @ ' +str(portal)+ 'with attribs = ' +str(self.prototype)) 
        
        #write item to objects list
        engine._Objects_Lock.acquire()
        self.logger.write_line('Objects lock acquired')
        engine._Objects[name] = portal
        self.logger.write_line('Objects Dict updated')
        engine._Objects_Lock.release()
        self.logger.write_line('Objects lock released')        
        
        self.send_message_to_player('Your '+self.type+' has been built.')
        self.logger.write_line('portal built successfully exiting makePortal function')
    
    def makeItem(self):
        """
        parses current prototype Dict and Instantiates an item.
        """
        self.logger.write_line('entered makeItem function')
        self.send_message_to_player('Your '+self.type+ ' is being built.')
        
        name = self.prototype['name']
        desc = self.prototype['description']
        i_desc = self.prototype['inspection_description']
        scripts = self.prototype['scripts']
        portable = self.prototype['portable']
        hidden = self.prototype['hidden']
        container = self.prototype['container']
        locked = self.prototype['locked']
        key = self.prototype['key']
        items = self.prototype['items']
        self.logger.write_line('prototype dict parsed to variables')
        
        item = engine.Item(name, desc, i_desc, scripts = scripts, portable = portable, hidden = hidden, container = container, locked = locked, key = key, items = items)
        self.logger.write_line(str(self.type) + ' instantiated @ ' +str(item)+ 'with attribs = ' +str(self.prototype))
        #write item to objects list
        engine._Objects_Lock.acquire()
        self.logger.write_line('Objects lock acquired')
        engine._Objects[name] = item
        self.logger.write_line('Objects Dict updated')
        engine._Objects_Lock.release()
        self.logger.write_line('Objects lock released')
        
        self.send_message_to_player('Your '+self.type+ ' has been built.')
        self.logger.write_line('makeItem successful exiting function')
                
    def get_valid_response(self, prompt, validResponses=(("yes", "y"), ("no", "n"))):
        """
        ask the player for a valid reponse to a prompt and keep asking until a valid response is received
        """
        self.logger.write_line('enter get_valid_response function')
        # prompt for input
        self.send_message_to_player(prompt)
        
        # build translation dictionary
        translate = {}
        for response in validResponses:
            word = response[0]
            synonym = response[1]
            translate[synonym] = word
        self.logger.write_line('translate dict built')            
        
        while 1:
            response = self.get_cmd_from_player()
            if response in translate: # if the response is in the list of inputs that can be translated to a valid response
                return translate[response] # translate the response and return the result
                self.logger.write_line('response validated returning = '+str(translate[response]))
            else:
                text = '\n' + textwrap.fill('Invalid response. Please respond with: ' + str(translate.keys()),  width=100).strip()
                self.send_message_to_player(text + prompt)
    
    def get_cmd_from_player(self):
        """
        command from player is sent in 3 part tuple (player_name, message, [tag])
        """
        self.logger.write_line('enter get_cmd_from_player function.')
        command = self.cmd_queue.get()
        message = command[1]
        self.logger.write_line('command recieved = '+str(command)+' message = '+ str(message)+', exiting get_cmd_from_player')
        return message

    def send_message_to_player(self, message):
        """
        Packages a message in the (name, msg, tags) format and puts it on the msg_queue
        """
        self.logger.write_line('enter send_message_to_player function')
        
        message_tuple = (self.player_name, message, [])
        
        self.msg_queue.put(message_tuple)
        
        self.logger.write_line('message sent to player = '+str(message_tuple)+' message printed = '+str(message))
