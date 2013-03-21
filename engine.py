__author__ = 'eking, adillon'

class Room:
    '''
    Attributes:
    - Description
    
    Contains:
    - Portals
    - Containers
    - Items
    '''
    def __init__(self, desc, portals = [], containers = [], items = []):
        self.desc = desc
        
        # Create a dictionary for each list of portals/containers/items
        self.portals = {}
        for portal in portals:
            self.portals[portal.name] = portal
        
        self.containers = {}
        for container in containers:
            self.containers[container.name] = container
        
        self.items = {}
        for item in items:
            self.items[item.name] = item
    
class Portal:
    '''
    Attributes:
    - Name
    - Direction (north, south, east, west, up and down)
    - Description
    - Inspect Description
    - Coordinates (coordinates that the portal lead to (x,y,z))
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Locked (bool)
    - Key
    - Hidden (bool)
    '''
    def __init__(self, name, direction, desc, inspect_desc, coords, scripts = {}, locked = False, hidden = False, key = None):
        self.name = name.lower()
        self.direction = direction
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.coords = coords
        self.scripts = scrub(scripts)
        self.locked = locked
        self.hidden = hidden
        self.key = key

class Container:
    '''
    Attributes:
    - Name
    - Description (for printing in a room)
    - Inspect Description (for looking at the item)
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Locked (bool)
    - Key
    - Hidden (bool)
    
    Contains:
    - Items
    '''
    def __init__(self, name, desc, inspect_desc, scripts = {}, locked = False, key = None, hidden = False, items = []):
        self.name = name.lower()
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.scripts = scrub(scripts)
        self.locked = locked
        self.hidden = hidden
        self.key = key
        
        self.items = {}     # Create a dictionary of items in the container
        for item in items:
            self.items[item.name] = item
    
class Item:
    '''
    Attributes:
    - Name
    - Description (for printing in a room)
    - Inspect Description (for looking at the item)
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Portable (bool)
    - Hidden (bool)
    '''
    def __init__(self, name, desc, inspect_desc, scripts = {}, portable = True, hidden = False):
        self.name = name.lower()
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.portable = portable
        self.hidden = hidden
        self.scripts = scrub(scripts)

class Player:
    '''
    Attributes:
    - Name
    - Coordinates
    - fih = faith in humanity
    - ego = Ego or vanity
    - tolerance
    - balls - aka bravery
    
    Contains:
    - Items
    '''
    def __init__(self, name, coords, items = []):
        self.name = name.lower()
        self.coords = coords
        self.fih = 25
        self.ego = 25
        self.tolerance = 25
        self.balls = 25
        self.items = {}     # Create a dictionary of the items a player contains
        for item in items:
            self.items[item.name] = item
            
def scrub(scripts):
    # Scrubs the verbs in the script to make sure they are valid, no sneaky code injection
    valid_verbs = ['take', 'open', 'go', 'drop', 'unlock', 'print_text', 'reveal']
    
    for script in scripts.keys():
        for action in scripts[script]:
            verb = action[0]
            if verb not in valid_verbs:
                del scripts[script]
                break
    
    return scripts

class NPC:
    '''
    Attributes:
    - Name
    - Affiliation/type
    - Coordinates
    - Targeted
    - Static (bool)
    - File (Twitter scrape generated)
    - Birth - time
    - Lifespan - hours/days
    '''
    def __init__(self, name ):
        self.name = name.lower()
        #self.affiliation = ""
        #self.coords = ""(x, y, z)
        #self.Targeted = ""(bool)
        #self.static = ""(bool)
        #self.file = ""(file extension/handler)
        #self.birth = ""(system time of birth)
        #self.lifespan = ""(int)
        
    
_IDs = {}

# Initialize the game state
_Rooms = {}


portal = Portal('door1', 'north', 'a wooden door', 'an old creaky door', (0,1,1))
apple1 = Item('small apple', 'a small apple', 'blah', scripts={'take': (('take', 'small apple'), ('reveal', 'large apple'), ('unlock', 'chest'), ('print_text', 'You have picked up the small apple, a large sword appears in the room.'))})
sword = Item('large sword', 'a large sword', 'blah', hidden=True)
room = Room('You are in an empty jail cell, there is a cot bolted into the south wall.', portals=[portal], items=[apple1, sword])
_Rooms[(0,0,1)] = room

portal = Portal('door2', 'south', 'an iron door', 'an old creaky door', (0,0,1))
apple2 = Item('large apple', 'a large apple', 'blah', hidden=True)
chest = Container('chest', 'a small chest', 'blah', items=[], locked=True)
room = Room('You are in a guard room, there is a table on the north end of the room.', portals=[portal], items=[apple2], containers=[chest])
_Rooms[(0,1,1)] = room
  
