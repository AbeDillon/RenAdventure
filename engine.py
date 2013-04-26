__author__ = 'eking, adillon'

from engine_classes import *
import loader, engine_helper
import os, random, time, math
import thread, threading, Queue
import Q2logging

class Engine:

    def __init__(self, name):
        self.logger = Q2logging.out_file_instance('logs/engine/RenEngine')

        self._StillAlive = True
        self._CommandQueue = Queue.Queue() # Commands that are waiting to be run
        self._MessageQueue = Queue.Queue() # Messages that are waiting to be sent to the server

        self._BuilderQueues = {} # Dictionary of builder queues, 'player name' => Queue

        self._Rooms = {} # Rooms currently in the game

        self._Characters = {} # All NPCs and Players currently in the game
        self._Characters_Lock = threading.RLock()

        self._Characters_In_Builder = {} # All Players that are currently in a builder thread
        self._Characters_In_Builder_Lock = threading.RLock()
        
        self._ShopQueues = {} # All players currently in the shop.
        
        self._Characters_In_Shop = {} #Players that are currently in a shop
        self._Characters_In_Shop_Lock = threading.RLock()

        self._Objects = {} # All Objects currently in the game
        self._Objects_Lock = threading.RLock()

        self._NPC_Bucket = {} # List of NPCs
        self._NPC_Bucket_Lock = threading.RLock()

        self._NPC_Queue = Queue.Queue()  # Queue of NPCs to be added to the game

    def init_game(self, save_state = 0):
        # Initializes the map and starts the command thread

        if save_state > 0:
            directory = 'SaveState%d' % save_state

            print 'Initializing game state from save state %d' % save_state
            self.logger.write_line('Initializing game state from save state %d' % save_state)
        else:
            directory = 'rooms'

            print 'Initializing game state from default save state'
            self.logger.write_line('Initializing game state from default save state')

        self._Objects_Lock.acquire()
        self._Objects = loader.load_objects('objects/objects.xml') # Load the global objects
        self._Objects_Lock.release()

        self.logger.write_line("Loaded global objects")

        for filename in os.listdir(directory):
            path = directory + '/' + filename
            split_name = filename.split('_')
            coords = (int(split_name[0]), int(split_name[1]), int(split_name[2]), int(split_name[3].replace('.xml', '')))

            self._Rooms[coords] = loader.load_room(path)
            self.logger.write_line("Loaded room at (%d,%d,%d,%d) from '%s'"%(coords[0], coords[1], coords[2], coords[3], path))

        # Add some NPCs to the bucket
        affiliation = {'Obama': 1, 'Gottfried': 2, 'OReilly': 3, 'Kanye': 4, 'Burbiglia': 5}
        kanye = NPC('@mr_kanyewest', (0,0,1,0), affiliation)
        
        affiliation = {'Obama': 1, 'Gottfried': 1, 'OReilly': 1, 'Kanye': 1, 'Burbiglia': 1}
        ermah = NPC('ermahgerd', (0,0,1,0), affiliation)
        pr = NPC('philosoraptor', (0,0,1,0), affiliation)
        lolcat = NPC('lolcat', (0,0,1,0), affiliation)
        hb = NPC('honeybadger', (0,0,1,0), affiliation)
        oagf = NPC('overlyattachedgirlfriend', (0,0,1,0), affiliation)
        ck = NPC("conspiracykeanu", (0,0,1,0), affiliation)
        ayb = NPC("allyourbase", (0,0,1,0), affiliation)
        xyz = NPC("inyourbase", (0,0,1,0), affiliation)

        self._NPC_Bucket_Lock.acquire()
        self._NPC_Bucket['@mr_kanyewest'] = kanye
        self._NPC_Bucket['ermahgkerd'] = ermah
        self._NPC_Bucket['philosoraptor'] = pr
        self._NPC_Bucket['lolcat'] = lolcat
        self._NPC_Bucket['honeybadger'] = hb
        self._NPC_Bucket['overlyattachedgirlfriend'] = oagf
        self._NPC_Bucket['conspiracykeanu'] = ck
        self._NPC_Bucket['allyourbase'] = ayb
        self._NPC_Bucket['inyourbase'] = xyz
        

        npcs = self._NPC_Bucket.values()
        random.shuffle(npcs)
        for npc in npcs: # Put all NPCs on the queue in random order
            self._NPC_Queue.put(npc)
        self._NPC_Bucket_Lock.release()

        thread.start_new_thread(self.command_thread, ())
        self.logger.write_line("Starting command thread")

        thread.start_new_thread(self.spawn_npc_thread, (10,))
        self.logger.write_line("Starting spawn NPC thread")

        thread.start_new_thread(self.npc_thread, ())
        self.logger.write_line("Starting NPC action thread")
        
        thread.start_new_thread(self.distribute_likes_thread, ())
        self.logger.write_line("Starting distribute likes thread")

        thread.start_new_thread(self.spawn_resources_thread, ())
        self.logger.write_line("Starting spawn resources thread")

    def shutdown_game(self):
        # Winds the game down and creates a directory with all of the saved state information

        self.logger.write_line('Shutting down the game.')

        self._StillAlive = False # Causes all of the threads to close

        for player in self._Characters.values(): # Save all of the player states
            if isinstance(player, Player):
                loader.save_player(player)
        self.logger.write_line('Saved player states.')

        save_num = 1
        while 1:    # Create a directory to save the game state in
            directory = 'SaveState%d' % save_num
            if not os.path.exists(directory):
                os.makedirs(directory)

                objects = []
                for object in self._Objects.values():
                    objects.append(object)
                loader.save_objects(objects, directory) # Save all objects in the game

                for coords in self._Rooms: # Save the rooms to the save state directory
                    path = directory + 'rooms/%d_%d_%d_%d.xml' % coords
                    loader.save_room(self._Rooms[coords], path)

                self.logger.write_line("Saved game state to '%s'" % directory)
                break
            else:
                save_num += 1

    def make_player(self, name, coords = (0,0,1,0), affiliation = {'Obama': 5, 'Kanye': 4, 'OReilly': 3, 'Gottfried': 2, 'Burbiglia': 1}):

        path = 'players/%s.xml' % name
        if os.path.exists(path):    # Load the player if a save file exists for them, otherwise create a new player
            player = loader.load_player(path)
        else:
            player = Player(name, coords, coords, affiliation)

        self._Characters_Lock.acquire()
        self._Characters[player.name] = player # Add to list of players in the game
        self._Characters_Lock.release()

        self._Rooms[player.coords].players.append(player.name) # Add player to list of players in the room they are in

        self.logger.write_line("Created player '%s' at (%d,%d,%d,%d)" % (player.name, player.coords[0], player.coords[1], player.coords[2], player.coords[3]))

    def remove_player(self, name):
        if name in self._Characters:
            self._Characters_Lock.acquire()
            player = self._Characters[name]
            del self._Characters[name] # Remove the player from the list of players in the game
            self._Characters_Lock.release()

            self._Rooms[player.coords].players.remove(player.name) # Remove the player from the room they are in
        elif name in self._Characters_In_Builder:
            self._Characters_In_Builder_Lock.acquire()
            player = self._Characters_In_Builder[name]
            del self._Rooms[player.coords] # Remove the room that was being built since it wasn't finished

            player.coords = player.prev_coords # Save the player in the previous room
            del self._Characters_In_Builder[name] # Remove the player from the list of players
            self._Characters_In_Builder_Lock.release()

        loader.save_player(player) # Save the player
        self.logger.write_line("Removed player '%s'" % player.name)

    def put_commands(self, commands):
        # Takes a list of commands and pushes them to the command queue
        for command in commands:
            if len(command) < 3: # Add tags if the command is missing them, THIS WILL NEED REPLACING
                command = (command[0], command[1], [])

            self._CommandQueue.put(command)
            self.logger.write_line("Put command (%s, %s) in the command queue" % (command[0], command[1]))

    def get_messages(self):
        # Returns all messages currently in the message queue
        messages = []
        while not self._MessageQueue.empty():
            message = self._MessageQueue.get()
            messages.append(message)

            self.logger.write_line("Sending message to server: (%s, %s)" % (message[0], message[1]))

        return messages

    def command_thread(self):
        # Runs commands from the command queue

        while self._StillAlive:
            if not self._CommandQueue.empty():
                command = self._CommandQueue.get()
                player_name = command[0]
                command_str = command[1]
                tags = command[2]
                
                if player_name in self._Characters:
                    messages = engine_helper.do_command(player_name, command_str, tags, self)

                    self.logger.write_line("Running command (%s, %s)" % (player_name, command))

                    for message in messages:
                        self._MessageQueue.put(message)
                elif player_name in self._BuilderQueues:
                    if command_str == 'done_building':
                        self._Characters_In_Builder_Lock.acquire()
                        self._Characters[player_name] = self._Characters_In_Builder[player_name]  # Move player from Builder back to _Characters
                        player = self._Characters[player_name]
                        self._Characters_In_Builder_Lock.release()

                        self._Rooms[player.coords].players.append(player.name) # Add the player to the room

                        self._MessageQueue.put((player.name, engine_helper.get_room_text(player.name, player.coords, self)))   # Put room description in the message queue

                        self.logger.write_line("Player (" + player.name + ") is done building, moved back to game at coordinates (%d,%d,%d,%d)." % player.coords)
                    else:
                        self._BuilderQueues[player_name].put(command)
        
                        self.logger.write_line("Forwarded command to builder queue (%s, %s)" % (player_name, command))
                        
                elif player_name in self._ShopQueues: 
                    if command_str == 'done_shopping':
                        self._Characters_In_Shop_Lock.acquire()
                        self._Characters_Lock.acquire()
                        self._Characters[player_name] = self._Characters_In_Shop[player_name] #Move from shop back to _Characters
                        player = self._Characters[player_name]
                        self._Characters_Lock.release()
                        del self._Characters_In_Shop[player_name]
                        self._Characters_In_Shop_Lock.release()

                        self._Rooms[player.coords].players.append(player_name) #Add the player back to the room, they are done shopping.
                        self._CommandQueue.put((player.name, 'look', []))
                        self.logger.write_line("Player ("+player.name+") is done shopping, moved back to the game at coordinates (%d,%d,%d,%d)." % player.coords)
                        
                    else: #Not done shopping
                        self._ShopQueues[player_name].put(command_str)
                        self.logger.write_line("Forwarded command to shop queue (%s, %s)" % (player_name, command_str))
                        

            time.sleep(.05) # Sleep for 50ms

        self.logger.write_line("Closing command thread.")
        
    def npc_thread(self):
        # Runs the commands for all NPC's in the game

        if self._StillAlive:
            threading.Timer(7.0, self.npc_thread).start()

            npcs = {}
            self._Characters_Lock.acquire()
            for character in self._Characters.keys():
                if isinstance(self._Characters[character], NPC):
                    if self._Characters[character].lifespan > self._Characters[character].cycles:
                        self._Characters[character].cycles += 1 # Increment the NPCs cycles
                        npcs[character] = self._Characters[character]
                    else:   # NPC is out of cycles
                        self._NPC_Queue.put(self._Characters[character])
                        self._Rooms[self._Characters[character].coords].npcs.remove(character) # Remove NPC from the room he was in
                        self._Characters[character].cycles = 0 # Reset cycles to 0
                        del self._Characters[character] # Remove NPC from the list of active characters
            self._Characters_Lock.release()

            for npc in npcs.values():
                engine_helper.npc_action(npc, self)
        else:
            self.logger.write_line("Closing npc action thread.")

    def spawn_npc_thread(self, n):
        # Spawns a new NPC for every 'n' rooms in the game
        while self._StillAlive:
            npcs = {}
            self._Characters_Lock.acquire()
            for character in self._Characters:
                if isinstance(self._Characters[character], NPC):
                    npcs[character] = self._Characters[character]
            self._Characters_Lock.release()

            if ((len(self._Rooms) / n) + 1) > len(npcs):
                # Select an NPC to add to the game
                while 1:
                    if not self._NPC_Queue.empty():
                        npc = self._NPC_Queue.get()

                        tweet_file = open('twitterfeeds/%s.txt' % npc.name)
                        for line in tweet_file.readlines():
                            npc.tweets.append(line.strip())
                        tweet_file.close()

                        vote_ratio = (npc.up_votes / (npc.up_votes + npc.down_votes)) * 100 # Ratio of up votes to down votes

                        if len(npc.tweets) > 0 and vote_ratio >= random.randint(1,100):
                            break # This NPC meets the criteria and will be inserted into the game
                        else:
                            self._NPC_Queue.put(npc)

                    time.sleep(.05) # Sleep for 50ms

                self._Characters_Lock.acquire()
                self._Characters[npc.name] = npc    # Add the NPC to the game
                self._Rooms[npc.coords].npcs.append(npc.name)   # Add the NPC to their room
                self._Characters_Lock.release()

                self.logger.write_line("Spawned NPC: (%s) %s" %(npc.name, npc))

            time.sleep(.05) # Sleep for 50ms

        self.logger.write_line("Closing spawn npc thread.")

    def spawn_resources_thread(self):
        # Spawns Likes, Mutagen and Flat Pack Furniture randomly throughout the game world

        if self._StillAlive:
            threading.Timer(900.0, self.spawn_resources_thread).start() # Runs every 15 minutes

            coords = self._Rooms.keys()
            random.shuffle(coords)
            for i in range(int(len(coords)*.33)):  # Put likes in the first third of the randomized room list
                if self._Rooms[coords[i]] != None:
                    if 'like' in self._Rooms[coords[i]].items:
                        self._Rooms[coords[i]].items['like'] += 5 # Add 5 'Likes' to the room
                    else:
                        self._Rooms[coords[i]].items['like'] = 5 # Put 5 'Likes' in the room

            random.shuffle(coords)
            for i in range(int(len(coords)*.1)):    # Put flat pack furniture in the first tenth of the randomized room list
                if self._Rooms[coords[i]] != None:
                    if 'flat pack furniture' in self._Rooms[coords[i]].items:
                        self._Rooms[coords[i]].items['flat pack furniture'] += 1 # Add 1 Flat Pack Furniture to the room
                    else:
                        self._Rooms[coords[i]].items['flat pack furniture'] = 1 # Put 1 Flat Furniture in the room

            random.shuffle(coords)
            num_rooms = int(len(coords))*.01

            if num_rooms < 1:
                num_rooms = 1   # Make sure that Mutagen spawns in at least 1 room

            for i in range(num_rooms):  # Put Mutagen in 1% of the rooms
                if self._Rooms[coords[i]] != None:
                    if 'mutagen' in self._Rooms[coords[i]].items:
                        self._Rooms[coords[i]].items['mutagen'] += 1 # Add 1 mutagen to the room
                    else:
                        self._Rooms[coords[i]].items['mutagen'] = 1 # Put 1 mutagen in the room
        else:
            self.logger.write_line("Closing spawn resources thread.")

    def distribute_likes_thread(self):
        likes_distribution = {} #Dictionary of player_name -> likes they get this turn around.
        while self._StillAlive:
            self.logger.write_line("Running iteration of distribute_likes_thread")
            self._NPC_Bucket_Lock.acquire()
            for npc in self._NPC_Bucket: #For each NPC, tally up likes going to people.
                self.logger.write_line("Examining score for NPC %s" % npc)
                if (self._NPC_Bucket[npc].up_votes - self._NPC_Bucket[npc].down_votes) > 0: #This has a positive overall score
                    self.logger.write_line("NPC %s has a positive score of %d" % (npc, self._NPC_Bucket[npc].up_votes-self._NPC_Bucket[npc].down_votes))
                    for editor in self._NPC_Bucket[npc].editors:
                        self.logger.write_line("Distributing %d likes to %s" % (int((self._NPC_Bucket[npc].up_votes - self._NPC_Bucket[npc].down_votes)/len(self._NPC_Bucket[npc].editors)), editor))
                        likes_distribution[editor] = likes_distribution.get(editor, 0) + int((self._NPC_Bucket[npc].up_votes - self._NPC_Bucket[npc].down_votes)/len(self._NPC_Bucket_[npc].editors)) #Add this to the likes going to them.
  
                else: #Negative over all score, presently do nothing
                    self.logger.write_line("NPC %s has a non-positive score of %d, moving on to the next NPC." % (npc, (self._NPC_Bucket[npc].up_votes - self._NPC_Bucket[npc].down_votes)))
                    pass
            self._NPC_Bucket_Lock.release()
            
            for room in self._Rooms: #For each room, tally up the likes going to people
                self.logger.write_line("Examining score for room (%d, %d, %d, %d)" % room)
                if (self._Rooms[room].up_votes - self._Rooms[room].down_votes)>0: #This has a positive overall score
                    self.logger.write_line("This room has a positive score of %d" % self._Rooms[room].up_votes - self._Rooms[room].down_votes)
                    for editor in self._Rooms[room].editors:
                        self.logger.write_line("Distributing %d likes to %s" % (int((self._Rooms[room].up_votes - self._Rooms[room].down_votes)/len(self._Rooms[room].editors)), editor))
                        likes_distribution[editor] = likes_distribution.get(editor, 0) + int((self._Rooms[room].up_votes - self._Rooms[room].down_votes)/len(self._Rooms[room].editors)) #Add to the likes going to them.
                    
                else:
                    self.logger.write_line("This room has a non-positive score of %d, moving on to the next Room." % (self._Rooms[room].up_votes - self._Rooms[room].down_votes))
                    pass
            
            for person in likes_distribution: #Distribute the likes after taxes to the people, then reset the distribution total
  
                initial_payout = likes_distribution[person]
                max_tax = 1.0
                inflection_point = 500.0
                welfare_const = 10.0
                welfare = ((initial_payout+welfare_const)/(initial_payout+1))
                intermediate_payout = initial_payout+inflection_point * max_tax*(math.log(initial_payout+inflection_point)-math.log(initial_payout)-(initial_payout/inflection_point))
                final_payout = intermediate_payout+welfare
                if person in self._Characters:
                    self._Characters_Lock.acquire()
                    self._Characters[person].items['likes'] = self._Characters[person].items.get('likes', 0) + final_payout #Put the likes in their inventory
                    self._Characters_Lock.release()
                    self.logger.write_line("Distributing %d likes to player %s in the game" % (final_payout, person))
                    self._MessageQueue.put((person, "You earned %d likes, however after taxes you get %d likes." % (initial_payout, final_payout)))
                    likes_distribution[person] = 0 #Reset the income level for the next tick.
                else: #This person is not in the game, either builder or shop?
                    if person in self._Characters_In_Builder: #Builder, not _Characters
                        self._Characters_In_Builder_Lock.acquire()
                        self._Characters_In_Builder[person].items['likes'] = self._Characters_In_Builder[person].items.get('likes', 0) + final_payout
                        self._Characters_In_Builder_Lock.release()
                        self.logger.write_line("Distributing %d likes to player %s in the builder" % (final_payout, person))
                        self._MessageQueue.put((person, "You earned %d likes, however after taxes you get %d likes." % (initial_payout, final_payout)))
                        likes_distribution[person] = 0
                        
                    elif person in self._Characters_In_Shop:
                        self._Characters_In_Shop_Lock.acquire()
                        self._Characters_In_Shop[person].items['likes'] = self._Characters_In_Shop[person].items.get('likes', 0) + final_payout
                        self._Characters_In_Shop_Lock.release()
                        self.logger.write_line("Distributing %d likes to player %s in the shop" % (final_payout, person))
                        self._MessageQueue.put((person, "You earned %d likes, however after taxes you get %d likes." % (initial_payout, final_payout)))
                        likes_distribution[person]  = 0
                    else: #This person is not in a shop, the builder or the game.
                        self.logger.write_line("User %s not logged in, holding off on distribution of %d likes" % (person, likes_distribution[person]))
            
            time.sleep(3600.0) ###Ticks once an hour.
        
