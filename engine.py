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
    
    Contains:
    - Items
    '''
    def __init__(self, name, coords, prev_coords, affiliation, items = {}, fih = 30):
        self.name = name.lower()
        self.coords = coords
        self.prev_coords = prev_coords
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
    def __init__(self, name, coords, affiliation, tweets = None):
        self.name = name.lower()
        self.coords = coords
        self.affiliation = affiliation
        self.tweets = []

        twitter_file = open('twitterfeeds/%s.txt' % self.name, 'a')
        twitter_file.close()

logger = Q2logging.out_file_instance('logs/engine/RenEngine') ###TEST

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
        #logger.debug('Initializing game state from save state %d' % save_state)
        logger.write_line('Initializing game state from save state %d' % save_state) ###TEST
    else:
        directory = 'rooms'

        print 'Initializing game state from default save state'
        #logger.debug('Initializing game state from default save state')
        logger.write_line('Initializing game state from default save state') ###TEST

    _Objects_Lock.acquire()
    _Objects = loader.load_objects('objects/objects.xml') # Load the global objects
    _Objects_Lock.release()

    #logger.debug("Loaded global objects")
    logger.write_line("Loaded global objects") ###TEST

    for filename in os.listdir(directory):
        path = directory + '/' + filename
        split_name = filename.split('_')
        coords = (int(split_name[0]), int(split_name[1]), int(split_name[2].replace('.xml', '')))

        _Rooms[coords] = loader.load_room(path)
        logger.write_line("Loaded room at (%d,%d,%d) from '%s'"%(coords[0], coords[1], coords[2], path))

    # Add some NPCs to the bucket
    affiliation = {'Obama': 1, 'Gottfried': 2, 'OReilly': 3, 'Kanye': 4, 'Burbiglia': 5}
    kanye = NPC('@mr_kanyewest', (0,2,1), affiliation)
    _NPCBucket.append(kanye)

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
        player = Player(name, coords, coords, affiliation)

    _Characters_Lock.acquire()
    _Characters[player.name] = player # Add to list of players in the game
    _Characters_Lock.release()

    _Rooms[player.coords].players.append(player.name) # Add player to list of players in the room they are in

    #logger.debug("Created player '%s' at (%d,%d,%d)" % (player.name, player.coords[0], player.coords[1], player.coords[2]))
    logger.write_line("Created player '%s' at (%d,%d,%d)" % (player.name, player.coords[0], player.coords[1], player.coords[2])) ###TEST

def remove_player(name):
    global _Rooms
    global _Characters

    _Characters_Lock.acquire()
    player = _Characters[name]
    loader.save_player(player)  # Save the player

    _Rooms[player.coords].players.remove(player.name) # Remove the player from the room they are in
    del _Characters[name] # Remove the player from the list of players in the game
    _Characters_Lock.release()

    #logger.debug("Removed player '%s'" % player.name)
    logger.write_line("Removed player '%s'"%player.name) ###TEST

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

        #final_msg = (message[0], sense_filter(message[1]) #Pass in the message, filter, get it back, make a new tuple. From here on use final_msg instead of message?
        messages.append(message)
        #messages.append(final_msg)

        logger.write_line("Sending message to server: (%s, %s)" % (message[0], message[1])) ###TEST
        #logger.write_line("Sending message to server: (%s, %s)" % (final_msg[0], final_msg[1])) 

    return messages

def sense_filter(message): ######In Progress. Presently requires players to have .sight, .sound and .smell attributes, as well as messages having tags <smell></smell> and <sound></sound>
        temp = message.split()
        resp = ''
        threshold = 50
        size = len(temp)
        
        
        if "<sound>" in message:
            start = temp.index("<sound>")
            state_sense = player.sound
            end = temp.index("</sound>")
            if state_sense == False: #This one is impaired
                for i in range(start+1, end-1):
                    test = random.randint(0, 99)
                    if test <= threshold:
                        temp[i] = '...' #Does all filtering only between sound tags.
        if "<smell>" in message:
            start = temp.index("<smell>")
            state_sense = player.smell
            end = temp.index("</smell>")
            if state_sense == False: #This one is impaired
                for i in range(start+1, end-1):
                    test = random.randint(0, 99)
                    if test <= threshold:
                        temp[i] = '...' #Filter only between smell tags
                        
        state_sense = player.sight
        if state_sense == False: #Impaired vision
            size = len(temp)
            if temp[0] != "<smell>" and temp[0] != "<sound>" and temp[size-1] != "</smell>" and temp[size-1] != "</sound>": #This message does not start or end with a tag.
                start = 0
                if "<smell>" in temp and "<sound>" not in temp:
                    end1 = temp.index("<smell>") #Get the position
                    for i in range(start, end1-1):
                        test = random.randint(0, 99)
                        if test <= threshold:
                            temp[i] = '...' #Do the replacements up until the <smell> tag
                    start = temp.index("</smell>")+1 #Start at one after the </smell> tag
                    end = len(temp)
                    for i in range(start, end-1):
                        test = random.randint(0, 99)
                        if test <= threshold:
                            temp[i] = '...' #Do the replacements following the </smell> tag
                            
                elif "<sound>" in temp and "<smell>" not in temp:
                    end1 = temp.index("<sound>") #Get the position
                    for i in range(start, end1-1):
                        test = random.randint(0, 99)
                        if test <= threshold:
                            temp[i] = '...' #Do the replacements up until the <sound> tag
                    start = temp.index("</sound>")+1 #Start after the </sound> tag
                    end = len(temp)
                    for i in range(start, end-1):
                        test = random.randint(0, 99)
                        if test <= threshold:
                            temp[i] = '...' #Replace following the </sound> tag
                            
                elif "<smell>" in temp and "<sound>" in temp: #This one has both alt-tags, we have to prioritize them.
                    tmp1 = temp.index("<smell>")
                    tmp2 = temp.index("<sound>")
                    if tmp1 < tmp2: #The smell tag comes first.
                        end1 = temp.index("<smell>") #Get our first endpoint.
                        for i in range(start, end1-1):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                        start = temp.index("</smell>")+1 #Get our second start point
                        end = temp.index("<sound>")-1 #Get our second endpoint
                        for i in range(start, end):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                        start = temp.index("</sound>")+1
                        end = len(temp) 
                        for i in range(start, end):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                                
                    else: #Sound tag comes first
                        end1 = temp.index("<sound>") #get first endpoint
                        for i in range(start, end1-1):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                        start = temp.index("</sound>")+1 #Get our second start point
                        end = temp.index("<smell>")-1 #Get our seond endpoint.
                        for i in range(start, end):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                        start = temp.index("</smell>")+1
                        end = len(temp)
                        for i in range(start, end):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                        
                
                for i in range(0, len(temp)): 
                        resp += temp[i]+' ' #string them all together. #resp is now the full, filtered response.
                        
            else: #This message starts or ends with a tag:
                if temp[0] == '<smell>' or temp[0] == '<sound>': #Starts with a tag
                    if '<smell>' in temp and not '<sound>' in temp: #Starts with the smell tag
                        start = temp.index('</smell>')+1
                        end = len(temp)
                        for i in range(start, end):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                                
                    elif '<sound>' in temp and not '<smell>' in temp: #Starts with sound tag
                        start = temp.index('</sound>')+1
                        end = len(temp)
                        for i in range(start, end):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                                
                    else: #Both <sound> and <smell> in temp, and one starts it
                        tmp1 = temp.index('<sound>')
                        tmp2 = temp.index('<smell>')
                        if tmp1 < tmp2: #<sound> comes first:
                            start = temp.index("</sound>")+1
                            end = temp.index("<smell>")
                            for i in range(start, end): #Filter out the text between the sound and smell tags
                                test = random.randint(0, 99)
                                if test <= threshold:
                                    temp[i] = '...'
                            start = temp.index("</smell>")+1
                            end = len(temp)
                            for i in range(start, end): #Filter out text after smell close tag.
                                test = random.randint(0, 99)
                                if test <= threshold:
                                    temp[i] = '...'
                                    
                        else: #temp2 < temp1, <smell> comes first
                            start = temp.index("</smell>")+1
                            end = temp.index("<sound>")
                            for i in range(start, end):
                                test = random.randint(0, 99)
                                if test <= threshold:
                                    temp[i] = '...'
                            start = temp.index("</sound>")+1
                            end = len(temp)
                            for i in range(start, end):
                                test = random.randint(0, 99)
                                if test <= threshold:
                                    temp[i] = '...'
                            
                elif temp[size-1] == '</smell>' or temp[size-1] == '</sound>': #The message ends in either a smell or sound tag
                    if '<smell>' in temp and not '<sound>' in temp: #Ends with smell tag, no sound tag present.
                        end = temp.index('<smell>')
                        for i in range(start, end): 
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                    elif '<sound>' in temp and not '<smell>' in temp: #Ends with sounds tag, smell tag present.
                        end = temp.index("<sound>")
                        for i in range(start, end):
                            test = random.randint(0, 99)
                            if test <= threshold:
                                temp[i] = '...'
                    elif '<sound>' in temp and '<smell>' in temp: #Ends with one, but we don't know the ordering.
                        tmp1 = temp.index("<sound>")
                        tmp2 = temp.index("<smell>")
                        if tmp1 < tmp2: #Sound comes before smell #Make changes up until <sound> tag
                            end = temp.index("<sound>")
                            for i in range(start, end):
                                test = random.randint(0, 99)
                                if test <= threshold:
                                    temp[i] = '...'
                            start = temp.index("</sound>")+1
                            end = temp.index("<smell>")
                            for i in range(start, end): 
                                test = random.randint(0, 99)
                                if test <= threshold:
                                    temp[i] = '...'
                        else: #sound comes after smell
                            end = temp.index("<smell>")
                            for i in range(start, end):
                                test = random.randint(0, 99)
                                if test <= threshold:
                                    temp[i] = '...'
                            start = temp.index("</smell>")+1
                            end = temp.index("<sound>")
                            for i in range(start, end): 
                                test = random.randint(0, 99)
                                if test <= threshold:
                                    temp[i] = '...'
                                    
                for i in range(0, len(temp)):
                    resp += temp[i]+' ' 
                
                
        resp = resp.replace("<sound>", '')
        resp = resp.replace("</sound>", '')
        resp = resp.replace("<smell>", '')
        resp = resp.replace("</smell>", '')
        
        return resp
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

    #logger.debug("Closing npc action thread.")
    logger.write_line("Closing npc action thread.") ###TEST

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
