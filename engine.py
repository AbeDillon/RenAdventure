__author__ = 'eking, adillon'

import loader
from engine_helper import *
import os, random, time
import thread, threading, Queue
#import logging
import Q2logging ###TEST


class Room:
    '''
    Attributes:
    - Description
    
    Contains:
    - Portals
    - Items
    - Players
    - NPCs
    '''
    def __init__(self, desc, portals, items, players, npcs):
        self.desc = desc
        self.players = players
        self.npcs = npcs

        self.portals = {}
        for portal in portals:
            if portal in self.portals:
                self.portals[portal] += 1
            else:
                self.portals[portal] = 1

        self.items = {}
        for item in items:
            if item in self.items:
                self.items[item] += 1
            else:
                self.items[item] = 1
    
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
    def __init__(self, name, direction, desc, inspect_desc, coords, scripts = {}, locked = False, hidden = False, key = ''):
        self.name = name.lower()
        self.direction = direction
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.coords = coords
        self.scripts = scrub(scripts)
        self.locked = locked
        self.hidden = hidden
        self.key = key
    
class Item:
    '''
    Attributes:
    - Name
    - Description (for printing in a room)
    - Inspect Description (for looking at the item)
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Portable (bool)
    - Hidden (bool)

    - Container (bool)
    - Locked (bool)
    - Key
    - Items
    '''
    def __init__(self, name, desc, inspect_desc, scripts = {}, portable = True, hidden = False, container = False, locked = False, key = '', items = []):
        self.name = name.lower()
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.portable = portable
        self.hidden = hidden
        self.container = container
        self.locked = locked
        self.key = key
        self.scripts = scrub(scripts)

        self.items = {}
        for item in items:
            if item in self.items:
                self.items[item] += 1
            else:
                self.items[item] = 1

class Player:
    '''
    Attributes:
    - Name
    - Coordinates
    - Faith in Humanity
    - Affiliation (dictionary of opinion of each person)
    
    Contains:
    - Items
    '''
    def __init__(self, name, coords, affiliation, items = [], fih = 30):
        self.name = name.lower()
        self.coords = coords
        self.fih = fih
        self.affiliation = affiliation

        self.items = {}
        for item in items:
            if item in self.items:
                self.items[item] += 1
            else:
                self.items[item] = 1

class NPC:
    '''
    Attributes:
    - Name
    - Coordinates
    - Affiliation (dictionary of opinion of each person)
    '''
    def __init__(self, name, coords, affiliation):
        self.name = name.lower()
        self.coords = coords
        self.affiliation = affiliation

#logger = logging.getLogger(__name__.title())
logger = Q2logging.out_file_instance('logs/engine/RenEngine') ###TEST
_StillAlive = True
_CommandQueue = Queue.Queue() # Commands that are waiting to be run
_MessageQueue = Queue.Queue() # Messages that are waiting to be sent to the server
_Characters = {} # All NPCs and Players currently in the game
_Rooms = {} # Rooms currently in the game
_Objects = {} # All Objects currently in the game
_NPCBucket = [] # List of NPCs to pull from when spawning a new NPC

