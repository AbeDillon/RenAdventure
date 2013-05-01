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

_Local_Host = socket.gethostbyname(socket.gethostname()) # replace with actual host address
_Server_Host = socket.gethostname() #'54.244.118.196' # replace with actual server address
_Login_Port = 8080
_Receive_Port = 8888

_CMD_Queue = Queue.Queue()

_Quit = False
_Quit_Lock = threading.RLock()

_Sound_Playing = False

def main():
    global _CMD_Queue
    global _Server_Host
    global _Login_Port
    global _Local_Host
    logger.write_line("Beginning client operations")
    
    it = InThread() #Start listening on port 8888 for connections
    it.start()
    logger.write_line("Beginning in port watching thread.")
    
    rank_list = {'Obama':0, 'Kanye':0, 'OReilly':0, 'Gottfried':0, 'Burbiglia':0}
    used_ranks = [5, 4, 3, 2, 1]
    
    #First get whether the user wishes to log in, or register.
    while 1: #Control loop for initial stages of user interaction prior to the actual connection being made
        choice = raw_input("Would you like to register, or login, or quit?\r\n")
        logger.write_line("Output: Would you like to register, or login, or quit?")
        logger.write_line("Input: %s" % choice)
        if choice == 'register': #Do registration
            uname = raw_input("Please enter a username you would like to use:\r\n")
            logger.write_line("Output: Please enter a username you would like to use:")
            logger.write_line("Input: %s" % uname)
            
            password = raw_input("Please enter a password you would like to use:\r\n")
            logger.write_line("Output: Please enter a password you would like to use:")
            if password != '': #We got one.
                logger.write_line("Input: User entered a password.")
                
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem')
            ssl_sock.connect((_Server_Host, _Login_Port))
            logger.write_line("Hidden: Connection to server made successfully")
            line = uname+' '+password+' '+'_register_'
            RAProtocol.sendMessage(line, ssl_sock) #Send the command to the server.
            logger.write_line("Hidden: Sending message to the server: %s" % line)
            response = RAProtocol.receiveMessage(ssl_sock) #Get the response
            logger.write_line("Hidden: Getting response from the server: %s" % resposne)
            if response == '_affiliation_get_': #They want our affiliation.
            
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
                
                RAProtocol.sendMessage(line, ssl_sock) #Send our response about the affiliation
                logger.write_line("Hidden: Sending message to server: %s" % line)
                resp = RAProtocol.receiveMessage(ssl_sock) #Receive the response from the server.
                logger.write_line("Hidden: Response from server: %s" % resp)
                if resp == "_get_ip_": #They want the IP we are at so they can make a connection to us, yay.
                    RAProtocol.sendMessage(_Local_Host, ssl_sock) #Send them our IP
                    logger.write_line("Hidden: Sending our IP to the server: %s" % _Local_Host)
                    resp = RAProtocol.receiveMessage(ssl_sock) #Get the last message back
                    logger.write_line("Hidden: Got response from server: %s" % resp)
                    
                    if resp == '_out_conn_made_': #We completed the connection and login process, horray.
                        logger.write_line("Hidden: Incoming connection from server completed, ending inbound processing on this socket")
                        break
                    else: #There was an error!
                        print >>sys.stdout, "Sorry, trouble connecting to the server. Please try again in a moment."
                    
            elif response != '_affiliation_get_': #We picked register and they don't want our affiliation? We were probably rejected then.
                print >>sys.stdout, "Registration failed: %s" % response
                
        elif choice == 'login': #Do the login proceedure.  
            uname = raw_input("Please enter a username you would like to use:\r\n")
            logger.write_line("Input: Attempting to log in with username <%s>" % uname)
            password = raw_input("Please enter a password you would like to use:\r\n")
            logger.write_line("Input: Got password to try. Testing.")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem')
            ssl_sock.connect((_Server_Host, _Login_Port))
            logger.write_line("Hidden: Connected to the server.")
            
            line = uname+' '+password+' '+'_login_'
            time.sleep(1.0) #Sleep before sending this one, to ensure they have time to get it?
            RAProtocol.sendMessage(line, ssl_sock) #Send the command to the server.
            logger.write_line("Hidden: Sending message with uname/pass to server.")
            response = RAProtocol.receiveMessage(ssl_sock) #Get the response
            logger.write_line("Hidden: Got the following reponse from the server: %s" % response)
            if response == '_invalid_': #They provided a wrong username/password combination.
                print >>sys.stdout, "Log in failed, incorrect username or password"
                logger.write_line("Output: Log in failed, incorrect username or password")
            elif response == '_requires_registration_': #They provided a username/password which is not registered
                print >>sys.stdout, "Log in failed, that is not a registered account"
                logger.write_line("Output: Log in failed, that is not a registered account")
            elif response == "_get_ip_": #They want our IP to connect to us, this is good.
                logger.write_line("Hidden: Server is requesting our IP.")
                RAProtocol.sendMessage(_Local_Host, ssl_sock) #Send them our IP
                logger.write_line("Hidden: Sending server the following IP: %s" % _Local_Host)
                response = RAProtocol.receiveMessage(ssl_sock) #Get their response
                logger.write_line("Hidden: Got the following response from the server: %s" % response)
                if response == '_out_conn_made_': #We completed the connection and login process.
                    logger.write_line("Hidden: Incoming connection from the server completed, ending inbound processing on this socket")
                    
                    ot = OutThread(ssl_sock) #Give it the connection to keep sending outgoing data on.
                    logger.write_line("Hidden: Beginning run of OutThread.")
                    ot.start()
                        
                    kat = KeepAliveThread()
                    logger.write_line("Hidden: Beginning run of KeepAliveThread")
                    kat.start()
                    
                    rlt = ReadLineThread()
                    logger.write_line("Hidden: Beginning ReadLineThread")
                    rlt.start()
                    break
                else: #Anything else
                    print >>sys.stdout, "Sorry, trouble connecting to the server. Please try again in a moment."
                    logger.write_line("Sorry, trouble connecting to the server. Please try again in a moment.")
                    
        elif choice == 'quit': #They are quitting the program.
            logger.write_line("Input: %s" % choice)
            logger.write_line("Hidden: User Qutting.")
            return True
        
    quit_game = False
    while not quit_game:
        _Quit_Lock.acquire()
        quit_game = _Quit
        _Quit_Lock.release()
        time.sleep(0.05)

    return True
    
