__author__ = 'ADillon, MNutter'
#Large singleport server is designed to use the single input port however it will use more threads for data send/receive

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
import copy

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

_Shutdown = False #Used to run server until shutdown.
_Shutdown_Lock = threading.RLock() 

#Tracking players logged in
_Logged_in = [] #List with player names

_Banned_names = []

_Server_Queue = Queue.Queue() #Set up a queue for commands to the server.

_User_Pings = {}
_User_Pings_Lock = threading.RLock()

_Server_Queue = Queue.Queue()

_World_list = {}

game_engine = engine.Engine('sandbox')

_World_list['sandbox'] = game_engine #This world instance.

def main(): 
    global _Logger
    global game_engine
    # Initialize _Game_State

    
    game_engine.init_game()

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
    
    global _Shutdown
    global _Shutdown_Lock

    login_thread = Login_Thread()

    _Threads_Lock.acquire()
    _Threads.append(login_thread)
    _Threads_Lock.release()

    login_thread.start()

    print "Log-in thread spawned"
    logger.write_line('Log-in thread spawned')
    
    
    timeout = PlayerTimeout()
    timeout.start()
    print 'Player timeout thread spawned'
    logger.write_line('Player timeout thread spawned')
    
    lobby = LobbyThread()
    lobby.start()
    print "Lobby message thread spawned"
    logger.write_line("Lobby message thread spawned")
    
    
    rlt = ReadLineThread()
    rlt.start()
    print "Read Line thread for server spawned"
    logger.write_line("Read line thread for server spawned")
    
    sat = ServerActionThread()
    sat.start()
    print "Server Action thread spawned"
    logger.write_line("Server Action thread spawned")
    
       
    
    print "Entering main loop..."
    logger.write_line('Entering main loop...')
    _Shutdown_Lock.acquire()
    done = _Shutdown
    _Shutdown_Lock.release()
    while not done:
        command = None
        try:
            command = _CMD_Queue.get()
            print "player: " + command[0] + " command: " + command[1]
            line = '<player>: '+command[0]+' <command>: '+command[1]
            logger.write_line('Processing Command from Queue: %s' % line)
        except:
            pass

        if command != None:
            game_engine.put_commands([command])
        time.sleep(0.50) #Wait between putting command in engine and getting message?
        messages = game_engine.get_messages()


        if messages != []:
            distribute(messages)
            
        _Shutdown_Lock.acquire()
        done = _Shutdown
        _Shutdown_Lock.release()
        time.sleep(0.05)

    
def distribute(messages):
    """

    """
    global _Player_OQueues_Lock
    global _Player_OQueues
    global _Player_Loc_Lock
    global _Player_Locations
    logger.write_line("Got %d messages from the engine." % len(messages))
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
    
    
    
