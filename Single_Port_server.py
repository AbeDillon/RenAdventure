__author__ = 'ADillon, MNutter'

import socket, sys
import thread, threading, Queue
import time, random
import RAProtocol
import engine_classes
import os
#import msvcrt
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

_Player_Connections = {} #player_name -> conn #Incoming
_Player_Connections_Lock = threading.RLock()

_Client_Connections = {} #Outgoing
_Client_Connections_Lock = threading.RLock() 

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
    
    pi = PlayerInput()
    logger.write_line("Player input thread spawned.")
    pi.start()
    
    po = PlayerOutput()
    logger.write_line("Player output thread spawned.")
    po.start()
    
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
        while 1:
            # wait to accept a connection
            conn, addr = sock.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            logger.write_line('Connected with '+str(addr[0])+':'+str(addr[1]))
            connstream = ssl.wrap_socket(conn, certfile = 'cert.pem', server_side = True) 
            start_dialogue = RAProtocol.receiveMessage(connstream)
            logger.write_line("Got start_dialogue: %s" % start_dialogue) ###DEBUG
            a_string = start_dialogue.split() #Split on space
            player_name = a_string[0]
            player_pass = a_string[1]
            flag = a_string[2] #Flag for either "_login_" to attempt to login, or "_register_" to attempt to register?
            if flag == '_login_': #Try and log them in
                print "Player wishes to log in as <%s>, verifying.." % player_name
                logger.write_line("Player wishes to log in as <%s>, verifying..." % player_name)
                proceed = self.verify_player(player_name, player_pass, connstream)
                if proceed: #This is a valid player, we have a registration for them.
                    _Player_Connections_Lock.acquire()
                    _Player_Connections[player_name] = connstream
                    _Player_Connections_Lock.release() #We now have this player in the game.
                    
            elif flag == '_register_': #Attempt to register them based on the data
                print "Player wishes to register as <%s>, proceeding.." % player_name
                logger.write_line("Player wishes to register as <%s>, proceeding..." % player_name)
                proceed = self.register_player(player_name, player_pass, conn)
                if proceed: #Valid player, we have their registration now.
                    _Player_Connections_Lock.acquire()
                    _Player_Connections[name] = connstream
                    _Player_Connections_Lock.release()
                
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
        global _Client_Connections
        global _Client_Connections_Lock
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
                ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem') 
                try:
                    ssl_sock.connect((ip, 8888)) #Connect to client on port 8888 for sending messages
                    logger.write_line("Connected to socket.")
                    RAProtocol.sendMessage("_out_conn_made_", connection)
                    logger.write_line("Sent connection_made response to client.")
                    _Client_Connections_Lock.acquire()
                    logger.write_line("Acquired _Client_Connections_Lock")
                    _Client_Connections[name] = ssl_sock #Add the outbound socket to the outbound connections list.
                    logger.write_line("Stored the ssl_socket connection in the dictionary under %s" % name)
                    _Client_Connections_Lock.release()
                    logger.write_line("Released _Client_Connections_Lock")
                    
                except: 
                    RAProtocol.sendMessage("_connection_fail_", connection)
                    logger.write_line("Failed to connect")
                    
                
                
                _Player_OQueues_Lock.acquire()
                _Player_OQueues[name] = oqueue
                _Player_Loc_Lock.acquire()
                
                
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
        global _Client_Connections_Lock
        
    
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
            logger.write_line("Received a user affiliation.")
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
            
        else:
            RAProtocol.sendMessage("_reject_", connection)
            logger.write_line("User login attempt rejected")
            return False
            
        if logged_in:
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
            
            
            # *create player state and add to _Player_States (to be added)
            # add new player I/O queues
            oqueue = Queue.Queue()
            line = "\r\n"
            for world in _World_list:
                line += "\t"+world+"\r\n"
            
            oqueue.put("Welcome to the RenAdventure lobby!\r\nThe following worlds are available (type: join name_of_world):"+line) ###TEST
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
            ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem') 
            
            try:
                
                ssl_sock.connect((ip, 8888)) #Connect to client on port 8888 for sending messages
                logger.write_line("Connection to socket on port 8888 made.")
                RAProtocol.sendMessage("_out_conn_made_", ssl_sock)
                _Client_Connections_Lock.acquire()
                _Client_Connections[name] = ssl_sock #Add the outbound socket to the outbound connections list.
                _Client_Connections_Lock.release()
                
                _Player_OQueues_Lock.acquire()
                _Player_OQueues[name] = oqueue
                _Player_Loc_Lock.acquire()
                
            except:
                RAProtocol.sendMessage("_conn_failure_", ssl_sock)
                logger.write_line("Failed to connect.")
            
            return True 
            
            
            
        else:
            RAProtocol.sendMessage("_reject_", connection)
            logger.write_line("User log in rejected")
            return False
            
            
