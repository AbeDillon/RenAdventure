__author__ = 'ADillon'

import socket, sys
import thread, threading, Queue
import time, random
import RAProtocol
import engine

_Host = socket.gethostname() # replace with actual host address

_Game_State = {} # (mutex controlled)
_Game_State_Lock = threading.RLock()

_CMD_Queue = Queue.Queue() # Queue of NPC and Player commands

_Players = {} # (mutex controlled)
# key = (string)Player_Name : val = (player_object)
_Players_Lock = threading.RLock()

_Player_OQueues = {} # (mutex controlled)
# key = (string)Player_Name : val = (Queue)Output_Queue
_Player_OQueues_Lock = threading.RLock()

_Player_States = {} # (mutex controlled)
# key = (string)Player_Name : val = (Game State)Instanced Game_State
_Player_States_Lock = threading.RLock()

# We may want to keep track of threads
_Threads = [] # mutex controlled
_Threads_Lock = threading.RLock()

def main():
    """

    """
    # Load Game Files
    print "Game loaded"

    # Initialize _Game_State
    global _Game_State
    global _Game_State_Lock

    print "Game State initialized"

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

    # Spin-off NPC Spawning thread

    # Spin-off Item Spawning thread

    # Start Main Loop
    print "Entering main loop..."
    while 1:
        try:
            player, command = _CMD_Queue.get()
            print "player: " + player + "\n command: " + command
            executeCMD(player, command)
        except:
            pass

def executeCMD(player, command):
    """

    """


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

    def __init__(self, listen_port=1000, spawn_port=1001, host=''):
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

        sock.bind((self.host, self.listen_port))
        print "Login Socket bound"

        # Listen for new connections
        sock.listen(10)
        print "Login socket listening"
        while 1:
            # wait to accept a connection
            conn, addr = sock.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])

            thread.start_new_thread(self.addPlayer, (conn, addr))

    def addPlayer(self, conn, addr):
        """
        Add a new player to the game
        """
        # receive message
        player_name = RAProtocol.receiveMessage(conn)

        print "Adding " + player_name + " to the game."

        # *load player object (to be added, create default player for now)
        player_obj = []

        # *create player state and add to _Player_States (to be added)
        # add new player I/O queues
        oqueue = Queue.Queue()

        _Player_OQueues_Lock.acquire()
        _Player_OQueues[player_name] = oqueue
        _Player_OQueues_Lock.release()

        # Get I/O port
        self.spawn_port_lock.acquire()
        port = self.spawn_port
        self.spawn_port += 1
        self.spawn_port_lock.release()

        # spin off new PlayerI/O threads
        ithread = PlayerInput(port, player_name)
        othread = PlayerOutput(oqueue, addr, port, player_name)

        _Threads_Lock.acquire()
        _Threads.append(ithread)
        _Threads.append(othread)
        _Threads_Lock.release()

        # send new I/O ports to communicate on
        message = str(port)
        RAProtocol.sendMessage(message, conn)

        # add player to _Players
        _Players_Lock.acquire()
        _Players[player_name] = player_obj
        _Players_Lock.release()

        conn.close()


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
        # Create Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((self.host, self.port))

        # Listen for connection
        sock.listen(10)

        while 1:
            conn, addr = sock.accept()
            print 'got input from ' + self.name

            thread.start_new_thread(self.handleInput, (self, conn))

    def handleInput(self, conn):
        """
        Receive input, parse the message*, and place it in the correct queue*

        * message parsing and separate queuing will be implemented if the chat
        input and game input share a port
        """

        # receive message
        message = RAProtocol.receiveMessage(conn)

        # add it to the queue
        try:
            _CMD_Queue.put((self.name, message))
        except:
            pass

        conn.close()

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
        self.host = host

    def run(self):
        """
        poll output queue and send messages to player
        """
        while 1:
            # Listen to Output Queue
            try:
                # get message
                message = self.queue.get()
                # Create Socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect to player
                sock.connect((self.address[0], self.port))
                # send message
                RAProtocol.sendMessage(message, sock)
                # close connection
                sock.close()
            except:
                # this should handle exceptions
                pass

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