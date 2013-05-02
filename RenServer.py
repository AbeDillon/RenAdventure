__author__ = 'ADillon, MNutter'

import socket, sys
import thread, threading, Queue
import time, random
import RAProtocol
import engine_classes
import os
import msvcrt
import string
import loader
import ssl
import Q2logging
import sense_effect_filters
import engine

logger = Q2logging.out_file_instance('logs/server/RenServer')

_Player_Locations = {} #{playername: location} where location is "Lobby" or the name of a running world instance? ###IP
_Player_Loc_Lock = threading.RLock() #Lock for player locations dict. ###IP

_Host = socket.gethostbyname(socket.gethostname()) # replace with actual host address

_CMD_Queue = Queue.Queue() # Queue of NPC and Player commands

_Lobby_Queue = Queue.Queue() #Queue of Player chatting/commands for lobby? ###IP

_MSG_Queue = Queue.Queue()

_Players = [] # (mutex controlled)
# key = (string)Player_Name : val = (player_object)
_Players_Lock = threading.RLock()

_Player_OQueues = {} # (mutex controlled)
# key = (string)Player_Name : val = (Queue)Output_Queue
_Player_OQueues_Lock = threading.RLock()

_Player_Data = {} #Hold information until we actually add the player to the game.
_Player_Data_Lock = threading.RLock()

# We may want to keep track of threads
_Threads = [] # mutex controlled
_Threads_Lock = threading.RLock()

#Tracking incoming/outgoing threads for termination
#key = (string)Player_Name : val = (bool) #True to keep running, False to stop the thread.
_InThreads = {}
_OutThreads = {}

#Tracking players logged in
_Logged_in = [] #List with player names

_Banned_names = []

_User_Pings = {}
_User_Pings_Lock = threading.RLock()

_Server_Queue = Queue.Queue()

_World_list = {}

game_engine = engine.Engine('sandbox')

_World_list['sandbox'] = game_engine #This world instance.

def main():
    """

    """
    global _Logger
    global game_engine
    # Initialize _Game_State

    
    #game_engine.init_game()

    print "Game State initialized"
    logger.write_line('Game State initialized')

    # Spin-off Log-in thread
    global _Threads
    global _Threads_Lock
    global _CMD_Queue

    global _Players
    global _Players_Lock

    global _Player_OQueues
    global _Player_OQueues_Lock

    global _Player_States
    global _Player_States_Lock

    login_thread = Login()

    _Threads_Lock.acquire()
    _Threads.append(login_thread)
    _Threads_Lock.release()

    login_thread.start()

    print "Log-in thread spawned"
    logger.write_line('Log-in thread spawned')

    rlt = ReadLineThread()
    rlt.start()

    print "Server console input thread spawned"
    logger.write_line('Server console input thread spawned')

    sat = ServerActionThread()
    sat.start()

    print 'Server action thread spawned'
    logger.write_line('Server action thread spawned')


    timeout = PlayerTimeout()
    timeout.start()
    print 'Player timeout thread spawned'
    logger.write_line('Player timeout thread spawned')
    
    lobby = LobbyThread()
    lobby.start()
    print "Lobby message thread spawned"
    logger.write_line("Lobby message thread spawned")
    
    # Spin-off NPC Spawning thread

    # Spin-off Item Spawning thread

    # Start Main Loop
    print "Entering main loop..."
    logger.write_line('Entering main loop...')
    #loop_cnt = 0
    while 1:
        command = None
        try:
            command = _CMD_Queue.get_nowait()
            print "player: " + command[0] + " command: " + command[1]
            line = '<player>: '+command[0]+' <command>: '+command[1]
            logger.write_line('Processing Command from Queue: %s' % line)
        except:
            pass

        if command != None:
            game_engine.put_commands([command])

        messages = game_engine.get_messages()

        if messages != []:
            distribute(messages)

        #print "loop count = " + str(loop_cnt)
        #loop_cnt += 1
        time.sleep(0.05)