class PlayerInput(threading.Thread): #Thread polls connections for data and passes it to engine. FAILED. Need new one for each?
    def __init__(self):
        threading.Thread.__init__(self)
        
        
    def run(self):
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
        
        while 1:
            _Player_Connections_Lock.acquire()
            conn_temp = _Player_Connections
            _Player_Connections_Lock.release() #Now we have a list to work with.
            for player in conn_temp: #For each player, we want to try and receive on their connection then put that data in the cmd queue.
                connection = conn_temp[player] #Get the connection
                logger.write_line("Attempting to get data from connection associated with <%s>" % player)
                try:
                    input_data = RAProtocol.receiveMessage(connection)
                    logger.write_line("Got the following from the client: %s" % input_data)
                except:
                    input_data = ''
                    logger.write_line("Did not get any data for the client this time.")
                    
                if input_data != '': #We got something, yay
                    logger.write_line("Handling data from client")
                    self.handle_input(player, input_data)
                    
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
        
        logger.write_line("Handling message: %s" % message)
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
                        

                conn.close()

            elif message == 'quit':#User is quitting, we can end this thread
                _Logged_in.remove(name)
                logger.write_line('Removing <%s> from _Logged_in' % name)
                game_engine._Characters_Lock.acquire()
                if name in game_engine._Characters: #This player has been added to the game
                    game_engine.remove_player(name) #Remove player existence from gamestate.
                game_engine._Characters_Lock.release()
                _Player_Loc_Lock.acquire()
                if _Player_Locations[name] == 'lobby': #This person is in the lobby, tell everyone they quit.
                    _Player_OQueues_Lock.acquire()
                    for person in _Player_OQueues:
                        if person != name: #This is not the person quitting, tell them who quit.
                            _Player_OQueues[person].put("%s quit."%name)
                    _Player_OQueues_Lock.release()
                _Player_Loc_Lock.release()
                _Player_Connections_Lock.acquire()
                del _Player_Connections[name]
                _Player_Connections_Lock.release()
                _Client_Connections_Lock.acquire()
                del _Client_Connections[name]
                _Client_Connections_Lock.release()

        elif message == '_ping_': #Keepalive ping
            _User_Pings_Lock.acquire()
            _User_Pings[name] = time.time()
            _User_Pings_Lock.release()
            logger.write_line("Got a ping from <%s>"%name)
            

class PlayerOutput(threading.Thread): #Thread sends players their messages from queue.
    def __init__(self):
        """
        queue:  The queue of messages to be sent to the player
        port:   The port that the player is listening on
        name:   The name of the player
        """
        threading.Thread.__init__(self)

        
    def run(self):
        global _Client_Connections_Lock
        global _Client_Connections
        global _Player_OQueues
        global _Player_OQueues_Lock
        
        
        while 1:
            _Client_Connections_Lock.acquire()
            connection_list = copy(_Client_Connections)
            _Client_Connections_Lock.release()
            for player in _PlayerOQueues: #For each person in the output queue...
                logger.write_line("Attempting to send output to player %s" % player)
                connection = connection_list[player] #Get this person's connection (outbound)
                message = ''
                try:
                    _Player_OQueues_Lock.acquire()
                    message = _Player_OQueues[player].get()
                    _Player_OQueues_Lock.release()
                    logger.write_line("Got a message for the player")
                except:
                    logger.write_line("Did not get a message for the player.")
                    pass
                
                if message != "" and message != 'Error, it appears this person has timed out.':
                    print message
                    logger.write_line('Sending message to <%s>: "%s"'%(player, message))
                    RAProtocol.sendMessage(message, connection)
                    
                elif message == 'Error, it appears this person has timed out.':
                    logger.write_line('Failed to either connect or send a message to <%s> after timeout.'%player)
                    RAProtocol.sendMessage(message, connection)
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
        
        timeout = 15
        to_rem = []
        
        while 1:
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
            time.sleep(0.05)


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
                    
                time.sleep(0.05)
                
            else:
                time.sleep(0.05)
            

if __name__ == "__main__":
    main()
