__author__ = 'ADillon'

import socket
import sys
import msvcrt
import thread, threading
import time
import string
import Queue
import RAProtocol
import logging

logging.basicConfig(filename='RenClient.log', level=logging.DEBUG, format = '%(asctime)s: %(message)s', datefmt = '%m/%d/%Y %I:%M:%S %p')

_Local_Host = socket.gethostname() # replace with actual host address
_Server_Host = socket.gethostname() #'10.245.50.150' # replace with actual server address
_Login_Port = 60005

_CMD_Queue = Queue.Queue()

_Quit = False
_Quit_Lock = threading.RLock()

def main():
    """

    """
    # start getting keyboard input
    global _CMD_Queue

    # try to log into the server and acquire a port
    ports = LogIn()
    rlt = ReadLineThread()
    rlt.start()

    ports = ports.split()

    # spin off I/O threads
    it = InThread(int(ports[1]))
    it.start()

    ot = OutThread(int(ports[0]))
    ot.start()

    kat = KeepAliveThread()
    kat.start()

    # wait for quit
    global _Quit
    global _Quit_Lock

    quit_game = False
    while not quit_game:
        _Quit_Lock.acquire()
        quit_game = _Quit
        _Quit_Lock.release()
        time.sleep(0.05)

    return True

def LogIn():
    """

    """
    global _CMD_Queue

    rank_list = {'Obama':0, 'Kanye':0, 'OReilly':0, 'Gottfried':0, 'Burbiglia':0}
    used_ranks = [5, 4, 3, 2, 1]
    ports = None
    while ports == None:

        line1 = raw_input('Please enter your username:\r\n') #Name
        logging.debug('Output: Please enter your username:')
        logging.debug('Input: %s' % line1)
        line2 = raw_input('Please enter your password:\r\n') #Pass
        logging.debug('Output: Please enter your password:')
        logging.debug('Input: %s' % line2)
        line = line1 + ' ' + line2
        if line != "":
            
            ports = connect_to_server(line)
            if ports == 'invalid': #Failed login
                logging.debug('Output: Error, failed to log in. Please try again')
                print >>sys.stdout, 'Error, failed to log in. Please try again'
                ports = None
            elif ports == 'banned_name': #Invalid username
                logging.debug('Output: Error, illegal player name. Please choose an appropriate name.')
                print >>sys.stdout, 'Error, illegal player name. Please choose an appropriate name.'
                ports = None
            elif ports == 'affiliation_get': #Get user affiliation set
                print >>sys.stdout, 'This is a new player, which requires you to rank your affiliation with people.'
                logging.debug('Output: This is a new player, which requires you to rank your affiliation with people.')
                print >>sys.stdout, 'Please rank the following people 1 through 5 in order of preference:'
                logging.debug('Output: Please rank the following people 1 through 5 in order of preference:')
                for person in rank_list:
                    print >>sys.stdout, '\t'+person

                for person in rank_list:
                    while 1:
                        rank = raw_input('On a scale of 1 to 5, where would you rank %s?\r\n'%person)
                        logging.debug('Output: On a scale of 1 to 5, where would you rank %s?\r\n' % person)
                        logging.debug('Input: %s' % rank)
                        rank = int(rank)
                        if rank in used_ranks: #This is okay
                            rank_list[person] = rank
                            used_ranks.remove(rank)
                            break
                        else:
                            print >>sys.stdout, 'Sorry, you may only give each person a different ranking'
                            logging.debug('Output: Sorry, you may only give each person a different ranking')
                for person in rank_list:
                    line = line+' '+person+' '+str(rank_list[person]) #Add all the people and their ranking to line

                ports = connect_to_server(line) #Re-send data with attached affiliation set

                
                    
            else:
                logging.debug('Hidden: Connection to server made, connecting on ports %s' % ports)


    print >>sys.stdout, "\nLogged in"
    logging.debug('Output: Logged in.')

    return ports

def connect_to_server(line):
    """

    """
    global _Server_Host
    global _Login_Port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((_Server_Host, _Login_Port))

    RAProtocol.sendMessage(line, sock)
    logging.debug('Hidden: Making connection with remote server')

    message = RAProtocol.receiveMessage(sock)

    sock.close()

    return message

class KeepAliveThread(threading.Thread):
    """

    """
    def run(self):
        """

        """
        global _CMD_Queue
        start_time = time.time()

        signal_time = 5
        _Quit_Lock.acquire()
        done = _Quit
        _Quit_Lock.release()
        while not done:
            if time.time()-start_time >= signal_time: #We send a keepalive signal.
                _CMD_Queue.put('_ping_')
                start_time = time.time()
                _Quit_Lock.acquire()
                done = _Quit
                _Quit_Lock.release()
            time.sleep(0.05)
                

class ReadLineThread(threading.Thread):
    """

    """

    def run(self):
        """

        """
        global _CMD_Queue
        global _Quit
        _Quit_Lock.acquire()
        done = _Quit
        _Quit_Lock.release()
        while not done:
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
                _CMD_Queue.put(line)
                if line != '':
                    logging.debug('Input from user: %s' % line)
            except:
                pass
            _Quit_Lock.acquire()
            done = _Quit
            _Quit_Lock.release()

class InThread(threading.Thread):
    """

    """

    def __init__(self, port):
        """

        """
        threading.Thread.__init__(self)
        global _Local_Host
        self.port = port
        self.host = _Local_Host

    def run(self):
        """

        """
        global _Quit
        # Create Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((self.host, self.port))

        # Listen for connection
        sock.listen(2)
        _Quit_Lock.acquire()
        done = _Quit
        _Quit_Lock.release()
        while not done:
            conn, addr = sock.accept()

            logging.debug('Hidden: Got connection from %s' % str(addr))
            #print 'got input from ' + self.name

            thread.start_new_thread(self.handleInput, (conn, ))
            time.sleep(0.05)
            _Quit_Lock.acquire()
            done = _Quit
            _Quit_Lock.release()


    def handleInput(self, conn):
        """

        """
        message = RAProtocol.receiveMessage(conn)
        logging.debug('Hidden: Got the following message from the server: "%s"' % message)
        conn.close()

        print >>sys.stdout, "\n" + message
        logging.debug('Output: %s' % message)

        return True

class OutThread(threading.Thread):
    """

    """
    def __init__(self, port):
        """

        """
        threading.Thread.__init__(self)
        global _Server_Host
        self.port = port
        self.host = _Server_Host

    def run(self):
        """

        """
        global _CMD_Queue
        global _Quit
        global _Quit_Lock
        _Quit_Lock.acquire()
        done = _Quit
        _Quit_Lock.release()
        while not done:
            message = ""
            # Listen to Output Queue
            try:
                # get message
                message = _CMD_Queue.get()

            except:
                pass

            if message != "":
                # Create Socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect to player
                sock.connect((self.host, self.port))
                # send message
                RAProtocol.sendMessage(message, sock)
                logging.debug('Hidden: Sending message "%s" to server' % message)
                # close connection
                sock.close()
                # check for quit
                if message.lower() == "quit":
                    _Quit_Lock.acquire()
                    _Quit = True
                    _Quit_Lock.release()

            done = _Quit
            time.sleep(0.05)

if __name__ == "__main__":
    main()
    logging.debug('Output: Game quit. Please close the program.')        
    sys.exit('Game quit. Please close the program.') 
