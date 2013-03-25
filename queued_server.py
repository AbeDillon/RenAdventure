#NOTE: Presently not working properly, only accepting of a single client connection before it starts having errors.

import time
import engine
import socket
import thread
import threading
import Queue

action_queue = Queue.Queue() #Queue user actions as [command, player, c]
return_queue = {} #Queue responses as c.fileno() -> response
client_map = {} #Map of c.fileno() -> c

def push_queue():
    print 'Pushing the response queue.'
    for client in client_map: #For each person...
            client_map[client].send(return_queue[client]) #Send persons's queue to them.
            return_queue[client] = '' #Clear queue for person.
            client_map[client].send('*') #End of transmission


def run_queue():
    print 'Running the command queue.'
    cnt = action_queue.qsize() #Number of items in the queue right now.
    for i in range(0, cnt):
        command = action_queue.get()
        if command[0] == 'did_nothing':
            response = "did_nothing_got_it"
        elif command[0] == 'quit':
            response = 'quit_accepted'
            
        else:
            response = engine.do_command(command[0], command[1])
        if response != '': #Non-blank response            
            return_queue[command[2].fileno()] = return_queue.get(command[2].fileno(), '') + response
   
        else: #Response was blank?, try to get a new one.

            response = engine.do_command(command[0], command[1])
            if(response != "You can't go that way."): #If this happened they didn't need to get this response.
                return_queue[command[2].fileno()] = return_queue.get(command[2].fileno(), '')+response

    push_queue()

    
def client_thread(c):
    player = engine.Player('player', (0,0,1))
    player_quit = False
    return_queue[c.fileno()] = ''
    
    while not player_quit:
        player_quit = room_loop(c, player)
    print 'Ending client thread %s' % c.fileno()
    del return_queue[c.fileno()]
    del client_map[c.fileno()]
    
    return 1 #Exit code 1

def room_loop(c, player):
    start_coords = player.coords
    description = engine.get_room_text(player.coords)
    c.send(description + '*')
    start_time = time.time()
    timeout = 0.01
    
    while(1):
        try:
            command = c.recv(4096)

            action_var = [command, player, c]
            if command != '':
                action_queue.put(action_var)
            
            if (time.time() - start_time) > timeout: #more than x seconds passed
                run_queue()
                start_time = time.time()
            
            if start_coords != player.coords: # Player changed rooms
                break
        except IOError, e:
            print 'Could not recieve command, assuming connection closed.'
            return True

s = socket.socket()
host = socket.gethostname()
port = 12345
 
print 'Server started!'
print 'Waiting for clients...'
 
s.bind((host, port))
s.listen(5)

while(1):
    c, addr = s.accept()
    print 'Got connection from', addr
    client_map[c.fileno()] = c
    thread.start_new_thread(client_thread,(c,))