def get_room_text(coords):
    global _Rooms
    
    room = _Rooms[coords]
    text = room.desc
    
    # Add items to the text
    visible_items = get_visible(room.items)
    
    if len(visible_items) > 0:
        text += " There is"

        for n, item in enumerate(visible_items):
            if len(visible_items) == 1:
                text += " %s in the room." % item.desc
            elif n == (len(visible_items) - 1):
                text += " and %s in the room." % item.desc
            else:
                text += " %s," % item.desc
                
    # Add containers to the text
    visible_containers = get_visible(room.containers)
    
    if len(visible_containers) > 0:
        text += " There is"

        for n, container in enumerate(visible_containers):
            if len(visible_containers) == 1:
                text += " %s in the room." % container.desc
            elif n == (len(visible_containers) - 1):
                text += " and %s in the room." % container.desc
            else:
                text += " %s," % container.desc
        
    # Add portals to the text
    visible_portals = get_visible(room.portals)
    
    if len(visible_portals) > 0:
        text += " There is"

        for n, portal in enumerate(visible_portals):
            if len(visible_portals) == 1:
                text += " %s to the %s." % (portal.desc, portal.direction)
            elif n == (len(visible_portals) - 1):
                text += " and %s to the %s." % (portal.desc, portal.direction)
            else:
                text += " %s to the %s," % (portal.desc, portal.direction)
    
    return text

def get_visible(objects):
    visible_objects = []
    
    for object in objects.values():
        if not object.hidden:
            visible_objects.append(object)
    
    return visible_objects

def check_key(player, key):
    for item in player.items.values():
        if item.name == key:
            return True
    
    return False
     
def do_command(command, player):
    global _Rooms
    
    room = _Rooms[player.coords]
    verb, nouns = parse_command(command, room)
    valid_objects = get_valid_objects(player, room, verb)   # Get all of the objects that the player can interact with
    object = get_object(nouns, valid_objects)
    
    noun_string = ' '.join(nouns)
    
    if object != None and verb in object.scripts: # Run a custom script for a verb on the object if it exists
        script = "custom_script(room, player, object.scripts[verb])"
    else:
        script = verb + "(room, player, object, noun_string)"
    
    text = eval(script)
    
    return text
    
def parse_command(command, room):
    # Create translation tables to make the command easier to parse
    translate_one_word = {'i': 'inventory',
                          'l': 'look room',
                          'h': 'help',
                          'q': 'quit',
                          'n': 'go north',
                          's': 'go south',
                          'w': 'go west',
                          'e': 'go east'}
    
    translate_verb = {'look': 'look',
                       'l': 'look',
                       'examine': 'look',
                       'inspect': 'look',
                       'search': 'look',
                       'take': 'take',
                       'grab': 'take',
                       'get': 'take',
                       'open': 'open',
                       'go': 'go',
                       'head': 'go',
                       'enter': 'go',
                       'walk': 'go',
                       'drop': 'drop',
                       'unlock': 'unlock',
                       'inventory': 'inventory',
                       'quit': 'quit'}
    
    translate_noun = {'n': 'north',
                       's': 'south',
                       'w': 'west',
                       'e': 'east',
                       'u': 'up',
                       'd': 'down'}
    
    command = command.lower()
    command = translate_one_word.get(command, command) # This compares command against the 'translate_one_word' dictionary and translates the command
    
    words = command.split()
    
    verb = words[0]
    verb = translate_verb.get(verb, 'bad_command')
    
    nouns = words[1:]
    for n, noun in enumerate(nouns):
        # convert short-hand nouns to their longer name (i.e. 's' => 'south')
        nouns[n] = translate_noun.get(noun, noun)
        
    return verb, nouns
  
'''
Flags  'p' = portals
       'r' = room items
       'i' = player items
       'c' = containers
'''
_ValidLookUp = {'look': ('pric', {'hidden': True}),
                 'take': ('r', {'hidden': True, 'portable': False}),
                 'drop': ('i', {'hidden': True}),
                 'go': ('p', {'hidden': True}),
                 'open': ('c', {'hidden': True}),
                 'unlock': ('pc', {'hidden': True}),
                 'reveal': ('prc', {'hidden': False})}
    
def get_valid_objects(player, room, verb):
    global _ValidLookUp
    
    flags, cull = _ValidLookUp.get(verb, ('',{}))
    valid_objects = []
    
    if 'p' in flags:
        for portal in room.portals:
            valid_objects.append(room.portals[portal])
    
    if 'r' in flags:
        for item in room.items:
            valid_objects.append(room.items[item])
        
    if 'i' in flags:
        for item in player.items:
            valid_objects.append(player.items[item])
    
    if 'c' in flags:
        for container in room.containers:
            valid_objects.append(room.containers[container])
    
    for object in valid_objects:
        for attribute, value in enumerate(cull):
            if isinstance(object, Item):    # Items are the only object that have all attributes
                if attribute == 'portable' and object.portable == value:
                    valid_objects.remove(object)
                    break
            
            if attribute == 'hidden' and object.hidden == value:
                valid_objects.remove(object)
                break
    
    return valid_objects