class Login_Thread(threading.Thread): #Thread handles getting client connections, making dict of them, doing authentication.
    def __init__(self, listen_port=8080, host=socket.gethostbyname(socket.gethostname())):
        """
        listen_port:        the default port for logging in to the server

        """
        threading.Thread.__init__(self)
        self.host = host
        self.listen_port = listen_port

    def run(self):
        """
        Creates a socket on the listen_port,
        waits for new connections, then
        handles new connections
        """
        global _Logger
        global _Logged_in
        global _Banned_names
        global _User_Pings
        global _Player_Loc_Lock
        global _Player_Locations
        global _World_list
        global _Player_Data
        global _Player_Data_Lock
        global _Player_Connections
        global _Player_Connections_Lock
        global _Threads_Lock
        global _Threads
        global _Shutdown
        global _Shutdown_Lock
        
        # Create a socket to listen for new connections
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Login Socket created"
        logger.write_line('Login Socket created')

        sock.bind((self.host, self.listen_port))
        print "Login Socket bound"
        logger.write_line('Login Socket bound')

        # Listen for new connections
        sock.listen(1000)
        print "Login socket listening"
        logger.write_line('Login socket listening')
            # wait to accept a connection
        _Shutdown_Lock.acquire()
        done = _Shutdown
        _Shutdown_Lock.release()
        while not done:
            conn, addr = sock.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            logger.write_line('Connected with '+str(addr[0])+':'+str(addr[1]))
            #connstream = ssl.wrap_socket(conn, certfile = 'cert.pem', server_side = True) 
            start_dialogue = RAProtocol.receiveMessage(conn)
            logger.write_line("Got start_dialogue: %s" % start_dialogue) ###DEBUG
            a_string = start_dialogue.split() #Split on space
            player_name = a_string[0]
            player_pass = a_string[1]
            flag = a_string[2] #Flag for either "_login_" to attempt to login, or "_register_" to attempt to register?
            if flag == '_login_': #Try and log them in
                print "Player wishes to log in as <%s>, verifying.." % player_name
                logger.write_line("Player wishes to log in as <%s>, verifying..." % player_name)
                proceed = self.verify_player(player_name, player_pass, conn)
                if proceed: #Valid player, with registration data
                    it = PlayerInput(player_name, conn) #Input reading thread for player_name using conn.
                    it.start() #Begin execution of in thread.
                    
                    _Threads_Lock.acquire()
                    _Threads.append(it)
                    _Threads_Lock.release()

                    
            elif flag == '_register_': #Attempt to register them based on the data
                print "Player wishes to register as <%s>, proceeding.." % player_name
                logger.write_line("Player wishes to register as <%s>, proceeding..." % player_name)
                proceed = self.register_player(player_name, player_pass, conn)
                if proceed: #Valid player, we have their registration now.
                    it = PlayerInput(player_name, conn) #Input reading thread for player_name using conn.
                    it.start() #Begin execution of in thread.
                    
                    _Threads_Lock.acquire()
                    _Threads.append(it)
                    _Threads_Lock.release()
                    
            _Shutdown_Lock.acquire()
            done = _Shutdown
            _Shutdown_Lock.release()
                
            time.sleep(0.05)
            
    def verify_player(self, name, password, connection):
    
        global _Logged_in
        global _Banned_names
        global _Logger
        global _User_Pings
        global _Player_Loc_Lock
        global _Player_Locations
        global _World_list
        global _Player_Data
        global _Player_Data_Lock
        global _Threads_Lock
        global _Threads
        
        path = 'login_file/%s.txt' % name 
        logger.write_line("Verifying player credentials")
        player_affil = {} #Current player's affiliation data.
        prev_coords = (0,0,1,0)
        items = []
        fih = 30
        vote_history = {}
        
        if name not in _Logged_in and name not in _Banned_names: #This person is not already logged in to the game, they may proceed to the next step.
            logger.write_line("This player is not already logged in, or banned. Proceed")
            if os.path.exists(path): #This file exists
                logger.write_line("This player's login file does indeed exist.")
                fin = open(path)
                pwd = fin.readline()
                fin.close()

                if password == pwd: #Login successful
                
                    print 'User <%s> authenticated' % name
                    logger.write_line('User <%s> authenticated.'%name)
                    _Logged_in.append(name)
                    _Player_Loc_Lock.acquire()
                    _Player_Locations[name] = "lobby" #Log in to the lobby initially
                    _Player_Loc_Lock.release()
                    _Player_Data_Lock.acquire()
                    _Player_Data[name] = [] #[0]: location tuple, [1]: affiliation dict
                    _Player_Data_Lock.release()
                    player_path = 'players/%s.xml'%name
                    try:
                        person = loader.load_player(player_path)
                        logger.write_line("Loading player file %s successful." % player_path)
                        logged_in = True
                        prev_coords = person.prev_coords
                        items = person.items
                        fih = person.fih
                        vote_history = person.vote_history

                    except:
                        logger.write_line("Error loading player file %s, file does not exist" % player_path)
                        print "Error loading player file %s, file does not exist" % player_path
                        return False
                    player_affil = person.affiliation #Load in the players affiliation
                    location = person.coords
                    
                    _Player_Data_Lock.acquire()
                    _Player_Data[name].append(location) #Add the location tuple to the list.
                    
                    _Player_Data_Lock.release()
                    
                else:
                    print 'User <%s> failed to authenticate.' % name
                    logger.write_line('User <%s> failed to authenticate.'%name)
                    RAProtocol.sendMessage('_invalid_', connection)
                    return False
                
            else: #File does not exist, require them to register
                RAProtocol.sendMessage("_requires_registration_", connection) #Tell them they are required to register and drop them?
                logger.write_line("User is not registered, ending.")
                return False
            
            
            if logged_in: #They have been logged in and their player data is known.
                _User_Pings_Lock.acquire()
                _User_Pings[name] = time.time()
                _User_Pings_Lock.release()
                _Player_Data_Lock.acquire()
                _Player_Data[name].append(player_affil) #This may be {}, but we check for that later.
                _Player_Data[name].append(prev_coords) #(0,0,1,0) unless loaded as otherwise.
                _Player_Data[name].append(items) #[] if not loaded.
                _Player_Data[name].append(fih) #30 if not loaded as otherwise.
                _Player_Data[name].append(vote_history) #{} if not loaded as otherwise.
                _Player_Data_Lock.release()
                
                loader.save_player(person) #Save the file
                logger.write_line("Saving player file for user <%s>" % name)
                
                # *create player state and add to _Player_States (to be added)
                # add new player I/O queues
                oqueue = Queue.Queue()
                line = "\r\n"
                for world in _World_list:
                    line += "\t"+world+"\r\n"
                
                oqueue.put("Welcome to the RenAdventure lobby!\r\nThe following worlds are available (type: join name_of_world):"+line) ###TEST
                _Player_OQueues_Lock.acquire()
                _Player_OQueues[name] = oqueue
                _Player_OQueues_Lock.release()
                line = "The following people are in the lobby: \r\n"
                _Player_Loc_Lock.acquire()
                for person in _Player_Locations:
                    if _Player_Locations[person] == 'lobby' and person != name: #This person is in the lobby, and isn't the person we're listing people to.
                        line+= "\t"+person+'\r\n'
                        
                _Player_Loc_Lock.release()
                if line != "The following people are in the lobby: \r\n": #We added players to this line
                    oqueue.put(line)
                else: #There are no people in the lobby but you
                    oqueue.put("There is no one else in the lobby at present.")
                    
                #oqueue.put(engine_classes.engine_helper.get_room_text(name, location, engine))  #####NEED FILTER
                RAProtocol.sendMessage("_get_ip_", connection) #Tell them we need their IP for outgoing messages
                logger.write_line("Getting IP from client..")
                
                ip = RAProtocol.receiveMessage(connection) # Get their IP from the client and make an outgoing connection with it.
                logger.write_line("Received the following IP from the client: %s" % ip)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect((ip, 8888)) #Connect to client on port 8888 for sending messages
                    logger.write_line("Connected to socket.")
                    RAProtocol.sendMessage("_out_conn_made_", connection)
                    ot = PlayerOutput(name, sock) #Output thread for this player
                    ot.start()
                    
                    _Threads_Lock.acquire()
                    _Threads.append(ot)
                    _Threads_Lock.release()
                    
                except: 
                    RAProtocol.sendMessage("_connection_fail_", connection)
                    logger.write_line("Failed to connect")
                    
                
                
                _Players_Lock.acquire()
                _Players.append(name)
                _Players_Lock.release()
                
                
                
                return True #Player has been logged in, et cetera if they made it this far.
                
        elif name not in _Banned_names: #Player name is in _Logged_in, and not in _Banned_names
            print 'Error, attempt to log in to an account already signed on'
            logger.write_line('Error, attempting to log in to an account already signed on: <%s>'%name)
            RAProtocol.sendMessage('already_logged_in', connection)
            return False

        else: #player_name in _Banned_names
            print 'Attempt to log in with a banned name <%s>, account creation rejected' % name
            logger.write_line('Attempt to log in with a banned name <%s>, account creation rejected'%name)
            RAProtocol.sendMessage('banned_name',connection)
            return False
                
        
    def register_player(self, name, password, connection):
        global _Logged_in
        global _Player_Loc_Lock
        global _Player_Locations
        global _Player_Data_Lock
        global _Player_Data
        global _User_Pings_Lock
        global _User_Pings
        global _Threads_Lock
        global _Threads
        global _Players_Lock
        global _Players
        
    
        path = 'login_file/%s.txt' % name
        
        location = (0,0,1,0)
        
        player_affil = {} #Initially blank affiliation
        items = []
        prev_coords = (0,0,1,0)
        fih = 30
        vote_history = {}
        
        print 'Creating user: <%s>'% name
        logger.write_line('Creating user: <%s>'%name)
        RAProtocol.sendMessage("_affiliation_get_", connection) #Let them know we need their affiliation
        temp_affil = RAProtocol.receiveMessage(connection) #Get their affiliation
        a_string = temp_affil.split()
        if len(a_string) == 10: #Affiliation data
            logger.write_line("Received a user affiliation, confirmed.")
            cur_person = ''
            for i in range(0, len(a_string)):
                if i % 2 == 1: #This is an odd numbered cell, and as such is an affinity.
                        player_affil[cur_person] = int(a_string[i])
                else: #Even numbered, person
                    cur_person = a_string[i]
                    player_affil[cur_person] = 0
                    
            fin = open(path, 'w')
            fin.write(password) #Save the player file
            fin.close()
            logger.write_line("Player login file created")
            
            logged_in = True
            _Logged_in.append(name)
            _Player_Loc_Lock.acquire()
            _Player_Locations[name] = "lobby" #Log in to the lobby initially
            _Player_Loc_Lock.release()
            _Player_Data_Lock.acquire()
            _Player_Data[name] = []
            _Player_Data[name].append(location) #Add the location tuple to the list.
            _Player_Data_Lock.release()
            person = engine_classes.Player(name, (0,0,1,0), (0,0,1,0), player_affil) #Make this person
            
            loader.save_player(person)
            logger.write_line("Saving newly created player %s" % name)
            
        else:
            RAProtocol.sendMessage("_reject_", connection)
            logger.write_line("User login attempt rejected")
            return False
            
        if logged_in:
            _User_Pings_Lock.acquire()
            _User_Pings[name] = time.time()
            logger.write_line("Putting user into _User_Pings")
            _User_Pings_Lock.release()
            _Player_Data_Lock.acquire()
            _Player_Data[name].append(player_affil) #This may be {}, but we check for that later.
            _Player_Data[name].append(prev_coords) #(0,0,1,0) unless loaded as otherwise.
            _Player_Data[name].append(items) #[] if not loaded.
            _Player_Data[name].append(fih) #30 if not loaded as otherwise.
            _Player_Data[name].append(vote_history) #{} if not loaded as otherwise.
            _Player_Data_Lock.release()
            logger.write_line("Finished adding additional data to _Player_Data[%s]" % name)
            
            
            # *create player state and add to _Player_States (to be added)
            # add new player I/O queues
            oqueue = Queue.Queue()
            _Player_OQueues_Lock.acquire()
            _Player_OQueues[name] = oqueue
            _Player_OQueues_Lock.release()
            
            line = "\r\n"
            for world in _World_list:
                line += "\t"+world+"\r\n"
            
            oqueue.put("Welcome to the RenAdventure lobby!\r\nThe following worlds are available (type: join name_of_world):"+line) ###TEST
            logger.write_line("Sending welcome message")
            line = "The following people are in the lobby: \r\n"
            _Player_Loc_Lock.acquire()
            for person in _Player_Locations:
                if _Player_Locations[person] == 'lobby' and person != name: #This person is in the lobby, and isn't the person we're listing people to.
                    line+= "\t"+person+'\r\n'
                    
            _Player_Loc_Lock.release()
            if line != "The following people are in the lobby: \r\n": #We added players to this line
                oqueue.put(line)
            else: #There are no people in the lobby but you
                oqueue.put("There is no one else in the lobby at present.")
                
            #oqueue.put(engine_classes.engine_helper.get_room_text(name, location, engine))  #####NEED FILTER
            RAProtocol.sendMessage("_get_ip_", connection) #Tell them we need their IP for outgoing messages
            logger.write_line("Getting IP from client...")
            ip = RAProtocol.receiveMessage(connection) # Get their IP from the client and make an outgoing connection with it.
            logger.write_line("Received the following IP: %s" % ip)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                
                sock.connect((ip, 8888)) #Connect to client on port 8888 for sending messages
                logger.write_line("Connection to socket on port 8888 made.")
                RAProtocol.sendMessage("_out_conn_made_", connection)
                ot = PlayerOutput(name, sock)
                ot.start()
                
                _Threads_Lock.acquire()
                _Threads.append(ot)
                _Threads_Lock.release()
                
            except:
                RAProtocol.sendMessage("_conn_failure_", connection)
                logger.write_line("Failed to connect.")
            
            return True 
            
            
            
        else:
            RAProtocol.sendMessage("_reject_", connection)
            logger.write_line("User log in rejected")
            return False
            
            