def distribute(messages):
    """

    """
    _Player_OQueues_Lock.acquire()
    for message in messages:
        player = message[0]
        text = message[1]
        
        if player in _Player_OQueues:
            _Player_Loc_Lock.acquire()
            if _Player_Locations[player] != 'lobby':
                _Player_OQueues[player].put(text)
            else:
                pass
            _Player_Loc_Lock.release()
        else:
            pass

    _Player_OQueues_Lock.release()

class Login(threading.Thread):
    """
    This thread listens to a port for new players joining the game.
    When a new player joins the game, the following happens:
        1) the player's player_object is loaded (or created)
        2) the player gets a copy of all the instanced objects in the Game_State
           this copy is added to the player's player_state
        3) the player gets its own output queue and I/O threads
        4) the log-in function designates an I/O  port reserved for the player
           and sends a message to the player indicating which ports to communicate on
        5) the player_object is added to _Players

    TO-DO:
        1) Add checking for max players
        2) Add log-off
        2) Move log-in to lobby
        3) Add registration (name, password, etc.)
    """

    def __init__(self, listen_port=60005, spawn_port=2000, host=""):
        """
        listen_port:        the default port for logging in to the server
        spawn_port:         keeps track of ports to allocate to new players
        spawn_port_lock:    prevents multiple threads from assigning the same ports
        """
        threading.Thread.__init__(self)
        self.host = host
        self.listen_port = listen_port
        self.spawn_port = spawn_port
        self.spawn_port_lock = threading.RLock()

    def run(self):
        """
        Creates a socket on the listen_port,
        waits for new connections, then
        handles new connections
        """
        global _Logger
        # Create a socket to listen for new connections
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Login Socket created"
        logger.write_line('Login Socket created')

        sock.bind((self.host, self.listen_port))
        print "Login Socket bound"
        logger.write_line('Login Socket bound')

        # Listen for new connections
        sock.listen(10)
        print "Login socket listening"
        logger.write_line('Login socket listening')
        while 1:
            # wait to accept a connection
            conn, addr = sock.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            logger.write_line('Connected with '+str(addr[0])+':'+str(addr[1]))
            connstream = ssl.wrap_socket(conn, certfile = 'cert.pem', server_side = True) 
            thread.start_new_thread(self.addPlayer, (connstream, addr))
            time.sleep(0.05)

    def addPlayer(self, conn, addr):
        """
        Add a new player to the game
        """
        global _Logged_in
        global _Banned_names
        global _Logger
        global _User_Pings
        global _Player_Loc_Lock
        global _Player_Locations
        global _World_list
        global _Player_Data
        global _Player_Data_Lock
        
        # receive message
        logged_in = False
        input_data = RAProtocol.receiveMessage(conn)
        a_string = input_data.split() #Split on space
        player_name = a_string[0]
        player_pass = a_string[1]
        player_affil = {} #Current player's affiliation data.
        prev_coords = (0,0,1,0)
        items = []
        fih = 30
        vote_history = {}

        path = 'login_file/%s.txt' % player_name

        if player_name not in _Logged_in and player_name not in _Banned_names: #This person is not already logged in to the game

            if os.path.exists(path): #This file exists
                fin = open(path)
                pwd = fin.readline()
                fin.close()

                if player_pass == pwd: #Login successful
                    print 'User <%s> logged in' % player_name
                    logger.write_line('User <%s> logged in.'%player_name)
                    logged_in = True
                    _Logged_in.append(player_name)
                    _Player_Loc_Lock.acquire()
                    _Player_Locations[player_name] = "lobby" #Log in to the lobby initially
                    _Player_Loc_Lock.release()
                    _Player_Data_Lock.acquire()
                    _Player_Data[player_name] = [] #[0]: location tuple, [1]: affiliation dict
                    _Player_Data_Lock.release()
                    player_path = 'players/%s.xml'%player_name
                    try:
                        person = loader.load_player(player_path)
                        prev_coords = person.prev_coords
                        items = person.items
                        fih = person.fih
                        vote_history = person.vote_history
                    except:
                        logger.write_line("Error loading player file %s, file does not exist" % player_path)
                        print "Error loading player file %s, file does not exist" % player_path
                    player_affil = person.affiliation #Load in the players affiliation
                    location = person.coords
                    
                    _Player_Data_Lock.acquire()
                    _Player_Data[player_name].append(location) #Add the location tuple to the list.
                    
                    _Player_Data_Lock.release()
                else:
                    print 'User <%s> failed to authenticate.' % player_name
                    logger.write_line('User <%s> failed to authenticate.'%player_name)
                    RAProtocol.sendMessage('invalid', conn)
            else: #File does not exist

                if len(a_string) == 2: #We just got name and password, not affiliation
                    RAProtocol.sendMessage('affiliation_get', conn)
                    print 'Getting user affiliation'
                    logger.write_line('Required user affiliation from <%s>'%player_name)
                elif len(a_string) == 12: #We got the affiliation data this time.
                    print 'Creating user: <%s>'% player_name
                    logger.write_line('Creating user: <%s>'%player_name)

                    cur_person = ''
                    for i in range(2, len(a_string)):
                        if i % 2 == 1: #This is an odd numbered cell, and as such is an affinity.
                            player_affil[cur_person] = int(a_string[i])
                        else: #Even numbered, person
                            cur_person = a_string[i]
                            player_affil[cur_person] = 0
                    
                    fin = open(path, 'w')
                    fin.write(player_pass)
                    fin.close()
                    location = (0,0,1,0)
                    logged_in = True
                    _Logged_in.append(player_name)
                    _Player_Loc_Lock.acquire()
                    _Player_Locations[player_name] = "lobby" #Log in to the lobby initially
                    _Player_Loc_Lock.release()
                    _Player_Data_Lock.acquire()
                    _Player_Data[player_name] = []
                    _Player_Data[player_name].append(location) #Add the location tuple to the list.
                    _Player_Data_Lock.release()
                    person = engine_classes.Player(player_name, (0,0,1,0), (0,0,1,0), player_affil) #Make this person 
                
            if logged_in:
                _User_Pings_Lock.acquire()
                _User_Pings[player_name] = time.time()
                _User_Pings_Lock.release()
                _Player_Data_Lock.acquire()
                _Player_Data[player_name].append(player_affil) #This may be {}, but we check for that later.
                _Player_Data[player_name].append(prev_coords) #(0,0,1,0) unless loaded as otherwise.
                _Player_Data[player_name].append(items) #[] if not loaded.
                _Player_Data[player_name].append(fih) #30 if not loaded as otherwise.
                _Player_Data[player_name].append(vote_history) #{} if not loaded as otherwise.
                _Player_Data_Lock.release()

                loader.save_player(person) #Save the file!
                logger.write_line("Creating player file for user <%s>" % player_name)
                
                # *create player state and add to _Player_States (to be added)
                # add new player I/O queues
                oqueue = Queue.Queue()
                line = "\r\n"
                for world in _World_list:
                    eng = _World_list[world]
                    if eng._IsRunning:
                        line += "\t"+world+"\r\n"
                
                oqueue.put("Welcome to the RenAdventure lobby!\r\nThe following worlds are available (type: join name_of_world):"+line) ###TEST
                line = "The following people are in the lobby: \r\n"
                _Player_Loc_Lock.acquire()
                for person in _Player_Locations:
                    if _Player_Locations[person] == 'lobby' and person != player_name: #This person is in the lobby, and isn't the person we're listing people to.
                        line+= "\t"+person+'\r\n'
                        
                _Player_Loc_Lock.release()
                if line != "The following people are in the lobby: \r\n": #We added players to this line
                    oqueue.put(line)
                else: #There are no people in the lobby but you
                    oqueue.put("There is no one else in the lobby at present.")
                    
                #oqueue.put(engine_classes.engine_helper.get_room_text(player_name, location, engine))  #####NEED FILTER

                _Player_OQueues_Lock.acquire()
                _Player_OQueues[player_name] = oqueue
                _Player_Loc_Lock.acquire()
                for person in _Player_Locations:
                    if _Player_Locations[person] == 'lobby' and person != player_name: #This person is in the lobby and is not who just joined. Tell everyone else.
                        _Player_OQueues[person].put("%s has joined the lobby" % player_name)
                _Player_Loc_Lock.release()
                _Player_OQueues_Lock.release()

                # Get I/O port
                self.spawn_port_lock.acquire()
                iport = self.spawn_port
                oport = self.spawn_port + 1
                self.spawn_port += 2
                self.spawn_port_lock.release()

                # spin off new PlayerI/O threads
                ithread = PlayerInput(iport, player_name)
                othread = PlayerOutput(oqueue, addr, oport, player_name)
                
                _Threads_Lock.acquire()
                _Threads.append(ithread)
                _Threads.append(othread)
                _Threads_Lock.release()

                _InThreads[player_name] = True
                _OutThreads[player_name] = True

                ithread.start()
                othread.start()


                # send new I/O ports to communicate on
                ports = str(iport) + " " + str(oport)
                message = str(ports)
                RAProtocol.sendMessage(message, conn)

                # add player to _Players
                _Players_Lock.acquire()
                _Players.append(player_name)
                _Players_Lock.release()

                conn.close()

                print player_name + " added to the game."
                logger.write_line('<'+player_name+'>'+" added to the game.")

        elif player_name not in _Banned_names: #Player name is in _Logged_in, and not in _Banned_names
            print 'Error, attempt to log in to an account already signed on'
            logger.write_line('Error, attempting to log in to an account already signed on: <%s>'%player_name)
            RAProtocol.sendMessage('already_logged_in', conn)

        else: #player_name in _Banned_names
            print 'Attempt to log in with a banned name <%s>, account creation rejected' % player_name
            logger.write_line('Attempt to log in with a banned name <%s>, account creation rejected'%player_name)
            RAProtocol.sendMessage('banned_name',conn)
            
