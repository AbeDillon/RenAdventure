from socket import *
import thread
# Just a Test comment I am adding to test git/Aptana integration.
# connections & message lists
s_connections = []
r_connections = []
msg = []

HOST = gethostname()  #  Will only work on a single Computer right now.  Need to modify Host IP in client and server to distribute
#HOST = '172.16.248.42'
R_PORT = 8000   # Port to recieve data through maps to client S_PORT
S_PORT = 1234   # Port to send through maps to client R_PORT

# open receive socket
r= socket(AF_INET, SOCK_STREAM)  # Open Socket named r
r.bind((HOST, R_PORT)) # bind socket to Host and recieve port
r.listen(10) # listen for connections
print '\nServer Recieve socket is running and listening....'


# open send socket
s = socket(AF_INET, SOCK_STREAM) # open socket named s 
s.bind((HOST, S_PORT)) #  bind socket to host and send port
s.listen(10)  # listen for connections to send socket
print '\nServer Send socket running and listening....'

def receive_msg(r):
    # to recieve a message.
    while(1):
        data = r.recv(1024) #    data is msg received
        if not data:    # if not data. (ie disconnect)
            break
        else:
            msg.append(data)    #append data to end of msg list for queued re broadcast
            
            print '\n', data  # print data new line
            print ""
            thread.start_new_thread(send_msg, ())     #    Begin thread to send messages.

def send_msg():
    # Send messages in message list to the point no messsages remain in list
    while len(msg) > 0:
        
        for user in s_connections:   # for each user connected to send socket
            user.send(msg[0])   # send 1st message in list
        del msg[0] # delete message after being sent out to list of connections
        # start over with next message in list

while(1):
    
    # Handle attempted connections to send socket
    s_conn, s_addr = s.accept() #  Aceept connections
    s_connections.append(s_conn)    # append connection to list of connections
    #print "\nsend connection established with " + str(s_addr)
    
    # Handle attempted connections to receive socket    
    r_conn, r_addr = r.accept() # accept connections
    r_connections.append(r_conn)    # append connection to list 
    #print "\nreceive connection established with " + str(r_addr)
    
    thread.start_new_thread(receive_msg, (r_conn,)) # start a thread to recieve messages from the new connection
     