class PlayerInput(threading.Thread): #Thread polls connections for data and passes it to engine.
    def __init__(self, name, connection):
        threading.Thread.__init__(self)
        self.name = name
        self.connection = connection
        
    def run(self):
        global _Shutdown
        global _Shutdown_Lock
        logger.write_line("Beginning input thread for %s" % self.name)
        _Shutdown_Lock.acquire()
        done = _Shutdown
        _Shutdown_Lock.release()
        while not done:

            try:
                input_data = RAProtocol.receiveMessage(self.connection)
                logger.write_line("Got the following from the client %s: %s" % (self.name, input_data))
            except:
                input_data = ''
                
            if input_data != '': #We got something, yay
                self.handle_input(self.name, input_data)
                
            _Shutdown_Lock.acquire()
            done = _Shutdown
            _Shutdown_Lock.release()
                    
            time.sleep(0.05)
                    
                    
    def handle_input(self, player, message):
        global _Player_Connections
        global _Player_Connections_Lock
        global _CMD_Queue
        global _Logged_in
        global _InThreads
        global _OutThreads
        global _Logger
        global _User_Pings
        global game_engine
        global _Player_Loc_Lock
        global _Player_Locations
        global _Lobby_Queue
        global _Client_Connections_Lock
        global _Client_Connections
        global _Player_OQueues
        global _Player_OQueues_Lock
        
        if message != '_ping_':

            # add it to the queue
            if message != 'quit':
                _Player_Loc_Lock.acquire() ###IP
                location = _Player_Locations.get(player, 'lobby') #Get whether player is in "Lobby" or a world? ###IP
                _Player_Loc_Lock.release() ###IP
                
                if location == 'lobby': #Player is in the lobby ###IP
                    try:
                        _Lobby_Queue.put((player, message))
                        logger.write_line("Putting in the lobby message queue: <%s>; '%s'" % (player, message))
                    except:
                        pass
                elif location == 'sandbox': #Player is in the game instance known as sandbox ###IP
                    try:
                        _CMD_Queue.put((player, message))
                        logger.write_line('Putting in the command queue: <%s>; "%s"'%(player, message))
                    except:
                        pass
                        

            elif message == 'quit':#User is quitting, we can end this thread
                _Logged_in.remove(player)
                logger.write_line('Removing <%s> from _Logged_in' % player)
                print "Player <%s> quitting." % player
                game_engine._Characters_Lock.acquire()
                if player in game_engine._Characters: #This player has been added to the game
                    game_engine.remove_player(player) #Remove player existence from gamestate.
                game_engine._Characters_Lock.release()
                _Player_Loc_Lock.acquire()
                loc = _Player_Locations[player]
                _Player_Loc_Lock.release()
                if loc == 'lobby': #This person is in the lobby, tell everyone they quit.
                    for person in _Player_OQueues:
                        if person != player: #This is not the person quitting, tell them who quit.
                            _Player_OQueues_Lock.acquire()
                            _Player_OQueues[person].put("%s quit."%player)
                            _Player_OQueues_Lock.release()
                _User_Pings_Lock.acquire()
                del _User_Pings[player] #This player quit, remove them from pings.
                _User_Pings_Lock.release()

        elif message == '_ping_': #Keepalive ping
            _User_Pings_Lock.acquire()
            _User_Pings[player] = time.time()
            _User_Pings_Lock.release()
            logger.write_line("Got a ping from <%s>"%player)
            