class PlayerInput(threading.Thread):
    """
    Listens for player input adding any input to the local queue
    """

    def __init__(self, port, player_name, host=""):
        """
        port:   a unique port designated for the given players input
        name:   the name of the player
        """
        threading.Thread.__init__(self)
        self.port = port
        self.name = player_name
        self.host = host


    def run(self):
        """
        Listen for player input and push it onto the queue
        """
        global _InThreads
        global _Logger
        # Create Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((self.host, self.port))

        # Listen for connection
        sock.listen(10)

        while 1:
            if not _InThreads[self.name]: #This input thread no longer needs to run
                break
            else:
                conn, addr = sock.accept()
                print 'got input from ' + self.name
                        
                logger.write_line('Got input from: <%s>' % self.name)
                
                connstream = ssl.wrap_socket(conn, certfile='cert.pem', server_side=True)
                thread.start_new_thread(self.handleInput, (connstream, ))
                time.sleep(0.05)
        if not _InThreads[self.name]: #We stopped the loop..
            print 'Input thread for player <%s> ending' % self.name
            logger.write_line('Input thread for player <%s> ending' % self.name)
            del _InThreads[self.name] #So we delete the tracker for it.
    def handleInput(self, conn):
        """
        Receive input, parse the message*, and place it in the correct queue*

        * message parsing and separate queuing will be implemented if the chat
        input and game input share a port
        """
        global _Logged_in
        global _InThreads
        global _OutThreads
        global _Logger
        global _User_Pings
        global game_engine
        global _Player_Loc_Lock
        global _Player_Locations
        global _Lobby_Queue
        
        message = RAProtocol.receiveMessage(conn)

        if message != '_ping_':

            # add it to the queue
            if message != 'quit':
                _Player_Loc_Lock.acquire() ###IP
                location = _Player_Locations.get(self.name, 'lobby') #Get whether player is in "Lobby" or a world? ###IP
                _Player_Loc_Lock.release() ###IP
                
                if location == 'lobby': #Player is in the lobby ###IP
                    try:
                        _Lobby_Queue.put((self.name, message))
                        logger.write_line("Putting in the lobby message queue: <%s>; '%s'" % (self.name, message))
                    except:
                        pass
                elif location == 'sandbox': #Player is in the game instance known as sandbox ###IP
                    try:
                        _CMD_Queue.put((self.name, message))
                        logger.write_line('Putting in the command queue: <%s>; "%s"'%(self.name, message))
                    except:
                        pass
                        

                conn.close()

            elif message == 'quit':#User is quitting, we can end this thread
                _InThreads[self.name] = False
                _OutThreads[self.name] = False
                _Logged_in.remove(self.name)
                logger.write_line('Removing <%s> from _Logged_in' % self.name)
                game_engine._Characters_Lock.acquire()
                if self.name in game_engine._Characters: #This player has been added to the game
                    game_engine.remove_player(self.name) #Remove player existence from gamestate.
                game_engine._Characters_Lock.release()
                _Player_Loc_Lock.acquire()
                if _Player_Locations[self.name] == 'lobby': #This person is in the lobby, tell everyone they quit.
                    _Player_OQueues_Lock.acquire()
                    for person in _Player_OQueues:
                        if person != self.name: #This is not the person quitting, tell them who quit.
                            _Player_OQueues[person].put("%s quit."%self.name)
                    _Player_OQueues_Lock.release()
                _Player_Loc_Lock.release()

        elif message == '_ping_': #Keepalive ping
            _User_Pings_Lock.acquire()
            _User_Pings[self.name] = time.time()
            _User_Pings_Lock.release()
            logger.write_line("Got a ping from <%s>"%self.name)

