import socket
import sys

def get_command():

    print >>sys.stdout, '> ' #sys.stdout = Wherever this is going. This will print whatever follows the , to sys.stdout
    command = ''

    command = sys.stdin.readline().strip() #Get the command from stdin

        
    
    print >>sys.stdout, '' 
    if len(command) > 0:
        return command
    else:
        return 'did nothing' #Empty command
 
s = socket.socket()
host = socket.gethostname() #Replace with actual server host address.
port = 12345

s.connect((host, port)) #Make connection

player_logged_in = False
while not player_logged_in:
    username = sys.stdin.readlines().strip() #sys.stdin = Wherever this is coming from
    password = sys.stdin.readlines().strip() #Get both username and password from stdin.
    s.send(username + ' ' + password) #Submit user/pass to server.
    response = s.recv(4096) #Get server response.
    print >>sys.stdout, response #Print server's response to stdout
    
    if response != 'Invalid username or password.':
        player_logged_in = True

player_quit = False

while(1):
    msg = '' #Initially blank so we can add to it.
    while(1):
        response = s.recv(4096) #Get response from server.
        
        if '*' in response: # * is an "end of this transmission" character here.
            msg += response.replace('*', '')
            break
        else:
            msg += response

    if msg == 'quit accepted': #This is the server response when we sent it "quit"
        player_quit = True
    
    if len(msg) > 0 and not player_quit:    
        print >>sys.stdout, msg #Print the msg to sys.stdout
    elif player_quit:
        break
        
    while(1):
        command = get_command() #Call function to get user input
        
        if len(command) > 0: #This is a non-empty command.
            break
    
    s.send(command) #Send the command to the server.
    

