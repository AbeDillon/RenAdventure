import socket
import sys
import time
import msvcrt

printed = False

def get_command():
    global printed
    start_time = time.time()
    timeout = 3
    command = ''

    if(printed): #We printed something last time.
        printed = False
        print >>sys.stdout, '> ', #sys.stdout = Wherever this is going. This will print whatever follows the , to sys.stdout

        while(1):
            if msvcrt.kbhit():
                char = msvcrt.getche()
                if ord(char) == 13: #Enter
                    break
                elif ord(char) == 8: #Backspace
                    command = command[:-1]
                elif ord(char) >= 32: #Space or other character
                    command += char
            if len(command) == 0 and (time.time()-start_time) > timeout:
                break        
        
    else: #We haven't printed anything yet
        while(1):
            if msvcrt.kbhit():
                char = msvcrt.getche()
                if ord(char) == 13: #Enter
                    break
                elif ord(char) == 8: #Backspace
                    command = command[:-1]
                elif ord(char) >= 32: #Space or other character
                    command += char
            if len(command) == 0 and (time.time()-start_time) > timeout:
                break

         
    if len(command) > 0 and command.strip() != '':
        print >>sys.stdout, ''
        return command
    else:
        return 'did_nothing' #Empty command
 
s = socket.socket()
host = socket.gethostname() #Replace with actual server host address.
port = 12345

s.connect((host, port)) #Make connection

#player_logged_in = False
#while not player_logged_in:
#    username = sys.stdin.readlines().strip() #sys.stdin = Wherever this is coming from
#    password = sys.stdin.readlines().strip() #Get both username and password from stdin.
#    s.send(username + ' ' + password) #Submit user/pass to server.
#    response = s.recv(4096) #Get server response.
#    print >>sys.stdout, response #Print server's response to stdout
#    
#    if response != 'Invalid username or password.':
#        player_logged_in = True

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

    if msg == 'quit_accepted': #This is the server response when we send it "quit"
        player_quit = True
        break
    
    if len(msg) > 0 and 'did_nothing_got_it' not in msg:    
        print >>sys.stdout, msg #Print the msg to sys.stdout
        printed = True
        
    while(1):
        command = get_command() #Call function to get user input
        
        if len(command) > 0: #This is a non-empty command.
            break
    
    s.send(command) #Send the command to the server.
    