def play_sound(sound):
    global _Sound_Playing
    path = 'sounds/%s.wav' % sound
        
    winsound.PlaySound(path, winsound.SND_FILENAME)
    _Sound_Playing = False
    return True
    
class KeepAliveThread(threading.Thread):


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
                logger.write_line("Sending a _ping_ to server.")
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
    def __init__(self):
        global _Receive_Port
        global _Local_Host
        global _Quit_Lock
        global _Quit
        
        threading.Thread.__init__(self)
        
    def run(self):
        done = False

        #Do things
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((_Local_Host, _Receive_Port)) #Bind here
        
        sock.listen(2)
        while not done:
            conn, addr = sock.accept()
            logger.write_line('Hidden: Got connection from %s' % str(addr))
            #print 'got input from ' + self.name
            connstream = ssl.wrap_socket(conn, certfile = 'cert.pem', server_side = True)
            logger.write_line("Hidden: Handling new connection")
            thread.start_new_thread(self.handleConnection, (connstream, ))
            time.sleep(0.05)
            _Quit_Lock.acquire()
            done = _Quit
            _Quit_Lock.release()
            
    def handleConnection(self, connection): #Just keep polling the connection for messages, when we get one we act with it.
        global _Sound_Playing
        done = False
        while not done: 
            message = ''
            try:
                message = RAProtocol.receiveMessage(connection) #Try getting a message from them.
                logger.write_line("Hidden: Got a message! %s" % message)
                
            except:
                pass #When you don't get anything.
                
            if message != '': #Non-blank message, we got data.
                logger.write_line('Hidden: Got the following message from the server: "%s"'%message)
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
                    
            time.sleep(1.0)

        return True

class OutThread(threading.Thread):

    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.connection = connection #A connection to the server.
        
    def run(self):
        global _Quit
        global _Quit_Lock
        global _CMD_Queue
        done = False
        while not done:
            message = ""
            # Listen to Output Queue
            try:
                # get message
                message = _CMD_Queue.get()

            except:
                pass

            if message != "":
            
                RAProtocol.sendMessage(message, self.connection)
                logger.write_line('Hidden: Sending message "%s" to server' % message)
                
                if message.lower() == "quit":
                    _Quit_Lock.acquire()
                    _Quit = True
                    _Quit_Lock.release()
            _Quit_Lock.acquire()
            done = _Quit
            _Quit_Lock.release()
            
            time.sleep(0.05)
        

if __name__ == "__main__":
    main()      
    logger.write_line('Output: Game quit. Please close the program')
    logger.shutdown()
    sys.exit('Game quit. Please close the program.') 
