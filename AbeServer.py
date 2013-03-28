__author__ = 'ADillon'

import socket, sys
import thread, threading, Queue
import time, random
import RAProtocol
import engine
import logging
import os

logging.basicConfig(filename='RenAdventure.log', level=logging.DEBUG, format = '%(asctime)s: %(message)s', datefmt = '%m/%d/%Y %I:%M:%S %p')

_Host = socket.gethostname() # replace with actual host address

_CMD_Queue = Queue.Queue() # Queue of NPC and Player commands

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

def main():
    """

    """
    # Initialize _Game_State
    engine.init_game()

    print "Game State initialized"
    logging.debug('Game State initialized')

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
    logging.debug('Log-in thread spawned')

    # Spin-off NPC Spawning thread

    # Spin-off Item Spawning thread

    # Start Main Loop
    print "Entering main loop..."
    logging.debug('Entering main loop...')
    #loop_cnt = 0
    while 1:
        command = None
        try:
            command = _CMD_Queue.get_nowait()
            print "player: " + command[0] + " command: " + command[1]
            line = '<player>: '+command[0]+' <command>: '+command[1]
            logging.debug('Processing Command from Queue: %s' % line)
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

    def __init__(self, listen_port=1000, spawn_port=2000, host=""):
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
        # Create a socket to listen for new connections
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Login Socket created"
        logging.debug('Login Socket created')

        sock.bind((self.host, self.listen_port))
        print "Login Socket bound"
        logging.debug('Login Socket bound')

        # Listen for new connections
        sock.listen(10)
        print "Login socket listening"
        logging.debug('Login socket listening')
        while 1:
            # wait to accept a connection
            conn, addr = sock.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            logging.debug('Connected with '+str(addr[0])+':'+str(addr[1]))


            thread.start_new_thread(self.addPlayer, (conn, addr))
            time.sleep(0.05)

    def addPlayer(self, conn, addr):
        """
        Add a new player to the game
        """
        # receive message
        logged_in = False
        input_data = RAProtocol.receiveMessage(conn)
        a_string = input_data.split() #Split on space
        player_name = a_string[0]
        player_pass = a_string[1]

        path = 'login_file/%s.txt' % player_name

        if os.path.exists(path): #This file exists
            fin = open(path)
            pwd = fin.readline()
            fin.close()

            if player_pass == pwd: #Login successful
                print 'User <%s> logged in' % player_name
                logged_in = True
            else:
                print 'User <%s> failed to authenticate.' % player_name
                RAProtocol.sendMessage('invalid', conn)
        else: #File does not exist
            fin = open(path, 'w')
            fin.write(player_pass)
            fin.close()
            logged_in = True
            
        if logged_in:
                


            # *load player object (to be added, create default player for now)
            engine.make_player(player_name, (0,0,1), {'Obama': 5, 'Kanye': 4, 'OReilly': 3, 'Gottfried': 2, 'Burbiglia': 1})


            # *create player state and add to _Player_States (to be added)
            # add new player I/O queues
            oqueue = Queue.Queue()
            oqueue.put(engine.get_room_text((0, 0, 1)))

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
            logging.debug('<'+player_name+'>'+" added to the game.")


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
                        
                logging.debug('Got input from: <%s>' % self.name)
                
                thread.start_new_thread(self.handleInput, (conn, ))
                time.sleep(0.05)
        if not _InThreads[self.name]: #We stopped the loop..
            print 'Input thread for player <%s> ending' % self.name
            logging.debug('Input thread for player <%s> ending' % self.name)
            del _InThreads[self.name] #So we delete the tracker for it.
    def handleInput(self, conn):
        """
        Receive input, parse the message*, and place it in the correct queue*

        * message parsing and separate queuing will be implemented if the chat
        input and game input share a port
        """
        global _InThreads
        # receive message
        message = RAProtocol.receiveMessage(conn)

        # add it to the queue
        try:
            _CMD_Queue.put((self.name, message))
            logging.debug('Putting in the command queue: <%s>; "%s"' % (self.name, message))
        except:
            pass

        conn.close()

        if message == 'quit':#User is quitting, we can end this thread
            _InThreads[self.name] = False

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
        while _OutThreads[self.name]:
            # Listen to Output Queue
            message = ""
            try:
                # get message
                message = self.queue.get()
            except:
                # this should handle exceptions
                pass
            if message != "":
                print message
                logging.debug('Sending message to <%s>: "%s"' %(self.name, message))
                if message == 'quit': #Replying to user quit message with a quit, we can stop this thread
                    _OutThreads[self.name] = False
                # Create Socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect to player
                sock.connect((self.address[0], self.port))
                # send message
                RAProtocol.sendMessage(message, sock)
                # close connection
                sock.close()
            time.sleep(0.05)
        if not _OutThreads[self.name]: #This thread will no longer be running...
            print 'Output thread for player <%s> ending.' % self.name
            logging.debug('Output thread for player <%s> ending.'%self.name)
            del _OutThreads[self.name] #So we delete the tracker for it.

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