def init_game(save_state = 0):
    # Initializes the map and starts the command thread
    global _Rooms
    global _Objects

    if save_state > 0:
        directory = 'SaveState%d' % save_state

        print 'Initializing game state from save state %d' % save_state
        #logger.debug('Initializing game state from save state %d' % save_state)
        logger.write_line('Initializing game state from save state %d' % save_state) ###TEST
    else:
        directory = 'rooms'

        print 'Initializing game state from default save state'
        #logger.debug('Initializing game state from default save state')
        logger.write_line('Initializing game state from default save state') ###TEST

    _Objects = loader.load_objects('objects/objects.xml') # Load the global objects
    #logger.debug("Loaded global objects")
    logger.write_line("Loaded global objects") ###TEST

    for filename in os.listdir(directory):
        path = directory + '/' + filename
        split_name = filename.split('_')
        coords = (int(split_name[0]), int(split_name[1]), int(split_name[2].replace('.xml', '')))

        _Rooms[coords] = loader.load_room(path)
        #logger.debug("Loaded room at (%d,%d,%d) from '%s'" % (coords[0], coords[1], coords[2], path))
        logger.write_line("Loaded room at (%d,%d,%d) from '%s'"%(coords[0], coords[1], coords[2], path)) ###TEST

    # Add some NPCs to the bucket
    affiliation = {'Obama': 1, 'Gottfried': 2, 'OReilly': 3, 'Kanye': 4, 'Burbiglia': 5}
    kanye = NPC('kanye', (0,2,1), affiliation)
    _NPCBucket.append(kanye)

    affiliation = {'Obama': 3, 'Gottfried': 2, 'OReilly': 4, 'Kanye': 1, 'Burbiglia': 5}
    gates = NPC('bill gates', (0,2,1), affiliation)
    _NPCBucket.append(gates)

    affiliation = {'Obama': 2, 'Gottfried': 4, 'OReilly': 1, 'Kanye': 5, 'Burbiglia': 3}
    oreilly = NPC('bill oreilly', (0,2,1), affiliation)
    _NPCBucket.append(oreilly)

    thread.start_new_thread(command_thread, ())
    #logger.debug("Starting command thread")
    logger.write_line("Starting command thread") ###TEST

    thread.start_new_thread(spawn_npc_thread, (10,))
    #logger.debug("Starting spawn NPC thread")
    logger.write_line("Starting spawn NPC thread") ###TEST

    thread.start_new_thread(npc_thread, ())
    #logger.debug("Starting NPC action thread")
    logger.write_line("Starting NPC action thread") ###TEST

def shutdown_game():
    # Winds the game down and creates a directory with all of the saved state information
    global _StillAlive
    global _Players
    global _Rooms

    #logger.debug('Shutting down the game.')
    logger.write_line('Shutting down the game.') ###TEST

    _StillAlive = False # Causes all of the threads to close

    for player in _Players.values(): # Save all of the player states
        loader.save_player(player)
    #logger.debug('Saved player states.')
    logger.write_line('Saved player states.') ###TEST

    save_num = 1
    while 1:    # Create a directory to save the game state in
        directory = 'SaveState%d' % save_num
        if not os.path.exists(directory):
            os.makedirs(directory)

            for coords in _Rooms: # Save the rooms to the save state directory
                path = directory + '/%d_%d_%d.xml' % coords
                loader.save_room(_Rooms[coords], path)

            #logger.debug("Saved game state to '%s'" % directory)
            logger.write_line("Saved game state to '%s'"%directory) ###TEST
            break
        else:
            save_num += 1

def make_player(name, coords = (0,0,1), affiliation = {'Obama': 5, 'Kanye': 4, 'OReilly': 3, 'Gottfried': 2, 'Burbiglia': 1}):
    global _Rooms
    global _Characters

    path = 'players/%s.xml' % name
    if os.path.exists(path):    # Load the player if a save file exists for them, otherwise create a new player
        player = loader.load_player(path)
    else:
        player = Player(name, coords, affiliation)

    _Characters[player.name] = player # Add to list of players in the game
    _Rooms[player.coords].players.append(player.name) # Add player to list of players in the room they are in

    #logger.debug("Created player '%s' at (%d,%d,%d)" % (player.name, player.coords[0], player.coords[1], player.coords[2]))
    logger.write_line("Created player '%s' at (%d,%d,%d)" % (player.name, player.coords[0], player.coords[1], player.coords[2])) ###TEST

def remove_player(name):
    global _Rooms
    global _Characters

    player = _Characters[name]
    loader.save_player(player)  # Save the player

    _Rooms[player.coords].players.remove(player.name) # Remove the player from the room they are in
    del _Characters[name] # Remove the player from the list of players in the game

    #logger.debug("Removed player '%s'" % player.name)
    logger.write_line("Removed player '%s'"%player.name) ###TEST

