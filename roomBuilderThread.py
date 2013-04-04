import threading
import textwrap
import Queue
import time
import copy
import engine
from msilib.schema import SelfReg

class BuilderThread(threading.Thread):
    """
    Room builder thread
    """

    def __init__(self, type_of_object, cmd_queue, msg_queue, valid_out_queue, room_coords=None, game_state, player_name=""):
        """
        Initialize a Room Builder thread
        """
        threading.Thread.__init__(self)
        self.type = type_of_object # being built
        self.cmd_queue = cmd_queue
        self.msg_queue = msg_queue
        self.validation_in_queue = Queue.Queue()
        self.validation_out_queue = valid_out_queue
        self.room_coords = room_coords
        self.game_state  = game_state
        self.player = player_name
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
        
        while 1:
            pass
            # build the prototype
            # send it to the validator
            # wait for a response
            # if validation failed: get new names
            # else exit the thread
            
    def buildRoom(self):
        
        text = textwrap.fill('In this module you will be building a "room" or "area" to your liking with some limits of course.  '
                        'We will walk you through the process of building and populating the room with things like Portals, '
                        'Containers, Items, and some other stuff.  So lets get started.', width=100).strip()
                        
        self.send_message_to_player(text)
        
        self.addDescription()
        
        self.addPortals()
        
        self.addItems()
        
        self.reviewObject()
        
        self.validate()
        
    def buildPortal(self, direction=""):
        """
        function to build a portal step by step.  Direction has been predetermined from room builder function.
        """
        
        # Name Portal 
        self.addName()

        # Description
        self.addDescription()
        
        # Inspection Description
        self.addInspectionDescription
        
        # Direction
        if direction == "":
            self.getDirection()
        else:
            self.prototype['direction'] = direction
            

        
        
    def buildItem(self):
        """
        
        """
        
    def buildNPC(self):
        """
        
        """
        
        
    def review_room():
        """
        
        """
    def addName(self):
        """
        function for adding a name
        """
        text = '\n' +textwrap.fill ('Enter a name for the ' + self.type , width=100).strip()
        deny = '\n' + textwrap.fill('That name has already been used try agian.',  width=100).strip()
        
        self.send_message_to_player(text)
        name = self.get_cmd_from_player()
                
        while name in game_state._Objects: #  ****CHANGE WHEN GAMESTATE PASSING IS KNOWN
            self.send_message_to_player(deny + text)
            name = self.get_cmd_from_player()
            
        self.prototype['name'] = name
            
        
    # begin room creation
    def addDescription(self):
        """
        function for adding a general description
        """
        text = '\n' +textwrap.fill ('Enter a description for the ' + self.type , width=100).strip()
                                    
        self.send_message_to_player(text)
        
        desc = self.get_cmd_from_player()
        
        self.prototype['description'] = desc
 
    def addInspectionDescription(self):
        """
        Function for adding Inspection Description
        """
        
        text = '\n' +textwrap.fill ('Enter an inspection (more detailed) description for the ' + self.type , width=100).strip()
                                    
        self.send_message_to_player(text)
        
        i_desc = self.get_cmd_from_player()
        
        self.prototype['inspection_description'] = i_desc

        
    
    
    def addPortals(self):
        
        portals = {}
        
        #  confirm they want to create portals
        text = '\n' + textwrap.fill('To add a portal, specify the direction you want ([n]orth, [s]outh, [e]ast, [w]est, [u]p, [d]own, [i]n, or [o]ut). If you are done adding portals e[x]it.',  width=100).strip()
        valid_responses = (("north", "n"), ("south", "s"), ("east", "e"), ("west", "w"), ("in", "i"), ("out", "o"), ("exit", "x"))
        
        self.send_message_to_player(text)
        
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
            portals[ans] = name
            # prompt the user again
            direction = self.get_valid_response(text, validResponses=valid_responses)
        
        # restore the prototype to the room prototype
        self.prototype = temp_prototype
        self.type = temp_type
        # add the portals to the room
        self.prototype['portals'] = portals
        
    def addItems(self):
        """
        
        """
        items = {}
        
        #  confirm they want to add item(s)
        text1 = '\n' + textwrap.fill('Add a [n]ew item, name an [e]xisting item, or e[x]it.',  width=100).strip()
        valid_responses = (("new", "n"), ("existing", "e"), ("exit", "x"), ("west", "w"))
        
        self.send_message_to_player(text1)
        
        # save the current room prototype because calling the buildPortal function will clobber it
        temp_prototype = copy.deepcopy(self.prototype)
        temp_type = copy.copy(self.type)
        self.type = "item"
        ans = self.get_valid_response(text, validResponses=valid_responses)
        while ans not in ("exit", "x"):
            # add an item by name
            if ans == "existing":
                # ask them what item
                text = '\n' + textwrap.fill('Enter the name of the item.',  width=100).strip()
                self.send_message_to_player(text)
                # get response                   
                item_name = self.get_cmd_from_player()
                # check if that item exists
                if item_name not in self.game_state.names:  #  Not sure this is right place to validate
                    text = '\n' + textwrap.fill('That item was not found. Try again',  width=100).strip()
                    self.send_message_to_player(text)
                else:
                    items[name] = items.get(name, 0) + 1
            # build your item
            else:
                # initialize the prototype for the buildItem function
                self.prototype = {}
                # build a new item
                self.buildItem()
                # get the item's name
                name = self.prototype["name"]
                # add that item to the list of items
                items[name] = items.get(name, 0) + 1
            
            # prompt the user again
            self.send_message_to_player(text1)
            ans = self.get_valid_response(text, validResponses=valid_responses)
        
        # restore the prototype
        self.prototype = temp_prototype
        self.type = temp_type
        # add the items to the prototype
        self.prototype['items'] = items
        
    def reviewObject(self):
        """
        
        """
        
    def validate(self):
        """
        
        """
                
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
            for synonym in response:
                translate[synonym] = word
        
        while 1:
            response = self.get_cmd_from_player()
            if response in translate: # if the response is in the list of inputs that can be translated to a valid response
                return translate(response) # translate the response and return the result
            
            else:
                text = '\n' + textwrap.fill('Invalid response. Please respond with: ' + str(translate.keys()),  width=100).strip()
                self.send_message_to_player(text + prompt)
                
    def get_cmd_from_player(self):
        """
        
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
        
    