class PlayerTimeout(threading.Thread): #Thread to handle players who time-out

    def run(self):
        global _Logged_in
        global _InThreads
        global _OutThreads
        global _Logger
        global _User_Pings
        global _User_Pings_Lock
        global _Player_OQueues_Lock
        global _Player_OQueues
        global game_engine

        timeout = 15
        to_rem = []
        while 1:
            _User_Pings_Lock.acquire()
            for person in to_rem:
                del _User_Pings[person]
            to_rem = []
            for player in _User_Pings:
                if time.time() - _User_Pings[player] > timeout: #This client has timed out
                    print 'Player timed out: <%s>' % player
                    logger.write_line('Removing <%s> from game: Timed out' % player)
                    game_engine._Characters_Lock.acquire()
                    if player in game_engine._Characters or player in game_engine._Characters_In_Builder:
                        if player in game_engine._Characters: #Player in regular characters
                            person = game_engine._Characters[player]
                            loader.save_player(person)
                            logger.write_line("Saving player file for <%s>" % player)
                        elif player in game_engine._Characters_In_Builder: #Player in builder
                            game_engine._Characters_In_Builder_Lock.acquire()
                            person = game_engine._Characters_In_Builder[player]
                            loader.save_player(person)
                            logger.write_line("Saving player file for <%s>" % player)
                            game_engine._Characters_In_Builder_Lock.release()
                        game_engine.remove_player(player)
                    else:
                        logger.write_line("Error! Could not find player in _Characters or _Characters_In_Builder: <%s>" % player)
                    game_engine._Characters_Lock.release()
                    if player in _Logged_in:
                        _Logged_in.remove(player)
                    to_rem.append(player)
                    _Player_OQueues_Lock.acquire()
                    _Player_OQueues[player].put('Error, it appears this person has timed out.')
                    _Player_OQueues_Lock.release()
            _User_Pings_Lock.release()
            time.sleep(0.05)

