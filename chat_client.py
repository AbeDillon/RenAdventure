from socket import *
import thread
import sys

HOST = gethostname()
#HOST = '172.16.248.48'
S_PORT = 8000
R_PORT = 1234
isRunning = True

#  connect to server's receive socket 
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, S_PORT))

#  connect to server's send socket
r = socket(AF_INET, SOCK_STREAM)
r.connect((HOST, R_PORT))

# Get user info (name)
print ""
user = raw_input('Enter your name >>>  ')
# send connection string
s.send(user + ' is now connected.')

def receive_msg(r):
    # called from constantly
    line = '<%s> says:' % user
    while True:
        data = r.recv(1024)
        if line not in data:
            print data + '\n'
        
def send_msg():
   
    #  might be an idea to make and create the send connection for every message sent.  ???? 
    message = raw_input('')
    if message == 'Quit' or message == 'quit':
        s.close()
        print 'You are no longer connected to Chat.'
    elif message.strip() == "":
        pass
    else:
        s.send('<'+user+'>' + ' says:  "' + message + '"')

thread.start_new_thread(receive_msg, (r,))

while (1):
    
    send_msg()
    
    
        