def put_commands(commands, script=False, npc=False):
    # Takes a list of commands and pushes them to the command queue (player, room, verb, object, tags)
    global _CommandQueue
    global _Characters
    global _Rooms

    for command in commands:
        tags = []
        player = _Characters[command[0]]

        room = _Rooms[player.coords]
        verb, nouns = parse_command(command[1])

        if not npc and verb == 'damage': # Only NPCs can use the command damage (for now)
            verb = 'bad_command'

        if not script:
            valid_objects = get_valid_objects(player, room, verb) # Find the valid objects in the room that can be acted on by the verb
        else: # Find all valid objects in the game for the verb
            all_objects = get_all_objects(player, verb) # tuple of all objects and the room they are in

            valid_objects = []
            for object_room, object in all_objects:
                valid_objects.append(object)

        object = get_object(nouns, valid_objects) # Get the object that the player is trying to act on

        if script: # We need to find which room the object is in
            for room, new_object in all_objects:
                if object is new_object:
                    break

        if object != None and verb in object.scripts and not script: # Object has a script to override the verb
            tags.append('start_script')

        if script:
            tags.append('script')
        if npc:
            tags.append('npc')

        command = [player, room, verb, nouns, object, tags]
        _CommandQueue.put(command)

        #logger.debug("Put command (%s, %s, %s, %s, %s, %s) in the command queue" % tuple(command))
        logger.write_line("Put command (%s, %s, %s, %s, %s, %s) in the command queue" % tuple(command)) ###TEST

def get_messages():
    # Returns all messages currently in the message queue
    global _MessageQueue

    messages = []
    while not _MessageQueue.empty():
        message = _MessageQueue.get()
        messages.append(message)

        #logger.debug("Sending message to server: (%s, %s)" % message)
        logger.write_line("Sending message to server: (%s, %s)"%message) ###TEST

    return messages

def command_thread():
    # Runs commands from the command queue
    global _StillAlive
    global _CommandQueue
    global _MessageQueue

    while _StillAlive:
        if not _CommandQueue.empty():
            command = _CommandQueue.get()
            player = command[0]
            room = command[1]
            verb = command[2]
            nouns = command[3]
            object = command[4]
            tags = command[5]

            messages = do_command(player, room, verb, nouns, object, tags)

            #logger.debug("Running command (%s, %s)" % (verb, ' '.join(nouns)))
            logger.write_line("Running command (%s, %s)" % (verb, ' '.join(nouns))) ###TEST

            for message in messages:
                _MessageQueue.put(message)

        time.sleep(.05) # Sleep for 50ms

    #logger.debug("Closing command thread.")
    logger.write_line("Closing command thread.") ###TEST

def npc_thread():
    # Runs the commands for all NPC's in the game
    global _StillAlive
    global _Characters

    if _StillAlive:
        threading.Timer(5.0, npc_thread).start()

        npcs = {}
        for character in _Characters:
            if isinstance(character, NPC):
                npcs[character] = _Characters[character]

        for npc in npcs.values():
            npc_action(npc)

    #logger.debug("Closing npc action thread.")
    logger.write_line("Closing npc action thread.") ###TEST

def spawn_npc_thread(n):
    # Spawns a new NPC for every 'n' rooms in the game
    global _StillAlive
    global _Characters
    global _NPCBucket

    while _StillAlive:
        npcs = {}
        for character in _Characters:
            if isinstance(character, NPC):
                npcs[character] = _Characters[character]

        if ((len(_Rooms) / n) + 1) > len(npcs):
            npc = random.choice(_NPCBucket)
            _Characters[npc.name] = npc
            _Rooms[npc.coords].npcs.append(npc.name) # Add the NPC to the room he spawned in

            #logger.debug("Spawned NPC: (%s) %s" % (npc.name, npc))
            logger.write_line("Spawned NPC: (%s) %s" %(npc.name, npc)) ###TEST
        elif ((len(_Rooms) / n) + 1) < len(npcs):
            name = random.choice(npcs.keys())
            npc = npcs[name]
            del _Characters[name] # Remove from the NPC list
            del _Rooms[npc.coords].npcs[npc.name] # Remove the NPC from the room

            #logger.debug("Removed NPC: (%s) %s" % (npc.name, npc))
            logger.write_line("Removed NPC: (%s) %s" % (npc.name, npc)) ###TEST

        time.sleep(.05) # Sleep for 50ms

    #logger.debug("Closing spawn npc thread.")
    logger.write_line("Closing spawn npc thread.") ###TEST