class PlayerOutput(threading.Thread):
    """
    This thread polls a player's output Queue and sends the contents to the player client

    TO DOs:
        1) handle queue.get exceptions
        2) time-out (?)
    """

    def __init__(self, output_queue, addr, port, player_name, host=""):
        """
        queue:  The queue of messages to be sent to the player
        port:   The port that the player is listening on
        name:   The name of the player
        """
        threading.Thread.__init__(self)
        self.queue = output_queue
        self.address = addr
        self.port = port
        self.name = player_name
        self.host = socket.gethostname()

    def run(self):
        """
        poll output queue and send messages to player
        """
        global _OutThreads
        global _Logger
        while _OutThreads[self.name]:
            # Listen to Output Queue
            message = ""
            try:
                # get message
                message = self.queue.get()
                
            except:
                # this should handle exceptions
                pass
            if message != "" and message != 'Error, it appears this person has timed out.':
                print message
                    
                logger.write_line('Sending message to <%s>: "%s"'%(self.name, message))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ssl_sock = ssl.wrap_socket(sock, certfile='cert.pem')
                # connect to player
                try:
                    ssl_sock.connect((self.address[0], self.port))
                    # send message
                    RAProtocol.sendMessage(message, ssl_sock)
                    # close connection
                    ssl_sock.close()  
                except:
                    #Could not make connection or send message
                    logger.write_line('Error making connection or sending message to <%s>'%self.name)
                time.sleep(0.05)
            elif message == 'Error, it appears this person has timed out.':
                print message
                logger.write_line('Sending message to <%s>: "%s"'%(self.name, message))
                _OutThreads[self.name] = False
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ssl_sock = ssl.wrap_socket(sock, certfile='cert.pem')
                try:
                    ssl_sock.connect((self.address[0], self.port))
                    RAProtocol.sendMessage(message, ssl_sock)
                    ssl_sock.close()
                except:
                    logger.write_line('Failed to either connect or send a message to <%s> after timeout.'%self.name)
                time.sleep(0.05)
        if not _OutThreads[self.name]: #This thread will no longer be running...
            print 'Output thread for player <%s> ending.' % self.name
            logger.write_line('Output thread for player <%s> ending.'%self.name)
            del _OutThreads[self.name] #So we delete the tracker for it.