class PlayerOutput(threading.Thread): #Thread sends players their messages from queue.
    def __init__(self, name, connection):
        """
        queue:  The queue of messages to be sent to the player
        port:   The port that the player is listening on
        name:   The name of the player
        """
        threading.Thread.__init__(self)
        self.name = name
        self.connection = connection

        
    def run(self):

        global _Player_OQueues
        global _Player_OQueues_Lock
        global _Shutdown
        global _Shutdown_Lock
        
        logger.write_line("Beginning output thread for <%s>" % self.name)
        _Shutdown_Lock.acquire()
        done = _Shutdown
        _Shutdown_Lock.release()
        while not done:

            try:
                _Player_OQueues_Lock.acquire()
                message = _Player_OQueues[self.name].get()
                _Player_OQueues_Lock.release()
                logger.write_line("Got a message for the player %s: %s" % (self.name, message))
            except:
                logger.write_line("No messages for %s found in queue" % self.name)
                pass
            
            if message != "" and message != 'Error, it appears this person has timed out.':
                print message
                logger.write_line('Sending message to <%s>: "%s"'%(self.name, message))
                RAProtocol.sendMessage(message, self.connection)
                
            elif message == 'Error, it appears this person has timed out.':
                logger.write_line('Failed to either connect or send a message to <%s> after timeout.'%player)
                RAProtocol.sendMessage(message, self.connection)
                
            _Shutdown_Lock.acquire()
            done = _Shutdown
            _Shutdown_Lock.release()

            time.sleep(0.05)
            

