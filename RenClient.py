__author__ = 'ADillon, MNutter'

import socket
import sys
import msvcrt
import thread, threading
import time
import string
import Queue
import RAProtocol
import ssl
import winsound
import Q2logging


logger = Q2logging.out_file_instance('logs/client/RenClient')

_Local_Host = socket.gethostname() # replace with actual host address
_Server_Host = socket.gethostname() #'54.244.118.196' # replace with actual server address
_Login_Port = 60005

_CMD_Queue = Queue.Queue()

_Quit = False
_Quit_Lock = threading.RLock()

_Sound_Playing = False

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
        logger.write_line('Output: Please enter your username:')
        logger.write_line('Input: %s' % line1)
        line2 = raw_input('Please enter your password:\r\n') #Pass
        logger.write_line('Output: Please enter your password:')
        logger.write_line('Input: %s' % line2)
        
        line = line1 + ' ' + line2
        if line != "":
            
            ports = connect_to_server(line)
            if ports == 'invalid': #Failed login
                logger.write_line('Output: Error, failed to log in. Please try again')
                print >>sys.stdout, 'Error, failed to log in. Please try again'
                ports = None
            elif ports == 'banned_name': #Invalid username
                logger.write_line('Output: Error, illegal player name. Please choose an appropriate name.')
                print >>sys.stdout, 'Error, illegal player name. Please choose an appropriate name.'
                ports = None
            elif ports == 'affiliation_get': #Get user affiliation set
                print >>sys.stdout, 'This is a new player, which requires you to rank your affiliation with people.'
                logger.write_line('Output: This is a new player, which requires you to rank your affiliation with people.')
                print >>sys.stdout, 'Please rank the following people 1 through 5 in order of preference:'
                logger.write_line('Output: Please rank the following people 1 through 5 in order of preference:')
                for person in rank_list:
                    print >>sys.stdout, '\t'+person
                    logger.write_line(person)
                for person in rank_list:
                    while 1:
                        rank = raw_input('On a scale of 1 to 5, where would you rank %s?\r\n'%person)
                        logger.write_line('Output: On a scale of 1 to 5, where would you rank %s?\r\n' % person)
                        logger.write_line('Input: %s' % rank)
                        rank = int(rank)
                        if rank in used_ranks: #This is okay
                            rank_list[person] = rank
                            used_ranks.remove(rank)
                            break
                        else:
                            print >>sys.stdout, 'Sorry, you may only give each person a different ranking'
                            logger.write_line('Output: Sorry, you may only give each person a different ranking')
                for person in rank_list:
                    line = line+' '+person+' '+str(rank_list[person]) #Add all the people and their ranking to line

                ports = connect_to_server(line) #Re-send data with attached affiliation set

                
                    
            else:
                logger.write_line('Hidden: Connection to server made, connecting on ports %s' % ports)


    print >>sys.stdout, "\nLogged in"
    logger.write_line('Output: Logged in.')

    return ports

def connect_to_server(line):
    """

    """
    global _Server_Host
    global _Login_Port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem')
    ssl_sock.connect((_Server_Host, _Login_Port))

    RAProtocol.sendMessage(line, ssl_sock)
    logger.write_line('Hidden: Making connection with remote server')

    message = RAProtocol.receiveMessage(ssl_sock)

    ssl_sock.close()

    return message
def play_sound(sound):
    global _Sound_Playing
    path = 'sounds/%s.wav' % sound
        
    winsound.PlaySound(path, winsound.SND_FILENAME)
    _Sound_Playing = False
    return True
    
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
                    logger.write_line('Input from user: %s' % line)
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

            logger.write_line('Hidden: Got connection from %s' % str(addr))
            #print 'got input from ' + self.name
            connstream = ssl.wrap_socket(conn, certfile = 'cert.pem', server_side = True)
            thread.start_new_thread(self.handleInput, (connstream, ))
            time.sleep(0.05)
            _Quit_Lock.acquire()
            done = _Quit
            _Quit_Lock.release()


    def handleInput(self, conn):
        """

        """
        global _Sound_Playing
        message = RAProtocol.receiveMessage(conn)
        logger.write_line('Hidden: Got the following message from the server: "%s"'%message)
        conn.close()
        if '_play_'in message and not _Sound_Playing: 
        #Format from engine for a play sound message is: "_play_ soundname" where soundname is the name of a file you wish to play from the sounds directory
            message = message.split() #Split into _play_ and the sound name
            sound_name = message[1]
            _Sound_Playing = True ###To block other plays for now.
            thread.start_new_thread(play_sound, (sound_name,))
            logger.write_line('Output: Playing sound file called %s' % sound_name) 
            
        elif not '_play_' in message: #This isn't a playsound message, we can print it.
            print >>sys.stdout, "\n" + message.strip()
            logger.write_line('Output: %s' % message)

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
                ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem') 
                # connect to player
                ssl_sock.connect((self.host, self.port))
                # send message
                RAProtocol.sendMessage(message, ssl_sock)
                logger.write_line('Hidden: Sending message "%s" to server' % message)
                # close connection
                ssl_sock.close()
                # check for quit
                if message.lower() == "quit":
                    _Quit_Lock.acquire()
                    _Quit = True
                    _Quit_Lock.release()

            done = _Quit
            time.sleep(0.05)

if __name__ == "__main__":
    main()      
    logger.write_line('Output: Game quit. Please close the program')
    logger.shutdown()
    sys.exit('Game quit. Please close the program.') 