class ReadLineThread(threading.Thread):
    """

    """

    def run(self):
        """

        """
        global _Server_Queue
        while True: #What would cause this to stop? Only the program ending.
            line = ""
            while 1:
                char = msvcrt.getche()
                if char == "\r": # enter
                    break

                elif char == "\x08": # backspace
                    # Remove a character from the screen
                    msvcrt.putch(" ")
                    msvcrt.putch(char)

                    # Remove a character from the string
                    line = line[:-1]

                elif char in string.printable:
                    line += char

                time.sleep(0.01)

            try:
                _Server_Queue.put(line)
                if line != '':
                    _Logger.debug('Input from server console: %s' % line)
            except:
                pass

class ServerActionThread(threading.Thread):
    """

    """
    def run(self):
        """

        """
        global _Server_Queue
        global _CMD_Queue
        global game_engine
        global _World_list
        
        done = False
        while not done:
            command = ''
            try:
                command = _Server_Queue.get()
            except:
                pass

            if command != '': #We got something
                logger.write_line("Got server command: %s" % command)
                if command.lower() == 'quit':
                    print 'Got quit, shutting down server and all engines.'
                    done = True
                    for engine in _World_list: #For each engine...
                        this_engine = _World_list[engine] #Get the engine.
                        logger.write_line("Shutting down engine %s" % engine)
                        print "Shutting down engine %s" % engine
                        this_engine.shutdown_game()
                    break
                    
                elif "start" in command.lower(): #command syntax: start engine_name <save_state#>
                    cmd = command.split() #Split it up
                    save_state = None
                    if len(cmd) > 3 or len(cmd) < 2: #We got too much or too few
                        print "Error, command syntax for start is: start engine_name [save_state]"
                    else:
                        if cmd[0].lower() == 'start': #Command is a start command, we will start an engine.
                            eng_name = cmd[1] #Get engine name.
                            if len(cmd) == 3: #We got a save state too.
                                save_state = cmd[2]
                            if eng_name in _World_list: #This is a valid engine to start up.
                                engine = _World_list[eng_name] #Get the engine
                                if not engine._IsRunning: #The engine has not been started yet, we can start it.
                                    if save_state != None: #We got a value for this, start the engine with this number
                                        logger.write_line("Starting engine %s with save state number %s" % (eng_name, save_state))
                                        print "Starting engine %s with save state number %s" % (eng_name, save_state)
                                        engine.init_game(int(save_state))
                                    else: #We did not get a save state
                                        engine.init_game() #Start without save state.
                                        logger.write_line("Starting engine %s without save state" % eng_name)
                                        print "Starting engine %s without save state" % eng_name
                                else: #This engine is already running, we don't want to start it again.
                                    print "Engine %s is already running, you cannot start it again." % eng_name
                                    logger.write_line("Starting of engine %s declined, engine already running" % eng_name)
                                
                elif "stop" in command.lower(): #command syntax: stop engine_name
                    cmd = command.split()
                    if len(cmd) > 2 or len(cmd) < 2: #We did not get enough
                        print "Error, command syntax for stop is: stop engine_name"
                    else: #Valid
                        eng_name = cmd[1] #Get the name of it
                        if eng_name in _World_list: #This is a valid engine we can shut down
                            engine = _World_list[eng_name]
                            if engine._IsRunning:
                                engine.shutdown_game()
                                logger.write_line("Got command to shutdown %s engine. Proceeding." % eng_name)
                                print "Shutting down engine <%s>" % eng_name
                            else: #This engine is already shut down.
                                print "This engine is already shut down <%s>" % eng_name
                        else: #This is not an engine we know of.
                            print "Unrecognized engine name <%s>" % eng_name
                    
             
                else: #No other commands presently.
                    print 'Got command: %s' % command
            time.sleep(0.05)
        return True