class PlayerTimeout(threading.Thread): #Thread for checking if and handling when players time out.
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
        global _Shutdown
        global _Shutdown_Lock
        
        timeout = 15
        to_rem = []
        
        _Shutdown_Lock.acquire()
        done = _Shutdown
        _Shutdown_Lock.release()
        
        while not done:
            _User_Pings_Lock.acquire()
            for person in to_rem:
                del _User_Pings[person]
                _Player_OQueues_Lock.acquire()
                del _Player_OQueues[person]
                _Player_OQueues_Lock.release()
                _Player_Connections_Lock.acquire()
                del _Player_Connections[person]
                _Player_Connections_Lock.release()
                _Client_Connections_Lock.acquire()
                del _Client_Connections[person]
                _Client_Connections_Lock.release()
                
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
                    try:
                        _Player_OQueues[player].put('Error, it appears this person has timed out.')
                    except:
                        pass
                    _Player_OQueues_Lock.release()
            _User_Pings_Lock.release()
            _Shutdown_Lock.acquire()
            done = _Shutdown
            _Shutdown_Lock.release()
            time.sleep(0.05)

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
        global _Shutdown_Lock
        global _Shutdown
        
        _Shutdown_Lock.acquire()
        done = _Shutdown
        _Shutdown_Lock.release()
        
        while not done:
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
                        _Player_Loc_Lock.acquire()
                        _Player_Locations[player] = world #Route this players messages to that world
                        _Player_Loc_Lock.release()

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
                    
                _Shutdown_Lock.acquire()
                done = _Shutdown
                _Shutdown_Lock.release()
                    
                time.sleep(0.05)
                
            else:
                _Shutdown_Lock.acquire()
                doen = _Shutdown
                _Shutdown_Lock.release()
                time.sleep(0.05)
            
            
if __name__ == "__main__":
    main()
