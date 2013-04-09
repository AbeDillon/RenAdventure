import threading
import textwrap
import Queue
import time
import copy
import engine
import Q2logging


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
        
    def buildItem(self):
        """
        function to build items
        """
        #Name Item
        self.addName()
        
        #Item Description
        self.addDescription()
        
        #Inspection Description
        self.addInspectionDescription()
        
        #Scripts
        self.buildScripts()
        
        #Portable
        self.isPortable()
        
        #Hidden
        self.isHidden()
        
        #Container
        self.isContainer()

        if self.prototype['container'] == True:
            #locked
            self.isLocked()
            #key
            self.addKey()
            #items in item
            self.addItems()
        else:
            self.prototype['locked'] = False
            self.prototype['key'] = None
            self.prototype['items'] = []
        
        self.reviewObject()
        
        self.makeItem()
        
    def buildNPC(self):
        """
        Function for Building Non Player Characters
        name = 
        coords = 
        affiliation = 
        twitter feed = 
        """
        # name NPC
        self.addName()
        
        # Get starting coords
        self.getValidCoords()
        
        #Twitter handle
    
    def buildScripts(self):
        """
        Function to build out Action scripts for Items and Portals
        """
        # list of valid verbs (populate when builder is run) from engine
        valid_verbs = ['take', 'drop', 'move']  # this list needs to be made dynamic
        scripts = {}
        
        intro_text = '\n' +textwrap.fill('You can [b]uild a script for this '+self.type+', e[x]it scripts, or get [h]elp?  What is your preference?', width=100).strip()
        valid_responses = (('build', 'b'), ('exit', 'x'), ('help', 'h'))
        #get user input
        ans = self.get_valid_response(intro_text, validResponses=valid_responses)
        while ans != 'exit':
            if ans == 'build':
               # get verb
               while 1:
                   verb_text = '\n'+textwrap.fill('Enter the verb you wish to replace.')
                   self.send_message_to_player(verb_text)
                   verb = self.get_cmd_from_player()
                   if verb in valid_verbs:
                       break
                   else:
                       self.send_message_to_player('The verb must be in list of valid verbs try again.')
               # get actions
               action_list = []
               self.send_message_to_player(action_list)
               action_text = '\n' + textwrap.fill('Enter the a action(s) you want to happen. Example - take apple 3 or take apple 3, take knife 0').strip()
               actions_complete = False
               while actions_complete == False:    
                   self.send_message_to_player(action_text)
                   actions = self.get_cmd_from_player().strip().split(', ')
                   for action in actions:
                       valid_action = self.validateAction(action)
                       if valid_action != None:
                           action_list.append(valid_action)
                   done_action_text = '\n'+textwrap.fill('Do you want to [a]dd more action(s) for this verb or are you [d]one with actions?', width=100).strip()
                   done_valid_response = (('add', 'a'), ('done', 'd'))
                   ans = self.get_valid_response(done_action_text,validResponses=done_valid_response)
                   if ans == 'done':
                       actions_complete = True        
               scripts[verb] = tuple(action_list)
               #prompt scripts again for another one
               ans = self.get_valid_response(intro_text, validResponses=valid_responses)
            elif ans == 'help':
                # User wants help
                self.scriptsHelp()
                ans = self.get_valid_response(intro_text, validResponses=valid_responses)
        
        self.prototype['scripts'] = scripts
        self.send_message_to_player(str(self.prototype['scripts']))
        
    def scriptsHelp(self):
        
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
                                    
        
        
    def validateAction(self, action):
        """  function to validate actions portion f a script 
        returns None for invalid action and tuple (verb, object, delay) for valid actions
        """

        print_action = action
        action = action.split(" ")    
        verb = action[0]
        object = str(action[1:-1]).strip('[]').replace("'", "").replace(",", "")
        delay = action[-1]
        
        if len(action) < 3:
            noAccept = '\n'+print_action+' was not accepted.  It must contain 3 parts verb object delay.'
            self.send_message_to_player(noAccept)
            return None
        else:
            try:
                delay = int(delay)
                return (verb, object, delay)
            except:
                noAccept = '\n'+print_action+' was not accepted.  The delay portion must be a whole number integer.'
                self.send_message_to_player(noAccept)
                return None
    
    def review_room():
        """
        
        """
        
    def addName(self):
        """
        function for adding a name
        does not allow names that have already been used.
        """
        text = '\n' +textwrap.fill ('Enter a name for the ' + self.type , width=100).strip()
        deny = '\n' + textwrap.fill('That name has already been used try again.',  width=100).strip()
        accept = '\n' + textwrap.fill('The name has been accepted... moving on.')
        self.send_message_to_player(text)
        name = self.get_cmd_from_player()
        
        if self.type != 'npc':  # For Items (NPC's require seperate name validation) 
            name_accept = False
            while name_accept == False:
            
                engine._Characters_Lock.acquire()
                if name not in engine._Characters:
                    engine._Characters_Lock.release()
                    engine._Objects_Lock.acquire()                
                    if name not in engine._Objects:
                        engine._Objects[name] = None
                        engine._Objects_Lock.release()                        
                        self.send_message_to_player(accept)
                        name_accept = True                
                else:
                    engine._Characters_Lock.release()
                    self.send_message_to_player(deny)
                    # prompt player again            
                    name = self.get_cmd_from_player()
        
        if self.type == 'npc':
            pass
            #  finish when we determine more about building npcs
        
        self.prototype['name'] = name
        msg = str(self.prototype)
        self.send_message_to_player(msg)

    def checkName(self):
        """
        function to make sure a name being entered is a name that exists
        returns (name entered, T/F flag) tuple        
        """
        # Get desired name
        text = '\n' +textwrap.fill ('Enter a name for the ' + self.type , width=100).strip()
        
        self.send_message_to_player(text)
        name = self.get_cmd_from_player()
        exist_flag = False
        
        engine._Objects_Lock.acquire()
        if name in engine._Objects:            
            exist_flag = True
        engine._Objects_Lock.release()
        
        if exist_flag == False:
            engine._Characters_Lock.acquire()
            if name in engine._Characters:
                exist_flag = True
            engine._Characters_Lock.release()        
        
        if exist_flag == True:
            return (name,True)
        else:
            return (name,False)
    
    # begin room creation
    def addDescription(self):
        """
        function for adding a general description
        """
        text = '\n' +textwrap.fill ('Enter a description for the ' + self.type , width=100).strip()
                                    
        self.send_message_to_player(text)
        
        desc = self.get_cmd_from_player()
        
        self.prototype['description'] = desc
        self.send_message_to_player(str(self.prototype))
 
    def addInspectionDescription(self):
        """
        Function for adding Inspection Description
        """
        
        text = '\n' +textwrap.fill ('Enter an inspection (more detailed) description for the ' + self.type , width=100).strip()
                                    
        self.send_message_to_player(text)
        
        i_desc = self.get_cmd_from_player()
        
        self.prototype['inspection_description'] = i_desc
        self.send_message_to_player(str(self.prototype))
        
    def getDirection(self):
        """
        function to get desired direction
        returns direction
        """
        self.logger.write_line('arrive getDirection function')
        dir_text = '\n' + textwrap.fill('To add a portal, specify the direction you want ([n]orth, [s]outh, [e]ast, [w]est, [u]p, [d]own, [i]n, or [o]ut).',  width=100).strip()
        valid_responses = (("north", "n"), ("south", "s"), ("east", "e"), ("west", "w"), ("in", "i"), ("out", "o"))
        
        direction = self.get_valid_response(dir_text, validResponses = valid_responses)
        
        self.prototype['direction'] = direction
        self.logger.write_line('response recieved = '+str(direction) + ' & assigned to protoype')
        return direction

    
    def getValidCoords(self):
        """
        function to get valid Coords
        """
        ask_coords = '\n' + textwrap.fill('Enter your 4 part coordinates seperated by a space. For Example  - 4 3 12 5', width=100).strip()
        coords = self.get_cmd_from_player(ask_coords).split(" ")
        
        valid_coords = False
        while valid_coords == False:
            if len(coords) != 4:
                deny_text = '\n' + textwrap.fill('Your input must be 4 whole numbers seperated by a space.')
                self.send_message_to_player(deny_text)
                # prompt again
                coords = self.get_cmd_from_player(ask_coords).split(" ")
            else:
                try:
                    x, y, z, d = coords
                    (int(x), int(y), int(z), int(d))
                    self.prototype['coords'] = (x,y,z,d)
                    self.send_message_to_player('\nYour coordinates have been accepted')
                    valid_coords = True
                except:
                    self.send_message_to_player(deny_text)
                    coords = self.get_cmd_from_player(ask_coords).split(" ")
        
        
        
    
    def assignCoords(self, direction):    
        """ function to assign coordinates for item based upon 
        room coordinates and direction given.  Typical use portal
        destination assignment
        """
        coords = self.room_coords
        x,y,z = coords
        if direction == 'north':
            coords = (x, y+1, z) 
        elif direction == 'south':
            coords = (x, y-1, z)
        elif direction == 'west':
            coords = (x-1, y, z)
        elif direction == 'east':
            coords = (x+1, y, z)
        elif direction == 'up':
            coords = (x, y,z+1)
        elif direction == 'down':
            coords = (x,y,z-1)