class NPCSpawnThread(threading.Thread):
    """
    This thread spawns NPCs on the map every X-seconds based on some NPC-spawning rules
    """

    def __init__(self, spawnable_NPCs):
        """

        """
        threading.Thread.__init__(self)
        self.NPCs = spawnable_NPCs

    def run(self):
        """

        """
        # every X-seconds
        # Check Spawning Rules
        # Randomly Choose NPC_object
        # -Create NPC State (choose random starting location)
        # add new player I/O queues
        # spin off new NPC thread
        # add NPC to _Players


class ItemSpawnThread(threading.Thread):
    """
    Thread spawns items every X-seconds based on some item-spawning rules
    """

    def __init__(self, spawnable_items):
        """

        """
        threading.Thread.__init__(self)
        self.items = spawnable_items

    def run(self):
        """

        """
        # every X-seconds
        # check spawning rules
        # randomly add new objects to _Game_State

class NPCThread(threading.Thread):
    """
    This thread executes an NPCs script every X-seconds
    """

    def __init__(self, NPC_object):
        """

        """
        threading.Thread.__init__(self)
        self.NPC_object = NPC_object

    def run(self):
        """

        """
        # every X-seconds
        # run NPC script

class TimedScriptThread(threading.Thread):
    """
    This thread executes scripts after a given amount of time
    NOTE: this might be better implemented using threading.Timer
    """

    def __init__(self, time, script):
        """

        """
        threading.Thread.__init__(self)
        self.time = time
        self.script = script

    def run(self):
        """

        """
        # Wait until time.time() >= time
        # run script
        
        
