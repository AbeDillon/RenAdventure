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

    def __init__(self, type_of_object, cmd_queue, msg_queue, game_cmd_cue, room_coords=None, player_name=""):
        """
        Initialize a Room Builder thread
        """
        logger = Q2logging.out_file_instance('logs/builder/builder')
        
        threading.Thread.__init__(self)
        self.type = type_of_object # being built
        self.cmd_queue = cmd_queue
        self.msg_queue = msg_queue
        self.game_cmd_cue = game_cmd_cue
        self.room_coords = room_coords
        self.player_name = player_name
        self.prototype = {}
        if self.type == "room":
            self.prototype["name"] = room_coords
        
    def run(self):
        """
        
        """
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
                        
        self.send_message_to_player(text)
        
        self.addDescription()
        
        self.addPortals()
        
        self.addItems()
        
        #add functionality for placing NPCs
        
        self.reviewObject()
        
        self.makeRoom()
        
    def buildPortal(self, direction=""):
        """
        function to build a portal step by step.  Direction has been predetermined from room builder function.
        """
        
        # Name Portal 
        self.addName()
        
        # Description
        self.addDescription()
        
        # Inspection Description
        self.addInspectionDescription()
        
        # Direction
        if direction == "":
            direction = self.getDirection()  # need to have variable set to pass into coords if direction = ""
        else:
            self.prototype['direction'] = direction
            self.send_message_to_player(str(self.prototype))
        # Coords
        self.assignCoords(direction)
        
        # Locked
        self.isLocked()
                
        # Key
        self.addKey()
        
        # Hidden
        self.isHidden()
        
        # Scripts
        self.buildScripts()
        
        self.reviewObject()
        
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
        
    def buildScripts(self):
        """
        Function to build out Action scripts for Items and Portals
        """
        # list of valid verbs (populate when builder is run) from engine
        verbs = []
        scripts = {}
        
        intro_text = '\n' +textwrap.fill('You can [b]uild a script for this '+self.type+', e[x]it scripts, or get [h]elp?  What is your preference?', width=100).strip()
        valid_responses = (('build', 'b'), ('exit', 'x'), ('help', 'h'))
        
        
        #get user
        ans = self.get_valid_response(intro_text, validResponses=valid_responses)
        while ans != 'exit':
            if ans == 'build':
               ans = 'exit'
#               script = {}
#               scripts = script.get(script,0)
#               text = 'Enter the verb you want to override.'
#               verb = self.get_cmd 
            else:
                # User wants help
                self.scriptsHelp()
                ans = self.get_valid_response(intro_text, validResponses=valid_responses)
        
        self.prototype['scripts'] = scripts
        
    def scriptsHelp(self):
        
        help_text = '\n' +textwrap.fill('Scripts are commands that run in place of the command given on this '+self.type+'.   For example if you are '
                                        'making an apple you could make it so that if they say "take apple" you can have it open a portal in the room and/or '
                                        'reveal a chest.  Remember if you do this if you still wanted to have the player take the apple you have to include '
                                        'that in the list of actions.', width=100).strip()
    
        help_text2 = '\n'+textwrap.fill('Here is how it works.  You give us a verb (the first word of a command) that you want to replace with other '
                                        'actions.  Then you give us the action(s) you want to happen along with a whole number that will represent '
                                        'a delay (in seconds) that will occur before that action happens. You can add an unlimited number of actions '
                                        'for each verb replaced.', width=100).strip()
        
        help_text3 = '\n'+textwrap.fill('And finally, a word about how delays work.  Delays will not begin until all the delays before them have completed.  '
                                        'For example -  if you were to replace the verb "take" on the item "apple" take apple 0, go north 3, drop apple 2 '
                                        'would have the player that issued the command take apple to take the apple immediately, wait 3 seconds and move north, '
                                        'wait another 2 seconds and drop the apple.  As you can see this could be rather interesting.  Have fun but try not to '
                                        'ruin things for everyone else while you are at it.',width=100)
        self.send_message_to_player(help_text + help_text2 + help_text3)
    
    def buildNPC(self):
        """
        
        """
        
        
    def review_room():
        """
        
        """
        
    def addName(self):
        """
        function for adding a name
        does not all names that have already been used.
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
        Function for checking name when player wants to add items by name
        Only allows names that do exist
        
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
        """
        pass
    
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
        
        portals = {}
        
        #  confirm they want to create portals
        text = '\n' + textwrap.fill('To add a portal, specify the direction you want ([n]orth, [s]outh, [e]ast, [w]est, [u]p, [d]own, [i]n, or [o]ut). If you are done adding portals e[x]it.',  width=100).strip()
        valid_responses = (("north", "n"), ("south", "s"), ("east", "e"), ("west", "w"), ("in", "i"), ("out", "o"), ("exit", "x"))
        
        # save the current room prototype because calling the buildPortal function will clobber it
        temp_prototype = copy.deepcopy(self.prototype)
        temp_type = copy.copy(self.type)
        self.type = "portal"
        direction = self.get_valid_response(text, validResponses=valid_responses)
        while direction not in ("exit", "x"):
            # initialize the prototype for the buildPortal function
            self.prototype = {}
            # build a new portal
            self.buildPortal(direction)
            # get the portal's name
            name = self.prototype["name"]
            # add that portal's direction : name to the dictionary of portals for the room
            portals[direction] = name
            self.send_message_to_player(str(portals))
            # prompt the user again
            direction = self.get_valid_response(text, validResponses=valid_responses)
                
        # restore the prototype to the room prototype
        self.prototype = temp_prototype
        self.type = temp_type
        # add the portals to the room
        self.prototype['portals'] = portals
        
    def addItems(self):
        """
        Function for adding items to room or a container item.
        """
        items = {}
        
        #  confirm they want to add item(s)
        item_text = '\n' + textwrap.fill('Add a [n]ew item, name an [e]xisting item, or e[x]it.',  width=100).strip()
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
        need to change NPC list when the npc builder is complete.
        """
        self.send_message_to_player('Your '+self.type+' is being built.')
        
        desc = self.prototype['description']
        portals = self.prototype['portals']
        items = self.prototype['items']
        players = []
        npcs = []
        
        room = engine.Room(desc, portals, items, players, npcs)
        
        self.send_message_to_player("Your "+self.type+" has been built.")
    
    def makePortal(self):
        """
        
        """
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
        
        # Build Portal
        portal = engine.Portal(name, dir, desc, i_desc, coords, scripts = scripts, locked = locked, hidden = hidden, key = key)
        
        self.send_message_to_player('Your '+self.type+' has been built.')
        return portal
    
    def makeItem(self):
        """
        
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
         
        item = engine.Item(name, desc, i_desc, scripts = scripts, portable = portable, hidden = hidden, container = container, locked = locked, key = key, items = items)
        
        self.send_message_to_player('Your '+self.type+ ' has been built.')
        
        return item
                
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