#        elif direction == 'in':
#            coords = (x,y,z,d+1)
#        elif direction == 'out':
#            coords = (x,y,z,d-1)
    
        self.prototype['coords'] = coords
        self.send_message_to_player(str(self.prototype))
        
    def isLocked(self):
        """
        Function to define lock state
        """
        lock_text = '\n' + textwrap.fill('This ' +self.type+ ' can be [l]ocked or [u]nlocked.  Which do you prefer?',  width=100).strip()
        valid_responses = (('unlocked', 'u'), ('locked', 'l'))
        
        lock_state = self.get_valid_response(lock_text, validResponses=valid_responses)
        if lock_state == 'unlocked':
            self.prototype['locked'] = False
        else:
            self.prototype['locked'] = True
            
        self.send_message_to_player(str(self.prototype))        
    
    def addKey(self):
        """
        Function to add a key to items and portals
        """
        
        key_text = '\n' + textwrap.fill('This ' +self.type+ ' can have a key (any item).  Do you want to [n]ame a key, [b]uild a key,  or leave it [k]eyless?',  width=100).strip()
        valid_responses = (('name', 'n'), ('build', 'b'), ('keyless', 'k'))
        ans = self.get_valid_response(key_text, validResponses=valid_responses)
        
        key = None
        while ans != 'keyless':
            orig_type = self.type #capture type we are currently making
            self.type = 'key' #change type to key for proper wording in functions
            
            if ans == 'name':
                # get key name
                check_name = self.checkName() # check name returns Tuple (name, T/F)
                self.send_message_to_player(str(check_name))
                name = check_name[0]
                flag = check_name[1]
                if flag == True: #name was accepted
                    key = name
                    self.prototype['key'] = key
                    accept = '\n' + textwrap.fill('The '+name+ ' is now the key to your '+orig_type+'.', width=100).strip()        
                    self.send_message_to_player(accept)
                    ans = 'keyless'
                else:
                    deny = '\n' +textwrap.fill('We cannot find '+name+'.', width=100).strip()
                    self.send_message_to_player(deny)
                    
            else:
                # copy dict we were working on before side tracking to the new object creator
                temp_prototype = copy.deepcopy(self.prototype)
                self.prototype = {} # open new dict for the new item
                self.buildItem()
                # capture name of key
                key = self.prototype['name']               
                # restore original prototype
                self.prototype = temp_prototype
                ans = 'keyless'       
        
            # reset temp type
            self.type = orig_type  # set type back to original type
        
        # set value of original prototype key
        self.prototype['key'] = key
        self.send_message_to_player(str(self.prototype))
        
        
    def isPortable(self):
        """
        Function sets portability state
        """
        
        portable_text = '\n' + textwrap.fill('Items can be [p]ortable or [n]on portable affecting players ability to pick them up.  Which do you prefer?',  width=100).strip()
        valid_responses = (('portable', 'p'), ('non portable', 'n'))
        
        portable_state = self.get_valid_response(portable_text, validResponses=valid_responses)
        if portable_state == "portable":
            self.prototype['portable'] = True
        else:
            self.prototype['portable'] = False
            
        self.send_message_to_player(str(self.prototype))
            
    def isHidden(self):
        """
        Function sets hidden state
        """
        
        hidden_text = '\n' + textwrap.fill('This ' +self.type+ ' can be [h]idden or [v]isible.  Which do you prefer?',  width=100).strip()
        valid_responses = (('hidden', 'h'), ('visible', 'v'))
        
        hidden_state = self.get_valid_response(hidden_text, validResponses=valid_responses)
        if hidden_state == "hidden":
            self.prototype['hidden'] = True
        else:
            self.prototype['hidden'] = False
            
        self.send_message_to_player(str(self.prototype))
    
    def isContainer(self):
        """
        Function sets Container flag (bool)
        """
        
        container_text = '\n' + textwrap.fill('Items can be containers that hold other items. Do you want to make it a container?  [y]es or [n]o',  width=100).strip()
                
        container_state = self.get_valid_response(container_text)
        if container_state == "yes":
            self.prototype['container'] = True
        else:
            self.prototype['container'] = False
    
        self.send_message_to_player(str(self.prototype))
            
    def addPortals(self):
        """
        
        """        
        self.logger.write_line('arrive addPortals Function')
        portals = {}
        #  confirm they want to add portal(s)
        portal_text = '\n' + textwrap.fill('Portals (doors) can be added to your room. Do you want to add portal?  [y]es or [n]o',  width=100).strip()
        more_portal = '\n' + textwrap.fill('Do you want to add another Portal?  [y]es or [n]o')
        ans = self.get_valid_response(portal_text) # default is yes/no
        
        # save the current room prototype because calling the buildPortal function will clobber it
        temp_prototype = copy.deepcopy(self.prototype)
        temp_type = copy.copy(self.type)
        self.logger.write_line('prototype & type copied as ' +str(temp_type) + ' & ' + str(temp_prototype))
        
        while True: 
            if ans == 'yes':                                                        
                self.logger.write_line('make portal? input recieved =' +str(ans))                
                self.type = "portal"
                self.prototype = {}
                # build a new portal
                self.logger.write_line('send to buildPortal function')
                self.buildPortal()
                # get the portal's name
                name = self.prototype['name']
                #add to dict for room
                portals[name] = portals.get(name, 0) + 1
                self.logger.write_line('portals dict for room to now looks like ' + str(portals)+ ' Prompt again....')
                #prompt for more
                ans = self.get_valid_response(more_portal)
            else:
                self.logger.write_line('make portal?  input recieved = '+str(ans))
                break
                
        # restore the prototype to the room prototype
        self.prototype = temp_prototype
        self.type = temp_type
        self.logger.write_line('begin exit from buildPortals Function.  Restored temp prototoype and type')
        # add the portals to the room prototype
        self.prototype['portals'] = portals
        self.logger.write_line('portals dict copied to dict prototype[portals]')
        
    def addItems(self):
        """
        Function for adding items to a room or a container item.
        """
        items = {}
        
        #  confirm they want to add item(s)
        item_text = '\n' + textwrap.fill('Items can be added to your ' +self.type+ '.  Enter your choice add a [n]ew item, name an [e]xisting item, or e[x]it.',  width=100).strip()
        valid_responses = (("new", "n"), ("existing", "e"), ("exit", "x"))
        
        ans = self.get_valid_response(item_text, validResponses=valid_responses)
        
        #ensure type to Item for proper dynamic printing
        temp_type = copy.copy(self.type)
        self.type = "item"
        
        while ans != 'exit':
            # add an existing item by name
            if ans == "existing":
                # ask them item name
                check_name = self.checkName() # check name returns Tuple (name, bool (T/F))
                name = check_name[0]
                flag = check_name[1]
                if flag == True: #name was accepted
                    #append name to item dict
                    items[name] = items.get(name, 0) + 1
                    accept = '\n' + textwrap.fill('The '+name+ ' has been added to your '+temp_type+'.', width=100).strip()        
                    self.send_message_to_player(accept)
                    ans = 'exit'
                else:
                    deny = '\n' +textwrap.fill('We cannot find the '+name+', try again.', width=100).strip()
                    self.send_message_to_player(deny)
                    
            # build an item
            else:                
                # save the current prototype because calling the buildItem function will clobber it
                temp_prototype = copy.deepcopy(self.prototype)
                # initialize the prototype for the buildItem function
                self.prototype = {}
                # build a new item
                self.buildItem()
                # capture the item's name
                name = self.prototype["name"]
                # add that item to the list of items
                items[name] = items.get(name, 0) + 1
                item_text2 = '\n' +textwrap.fill('Your ' + self.type + ' has been added to ' +temp_type+ ' list. Now what do you want to do?', width= 100).strip()
                self.send_message_to_player(item_text2)
                # restore original prototype
                self.prototype = temp_prototype
                ans = 'exit'                    
            
            # prompt the user again            
            ans = self.get_valid_response(item_text, validResponses=valid_responses)
       
        self.type = temp_type
        # add the items to the prototype
        self.prototype['items'] = items
        
    def reviewObject(self):
        """
        function to display the object created and allow for the player to make edits.
        """
        self.send_message_to_player('Here is a look at the characteristics of your '+self.type+'.')
        self.printObject()
        #I want to add editing capabilities here later hence the review object and print object functions
    
    def printObject(self):
        """
        Displays object in printable format.
        """
        text = ""
        for key in self.prototype:
            text += key + '=   ' + str(self.prototype[key]) + "\n"
            
        self.send_message_to_player(text)
        
    def makeRoom(self):
        """
        parses the current protoype dict and instantiates a room
        """
        self.logger.write_line('arrive makeRoom function')
        self.send_message_to_player('Your '+self.type+' is being built.')
        
        desc = self.prototype['description']
        portals = self.prototype['portals']
        items = self.prototype['items']
        players = [] # updated only by engine
        npcs = []   # when NPC builder complete we need to have this list populated by builder.
        self.logger.write_line('dict parsed to variables')
        
        room = engine.Room(desc, portals, items, players, npcs)
        self.logger.write_line(str(self.type) + ' instantiated @ ' +str(room)+ 'as ' + str(self.prototype))
        self.send_message_to_player("Your "+self.type+" has been built.")
        
        #add room to list of rooms
        engine._Rooms[self.room_coords] = room
        
        # send messsage to game_cmd_queue signaling done with builder.
        self.game_cmd_queue.put((self.player_name, 'done_building', []))
        
    
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
        self.logger.write_line('prototype dict parsed')
        
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
    
    def makeItem(self):
        """
        parses current prototype Dict and Instantiates an item.
        """
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
        
        self.logger.write_line(str(self.type)+' Sent to instatiante as ' + str(self.prototype)) 
        item = engine.Item(name, desc, i_desc, scripts = scripts, portable = portable, hidden = hidden, container = container, locked = locked, key = key, items = items)
        self.logger.write_line(str(self.type)+ ' instantiated @ ' + str(item))
        #write item to objects list
        engine._Objects_Lock.acquire()
        self.logger.write_line('Objects lock acquired')
        engine._Objects[name] = item
        self.logger.write_line('Objects Dict updated')
        engine._Objects_Lock.release()
        self.logger.write_line('Objects lock released')
        
        self.send_message_to_player('Your '+self.type+ ' has been built.')
                
    def get_valid_response(self, prompt, validResponses=(("yes", "y"), ("no", "n"))):
        """
        ask the player for a valid reponse to a prompt and keep asking until a valid response is received
        """
        # prompt for input
        self.send_message_to_player(prompt)
        
        # build translation dictionary
        translate = {}
        for response in validResponses:
            word = response[0]
            synonym = response[1]
            translate[synonym] = word            
        
        while 1:
            response = self.get_cmd_from_player()
            if response in translate: # if the response is in the list of inputs that can be translated to a valid response
                return translate[response] # translate the response and return the result

            else:
                text = '\n' + textwrap.fill('Invalid response. Please respond with: ' + str(translate.keys()),  width=100).strip()
                self.send_message_to_player(text + prompt)
    
    def get_cmd_from_player(self):
        """
        command from player is sent in 3 part tuple (player_name, message, [tag])
        """
        command = self.cmd_queue.get()
        message = command[1]
        return message

    def send_message_to_player(self, message):
        """
        Packages a message in the (name, msg, tags) format and puts it on the msg_queue
        """
        
        message_tuple = (self.player_name, message, [])
        
        self.msg_queue.put(message_tuple)