class LobbyThread(threading.Thread):

    def run(self):
        global _Lobby_Queue
        global _World_list
        global _Player_Locations
        global _Player_Loc_Lock
        global _Player_OQueues_Lock
        global _Player_OQueues
        global game_engine
        global _Players
        global _Players_Lock
        global _Player_Data
        global _Player_Data_Lock
        global _CMD_Queue
        
        while 1:
            if not _Lobby_Queue.empty():
                msg = _Lobby_Queue.get()
                if "join" in msg[1]: #Syntax format: <player>: join (worldname)
                    player = msg[0] #Player name
                    _Player_Data_Lock.acquire()
                    location = _Player_Data[player][0] #Location
                    affil = _Player_Data[player][1] #Affiliation
                    prev_loc = _Player_Data[player][2] #Previous location
                    items = _Player_Data[player][3] #Items
                    fih = _Player_Data[player][4] #FIH
                    vote_hist = _Player_Data[player][5] #Vote History
                    
                    _Player_Data_Lock.release()
                    message = msg[1]
                    
                    cmd, world = msg[1].split()
                    if world in _World_list: #This is a world we know about, let's "move" the player here.
                        eng = _World_list[world]
                        if eng._IsRunning:
                            _Player_Loc_Lock.acquire()
                            _Player_Locations[player] = world #Route this players messages to that world
                            _Player_Loc_Lock.release()
                        else: #This is not a running engine, don't let them access this.
                            output = "That engine is not up and running right now, you cannot join it."
                            _Player_OQueues_Lock.acquire()
                            _Player_OQueues[player].put(output)
                            _Player_OQueues_Lock.release()

                        if affil != {}: #We have this players affiliation, give it.
                            game_engine.make_player(player, location, affil) #Make with given affiliation
                            game_engine._Characters_Lock.acquire()
                            game_engine._Characters[player].prev_coords = prev_loc
                            for item in items:
                                game_engine._Characters[player].items[item] = items[item]
                            game_engine._Characters[player].fih = fih
                            game_engine._Characters[player].vote_history = vote_hist
                            game_engine._Characters_Lock.release()

                        else: #This player's affiliation is {}, default make without extra information.
                            game_engine.make_player(player, location) #Make with default
                            
                            
                        _Player_Data_Lock.acquire()
                        _Player_Data[player] = [] #Reset the list for this person
                        _Player_Data_Lock.release()
                            
                        _CMD_Queue.put((player, 'look'))
                      
                
                elif msg[1] == "_ping_": #This is just a ping.
                    _User_Pings_Lock.acquire()
                    _User_Pings[self.name] = time.time()
                    _User_Pings_Lock.release()
                    logger.write_line("Got a ping from <%s>"% msg[0])
                    
                else: #This is a regular message for now.
                    player = msg[0]
                    message = msg[1]

                    _Player_OQueues_Lock.acquire()
                    for person in _Player_OQueues:
                        if person != player: #We want them to get the message, they weren't the ones who said it.
                            output = "<"+player+">: "+message
                            _Player_Loc_Lock.acquire()
                            if _Player_Locations[person] == 'lobby': #They are in the lobby and so should get this message
                                _Player_OQueues[person].put(output)
                            else: #They are not in the lobby
                                pass
                            _Player_Loc_Lock.release()
                        else: #They are the person who said the message, send them a copy?
                            output = '\r\n'
                            _Player_OQueues[person].put(output)
                            # _Player_Loc_Lock.acquire()
                            # if _Player_Locations[person] == 'lobby': #Person who said it, still in lobby
                                # output = "> "
                                # _Player_OQueues[person].put(output)
                            # _Player_Loc_Lock.release()
                            
                    _Player_OQueues_Lock.release()
                    
                time.sleep(0.05)
                
            else:
                time.sleep(0.05)
            

if __name__ == "__main__":
    main()