def get_all_objects(player, verb):
    # Returns all valid objects in the game for a verb
    global _ValidLookUp
    global _Rooms
    
    flags, cull = _ValidLookUp.get(verb, ('',{}))
    valid_objects = []
    
    for room in _Rooms.values():
        if 'r' in flags:
            for item in room.items.values():
                valid_objects.append(item)
        
        if 'p' in flags:
            for portal in room.portals.values():
                valid_objects.append(portal)
        
        if 'c' in flags:
            for container in room.containers.values():
                valid_objects.append(container)
    
    if 'i' in flags:
        for item in player.items.values():
            valid_objects.append(item)
    
    for object in valid_objects:
        for attribute, value in enumerate(cull):
            if isinstance(object, Item):    # Items are the only object that have all attributes
                if attribute == 'portable' and object.portable == value:
                    valid_objects.remove(object)
                    break
            
            if attribute == 'hidden' and object.hidden == value:
                valid_objects.remove(object)
                break
    
    return valid_objects

def get_object(nouns, valid_objects):
    """
    Recognizes short hand for nouns (i.e. if there is a gold key in the room, and the command is "get key", the
    game will recognize that you meant "get gold key" so long as there is only one key in the room.
    
    Returns the object pertaining to the noun.
    """

    # break the nouns into individual words
    noun_bits = []
    for noun in nouns:
        noun = noun.replace('_', ' ')
        noun = noun.replace('-', ' ')
        noun_bits.append(noun)

    # break the list of valid objects into individual words
    object_bits = {}
    for object in valid_objects:
        if isinstance(object, Portal):
            name = object.direction
        else:
            name = object.name
        name = name.replace('_', ' ')
        name = name.replace('-', ' ')
        name = name.split()
        for bit in name:
            if bit in object_bits:
                object_bits[bit].append(object)
            else:
                object_bits[bit] = [object]
    
    # find unique matches between the nouns and the valid items
    for bit in noun_bits:
        if bit in object_bits:
            if len(object_bits[bit]) == 1:
                return object_bits[bit][0]
            
########### ACTIONS #############
def look(room, player, object, noun, script=False):
    if object == None:
        if 'room' in noun or noun == '':
            text = get_room_text(player.coords)
        else:
            text = "There is no %s here." % noun
    else:
        text = object.inspect_desc
            
    return text

def take(room, player, object, noun, script=False):
    if object == None:
        text = "There is no %s to take." % noun
    else:
        # Move object from room to player
        player.items[object.name] = object
        del room.items[object.name]
        text = "You have taken the %s." % object.name
    
    return text

def open(room, player, object, noun, script=False):
    if object == None:
        text = "There is no %s to open." % noun
    elif object.locked and not script:
        text = "You can't open the %s, it is locked." % object.name
    else:
        if len(object.items) > 0:
            text = "You have opened the %s, inside you find:" % object.name
            
            # Open the container and move its contents to the room
            for item in object.items.keys():
                room.items[item] = object.items[item]
                del object.items[item]
                text += "\n\t%s" % item
        else:
            text = "You have opened the %s, but there is nothing inside." % object.name
    
    return text

def go(room, player, object, noun, script=False):
    if object == None:
        text = "You can't go that way."
    elif object.locked and not script:
        text = "That way is locked."
    else:
        # Move player to the coordinates the portal leads to
        player.coords = object.coords
        text = ''
        
    return text

def drop(room, player, object, noun, script=False):
    if object == None:
        text = "You have no %s to drop." % noun
    else:
        # Move item from player to the room
        room.items[object.name] = object
        del player.items[object.name]
        text = "You have taken the %s." % object.name
    
    return text

def unlock(room, player, object, noun, script=False):
    if object == None:
        text = "There is no %s to unlock." % noun
    elif not object.locked:
        text = "The %s is already unlocked." % object.name
    else:
        if check_key(player, object.key) or script:
            object.locked = False
            text = "You have unlocked the %s." % object.name
        else:
            text = "You don't have the key to unlock the %s." % object.name
    
    return text

def inventory(room, player, object, noun, script=False):
    if len(player.items) > 0:
        text = "Inventory:"
        for item in player.items.values():
            text += "\n\t%s" % item.name
    else:
        text = "Your inventory is empty."
        
    return text

def quit(room, player, object, noun, script=False):
    return 'quit'

def bad_command(room, player, object, noun, script=False):
    return "That is not a valid command."

############# CUSTOM SCRIPT METHODS ##########
def custom_script(room, player, script):
    message = ''
    for verb, noun in script:
        nouns = noun.split()
        valid_objects = get_all_objects(player, verb)
        object = get_object(nouns, valid_objects)
        
        script = verb + "(room, player, object, noun, script=True)"
        text = eval(script)
        
        if verb == 'print_text':
            message += text
    
    return message
        
def print_text(room, player, object, noun, script=False):
    return noun

def reveal(room, player, object, noun, script=False):
    # Reveals a hidden object
    object.hidden = False
