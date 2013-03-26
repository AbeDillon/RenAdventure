__author__ = 'ADillon'

import socket
import sys
import msvcrt
import thread, threading
import time
import string
import Queue
import RAProtocol

_Host = socket.gethostname() # replace with actual host address
_Login_Port = 1000

_CMD_Queue = Queue.Queue()

_Quit = False
_Quit_Lock = threading.RLock()

def main():
    """

    """
    # start getting keyboard input
    global _CMD_Queue
    rlt = ReadLineThread()
    rlt.start()

    # try to log into the server and acquire a port
    port = LogIn()

    # spin off I/O threads
    it = InThread(port)
    it.start()

    ot = OutThread(port)
    ot.start()

    # wait for quit
    global _Quit
    global _Quit_Lock

    quit_game = False
    while not quit_game:
        _Quit_Lock.acquire()
        quit_game = _Quit
        _Quit_Lock.release()

def LogIn():
    """

    """
    global _CMD_Queue

    print >>sys.stdout, "What is your name?"
    port = None
    while port == None:
        empty_queue = _CMD_Queue.qsize()

        try:
            line = _CMD_Queue.get()
            port = connect_to_server(line)
        except:
            port = None

        if (port == None) and (empty_queue != 0):
            print >>sys.stdout, "Invalid name, try again."

    return port

def connect_to_server(line):
    """

    """
    global _Host
    global _Login_Port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((_Host, _Login_Port))

    RAProtocol.sendMessage(line, sock)

    message = RAProtocol.receiveMessage(sock)

    try:
        port = int(message)

    except:
        port = None

    return port

class ReadLineThread(threading.Thread):
    """

    """

    def run(self):
        """

        """
        global _CMD_Queue

        while 1:
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

            try:
                _CMD_Queue.put(line)
            except:
                pass

class InThread(threading.Thread):
    """

    """

    def __init__(self, port):
        """

        """
        threading.Thread.__init__(self)
        global _Host
        self.port = port
        self.host = _Host

    def run(self):
        """

        """
        # Create Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((self.host, self.port))

        # Listen for connection
        sock.listen(10)

        while 1:
            conn, addr = sock.accept()
            print 'got input from ' + self.name

            thread.start_new_thread(self.handleInput, (conn, ))


    def handleInput(self, conn):
        """

        """
        message = RAProtocol.receiveMessage(conn)

        print >>sys.stdout, message

class OutThread(threading.Thread):
    """

    """
    def __init__(self, port):
        """

        """
        threading.Thread.__init__(self)
        global _Host
        self.port = port
        self.host = _Host

    def run(self):
        """

        """
        global _CMD_Queue
        while 1:
            # Listen to Output Queue
            try:
                # get message
                message = _CMD_Queue.get()
                # Create Socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect to player
                sock.connect((self.host, self.port))
                # send message
                RAProtocol.sendMessage(message, sock)
                # close connection
                sock.close()
                # check for quit
                if message.lower() == "quit":
                    global _Quit
                    global _Quit_Lock

                    _Quit_Lock.acquire()
                    _Quit = True
                    _Quit_Lock.release()

            except:
                # this should handle exceptions
                pass

if __name__ == "__main__":
    main()
