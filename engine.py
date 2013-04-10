__author__ = 'eking, adillon'

import loader, engine_helper
import os, random, time
import thread, threading, Queue
import Q2logging

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
        self.scripts = engine_helper.scrub(scripts)
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
    def __init__(self, name, desc, inspect_desc, scripts = {}, portable = True, hidden = False, container = False, locked = False, key = '', items = {}):
        self.name = name.lower()
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.portable = portable
        self.hidden = hidden
        self.container = container
        self.locked = locked
        self.key = key
        self.scripts = engine_helper.scrub(scripts)

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
    - Senses (Sight, Sound, Smell, Seeing Dead People)
    
    Contains:
    - Items
    '''
    def __init__(self, name, coords, prev_coords, affiliation, senses, items = {}, fih = 30):
        self.name = name.lower()
        self.coords = coords
        self.prev_coords = prev_coords
        self.fih = fih
        self.affiliation = affiliation
        self.senses = senses

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
    def __init__(self, name, coords, affiliation, tweets = None):
        self.name = name.lower()
        self.coords = coords
        self.affiliation = affiliation
        self.tweets = []

        twitter_file = open('twitterfeeds/%s.txt' % self.name, 'a')
        twitter_file.close()

logger = Q2logging.out_file_instance('logs/engine/RenEngine')

_StillAlive = True
_CommandQueue = Queue.Queue() # Commands that are waiting to be run
_MessageQueue = Queue.Queue() # Messages that are waiting to be sent to the server

_BuilderQueues = {} # Dictionary of builder queues, 'player name' => Queue

_Rooms = {} # Rooms currently in the game

_Characters = {} # All NPCs and Players currently in the game
_Characters_Lock = threading.RLock()

_Characters_In_Builder = {} # All Players that are currently in a builder thread
_Characters_In_Builder_Lock = threading.RLock()

_Objects = {} # All Objects currently in the game
_Objects_Lock = threading.RLock()

_NPCBucket = [] # List of NPCs to pull from when spawning a new NPC

def init_game(save_state = 0):
    # Initializes the map and starts the command thread
    global _Rooms
    global _Objects

    if save_state > 0:
        directory = 'SaveState%d' % save_state

        print 'Initializing game state from save state %d' % save_state
        logger.write_line('Initializing game state from save state %d' % save_state)
    else:
        directory = 'rooms'

        print 'Initializing game state from default save state'
        logger.write_line('Initializing game state from default save state')

    _Objects_Lock.acquire()
    _Objects = loader.load_objects('objects/objects.xml') # Load the global objects
    _Objects_Lock.release()

    logger.write_line("Loaded global objects")

    for filename in os.listdir(directory):
        path = directory + '/' + filename
        split_name = filename.split('_')
        coords = (int(split_name[0]), int(split_name[1]), int(split_name[2]), int(split_name[3].replace('.xml', '')))

        _Rooms[coords] = loader.load_room(path)
        logger.write_line("Loaded room at (%d,%d,%d,%d) from '%s'"%(coords[0], coords[1], coords[2], coords[3], path))

    # Add some NPCs to the bucket
    affiliation = {'Obama': 1, 'Gottfried': 2, 'OReilly': 3, 'Kanye': 4, 'Burbiglia': 5}
    kanye = NPC('@mr_kanyewest', (0,2,1,0), affiliation)
    _NPCBucket.append(kanye)

    thread.start_new_thread(command_thread, ())
    logger.write_line("Starting command thread")

    thread.start_new_thread(spawn_npc_thread, (10,))
    logger.write_line("Starting spawn NPC thread")

    thread.start_new_thread(npc_thread, ())
    logger.write_line("Starting NPC action thread")

def shutdown_game():
    # Winds the game down and creates a directory with all of the saved state information
    global _StillAlive
    global _Characters
    global _Objects
    global _Rooms

    logger.write_line('Shutting down the game.')

    _StillAlive = False # Causes all of the threads to close

    for player in _Characters.values(): # Save all of the player states
        if isinstance(player, Player):
            loader.save_player(player)
    logger.write_line('Saved player states.')

    save_num = 1
    while 1:    # Create a directory to save the game state in
        directory = 'SaveState%d' % save_num
        if not os.path.exists(directory):
            os.makedirs(directory)

            objects = []
            for object in _Objects.values():
                objects.append(object)
            loader.save_objects(objects, directory) # Save all objects in the game

            for coords in _Rooms: # Save the rooms to the save state directory
                path = directory + 'rooms/%d_%d_%d_%d.xml' % coords
                loader.save_room(_Rooms[coords], path)

            logger.write_line("Saved game state to '%s'" % directory)
            break
        else:
            save_num += 1

def make_player(name, coords = (0,0,1,0), affiliation = {'Obama': 5, 'Kanye': 4, 'OReilly': 3, 'Gottfried': 2, 'Burbiglia': 1}):
    global _Rooms
    global _Characters

    path = 'players/%s.xml' % name
    if os.path.exists(path):    # Load the player if a save file exists for them, otherwise create a new player
        player = loader.load_player(path)
    else:
        senses = {'sight': True,
                  'sound': True,
                  'smell': True,
                  'see_dead_people': False}
        player = Player(name, coords, coords, affiliation, senses)

    _Characters_Lock.acquire()
    _Characters[player.name] = player # Add to list of players in the game
    _Characters_Lock.release()

    _Rooms[player.coords].players.append(player.name) # Add player to list of players in the room they are in

    logger.write_line("Created player '%s' at (%d,%d,%d,%d)" % (player.name, player.coords[0], player.coords[1], player.coords[2], player.coords[3]))

def remove_player(name):
    global _Rooms
    global _Characters

    _Characters_Lock.acquire()
    player = _Characters[name]
    loader.save_player(player)  # Save the player

    _Rooms[player.coords].players.remove(player.name) # Remove the player from the room they are in
    del _Characters[name] # Remove the player from the list of players in the game
    _Characters_Lock.release()

    logger.write_line("Removed player '%s'" % player.name)

def put_commands(commands):
    # Takes a list of commands and pushes them to the command queue
    global _CommandQueue

    for command in commands:
        if len(command) < 3: # Add tags if the command is missing them, THIS WILL NEED REPLACING
            command = (command[0], command[1], [])

        _CommandQueue.put(command)
        logger.write_line("Put command (%s, %s) in the command queue" % (command[0], command[1]))

def get_messages():
    # Returns all messages currently in the message queue
    global _MessageQueue

    messages = []
    while not _MessageQueue.empty():
        message = _MessageQueue.get()

        messages.append(message)

        logger.write_line("Sending message to server: (%s, %s)" % (message[0], message[1]))

    return messages

def command_thread():
    # Runs commands from the command queue
    global _StillAlive
    global _CommandQueue
    global _MessageQueue
    global _Characters
    global _BuilderQueues

    while _StillAlive:
        if not _CommandQueue.empty():
            command = _CommandQueue.get()
            player_name = command[0]
            command_str = command[1]
            tags = command[2]

            if player_name in _Characters:
                messages = engine_helper.do_command(player_name, command_str, tags)

                logger.write_line("Running command (%s, %s)" % (player_name, command))

                for message in messages:
                    _MessageQueue.put(message)
            elif player_name in _BuilderQueues:
                if command_str == 'done_building':
                    _Characters_In_Builder_Lock.acquire()
                    _Characters[player_name] = _Characters_In_Builder[player_name]  # Move player from Builder back to _Characters
                    player = _Characters[player_name]
                    _Characters_In_Builder_Lock.release()

                    _Rooms[player.coords].players.append(player.name) # Add the player to the room

                    _MessageQueue.put((player.name, engine_helper.get_room_text(player.name, player.coords)))   # Put room description in the message queue

                    logger.write_line("Player (" + player.name + ") is done building, moved back to game at coordinates (%d,%d,%d,%d)." % player.coords)
                else:
                    _BuilderQueues[player_name].put(command)
    
                    logger.write_line("Forwarded command to builder queue (%s, %s)" % (player_name, command))

        time.sleep(.05) # Sleep for 50ms

    logger.write_line("Closing command thread.")

def npc_thread():
    # Runs the commands for all NPC's in the game
    global _StillAlive
    global _Characters

    if _StillAlive:
        threading.Timer(5.0, npc_thread).start()

        npcs = {}
        _Characters_Lock.acquire()
        for character in _Characters:
            if isinstance(_Characters[character], NPC):
                npcs[character] = _Characters[character]
        _Characters_Lock.release()

        for npc in npcs.values():
            engine_helper.npc_action(npc)
    else:
        logger.write_line("Closing npc action thread.")

def spawn_npc_thread(n):
    # Spawns a new NPC for every 'n' rooms in the game
    global _StillAlive
    global _Characters
    global _NPCBucket

    while _StillAlive:
        npcs = {}
        _Characters_Lock.acquire()
        for character in _Characters:
            if isinstance(_Characters[character], NPC):
                npcs[character] = _Characters[character]

        if ((len(_Rooms) / n) + 1) > len(npcs):
            npc = random.choice(_NPCBucket)

            # Get the NPCs tweets
            twitter_file = open('twitterfeeds/%s.txt' % npc.name)
            for line in twitter_file.readlines():
                npc.tweets.append(line.strip())
            twitter_file.close()

            if len(npc.tweets) > 0:
                _Characters[npc.name] = npc
                _Rooms[npc.coords].npcs.append(npc.name) # Add the NPC to the room he spawned in

                logger.write_line("Spawned NPC: (%s) %s" %(npc.name, npc))


        elif ((len(_Rooms) / n) + 1) < len(npcs):
            name = random.choice(npcs.keys())
            npc = npcs[name]
            del _Characters[name] # Remove from the NPC list
            del _Rooms[npc.coords].npcs[npc.name] # Remove the NPC from the room
            logger.write_line("Removed NPC: (%s) %s" % (npc.name, npc))

        _Characters_Lock.release()
        time.sleep(.05) # Sleep for 50ms

    logger.write_line("Closing spawn npc thread.")
