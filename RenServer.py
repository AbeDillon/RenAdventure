__author__ = 'ADillon, MNutter'

import socket, sys
import thread, threading, Queue
import time, random
import RAProtocol
import engine
import os
#import msvcrt
import string
import loader
import ssl
import Q2logging

logger = Q2logging.out_file_instance('logs/server/RenServer')

# _Player_Locations = {} #{playername: location} where location is "Lobby" or the name of a running world instance? ###IP
# _Player_Loc_Lock = threading.RLock() #Lock for player locations dict. ###IP

_Host = socket.gethostbyname(socket.gethostname()) # replace with actual host address

_CMD_Queue = Queue.Queue() # Queue of NPC and Player commands

#_Lobby_Queue = Queue.Queue() #Queue of Player chatting/commands for lobby? ###IP

_MSG_Queue = Queue.Queue()

_Players = [] # (mutex controlled)
# key = (string)Player_Name : val = (player_object)
_Players_Lock = threading.RLock()

_Player_OQueues = {} # (mutex controlled)
# key = (string)Player_Name : val = (Queue)Output_Queue
_Player_OQueues_Lock = threading.RLock()

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

_Server_Queue = Queue.Queue()

def main():
    """

    """
    global _Logger
    # Initialize _Game_State
    engine.init_game()

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

    #rlt = ReadLineThread()
    #rlt.start()

    #print "Server console input thread spawned"
    #logger.write_line('Server console input thread spawned')

    sat = ServerActionThread()
    sat.start()

    print 'Server action thread spawned'
    logger.write_line('Server action thread spawned')


    timeout = PlayerTimeout()
    timeout.start()
    print 'Player timeout thread spawned'
    logger.write_line('Player timeout thread spawned')
    
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
            engine.put_commands([command])

        messages = engine.get_messages()

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
            _Player_OQueues[player].put(text)

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
        # receive message
        logged_in = False
        input_data = RAProtocol.receiveMessage(conn)
        a_string = input_data.split() #Split on space
        player_name = a_string[0]
        player_pass = a_string[1]
        player_affil = {} #Current player's affiliation data.

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
                    player_path = 'players/%s.xml'%player_name
                    try:
                        person = loader.load_player(player_path)
                    except:
                        logger.write_line("Error loading player file %s, file does not exist" % player_path)
                        print "Error loading player file %s, file does not exist" % player_path
                    player_affil = person.affiliation #Load in the players affiliation
                    location = person.coords
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
                
            if logged_in:

                _User_Pings[player_name] = time.time()
                if player_affil != {}: #Blank dict:
                # *load player object (to be added, create default player for now)
                    engine.make_player(player_name, location, player_affil)

                else: #Player did not provide an affiliation?
                    engine.make_player(player_name, location) #Blank affiliation, use default?


                # *create player state and add to _Player_States (to be added)
                # add new player I/O queues
                oqueue = Queue.Queue()
                oqueue.put(engine.engine_helper.get_room_text(player_name, location))  #####NEED FILTER

                _Player_OQueues_Lock.acquire()
                _Player_OQueues[player_name] = oqueue
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
        #global _Lobby_Queue
        # receive message
        message = RAProtocol.receiveMessage(conn)

        if message != '_ping_':

            # add it to the queue
            if message != 'quit':
                # _Player_Loc_Lock.acquire() ###IP
                # location = _Player_Locations.get(self.name, 'lobby') #Get whether player is in "Lobby" or a world? ###IP
                # _Player_Loc_Lock.release() ###IP
                
                # if location == 'lobby': #Player is in the lobby ###IP
                    # try:
                        # _Lobby_Queue.put((self.name, message))
                    # except:
                        # pass
                # elif location == 'world1': #Player is in the game instance known as world1 ###IP
                    # try:
                        # _CMD_Queue.put((self.name, message))
                        # logger.write_line('Putting in the command queue: <%s>; "%s"'%(self.name, message))
                    # except:
                        # pass
                        
                        
                try:
                    _CMD_Queue.put((self.name, message))
                    logger.write_line('Putting in the command queue: <%s>; "%s"' % (self.name, message))
                except:
                    pass

                conn.close()

            elif message == 'quit':#User is quitting, we can end this thread
                _InThreads[self.name] = False
                _OutThreads[self.name] = False
                _Logged_in.remove(self.name)
                logger.write_line('Removing <%s> from _Logged_in' % self.name)
                engine.remove_player(self.name) #Remove player existence from gamestate.

        elif message == '_ping_': #Keepalive ping
            _User_Pings[self.name] = time.time()
            logger.write_line("Got a ping from <%s>"%self.name)

class PlayerTimeout(threading.Thread): #Thread to handle players who time-out

    def run(self):
        global _Logged_in
        global _InThreads
        global _OutThreads
        global _Logger
        global _User_Pings
        global _Player_OQueues_Lock
        global _Player_OQueues

        timeout = 15
        to_rem = []
        while 1:
            for person in to_rem:
                del _User_Pings[person]
            to_rem = []
            for player in _User_Pings:
                if time.time() - _User_Pings[player] > timeout: #This client has timed out
                    print 'Player timed out: <%s>' % player
                    logger.write_line('Removing <%s> from game: Timed out' % player)
                    engine._Characters_Lock.acquire()
                    if player in engine._Characters:
                        engine.remove_player(player)
                    engine._Characters_Lock.release()
                    if player in _Logged_in:
                        _Logged_in.remove(player)
                    to_rem.append(player)
                    _Player_OQueues_Lock.acquire()
                    _Player_OQueues[player].put('Error, it appears this person has timed out.')
                    _Player_OQueues_Lock.release()

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


# class ReadLineThread(threading.Thread):
    # """

    # """

    # def run(self):
        # """

        # """
        # global _Server_Queue
        # while True: #What would cause this to stop? Only the program ending.
            # line = ""
            # while 1:
                # char = msvcrt.getche()
                # if char == "\r": # enter
                    # break

                # elif char == "\x08": # backspace
                    # # Remove a character from the screen
                    # msvcrt.putch(" ")
                    # msvcrt.putch(char)

                    # # Remove a character from the string
                    # line = line[:-1]

                # elif char in string.printable:
                    # line += char

                # time.sleep(0.01)

            # try:
                # _Server_Queue.put(line)
                # if line != '':
                    # _Logger.debug('Input from server console: %s' % line)
            # except:
                # pass

class ServerActionThread(threading.Thread):
    """

    """
    def run(self):
        """

        """
        global _Server_Queue
        global _CMD_Queue
        done = False
        while not done:
            command = ''
            try:
                command = _Server_Queue.get()
            except:
                pass

            if command != '': #We got something
                if command.lower() == 'quit':
                    print 'Got quit, shutting down server.'
                    done = True
                    engine.shutdown_game()
                    break
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

if __name__ == "__main__":
    main()

