#NOTE: Presently not working properly, issues with room data printing out.

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
    for client in client_map: #For each person...
        client_map[client].send(return_queue[client]+'*') #Send persons's queue to them.
        return_queue[client] = '' #Clear queue for person.


def run_queue():
    cnt = action_queue.qsize() #Number of items in the queue right now.
    for i in range(0, cnt):
        alt = False
        command = action_queue.get()
        if command[0] == 'did_nothing':
            response = "did_nothing_got_it"
        elif command[0] == 'quit':
            response = 'quit_accepted'
            
        else:
            response = engine.do_command(command[0], command[1])
            print 'First round response is: %s' % response
##            if "you have taken the" in response.lower(): #This should go to others.
##                alt = True
##                alt_response = response.replace('you', command[1].name)
##                alt_response = alt_response.replace('You', command[1].name)
##                alt_response = alt_response.replace('have', 'has')
##            elif "you have opened the" in response.lower():
##                alt = True
##                alt_response = response.replace('You', command[1].name)
##                alt_response = alt_response.replace('have', 'has')
##            elif 'you have dropped the' in response.lower():
##                alt = True
##                alt_response = response.replace('You', command[1].name)
##                alt_response = alt_response.replace('have', 'has')
##            elif 'you have unlocked the' in response.lower():
##                alt = True
##                alt_response = response.replace('You', command[1].name)
##                alt_response = alt_response.replace('have', 'has')
            
            
            
        if response != '': #Non-blank response
            
            return_queue[command[2].fileno()] = return_queue.get(command[2].fileno(), '') + response
##            if alt:
##                for person in return_queue:
##                    if person != command[2].fileno(): #This is someone else
##                        return_queue[person] = return_queue.get(person, '') + alt_response
   
        else: #Response was blank?, try to get a new one.

            response = engine.do_command(command[0], command[1])
            print 'Second round response is: %s' % response
##            if "you have taken the" in response.lower(): #This should go to others.
##                alt = True
##                alt_response = response.replace('you', command[1].name)
##                alt_response = alt_response.replace('You', command[1].name)
##                alt_response = alt_response.replace('have', 'has')
##            elif "you have opened the" in response.lower():
##                alt = True
##                alt_response = response.replace('You', command[1].name)
##                alt_response = alt_response.replace('have', 'has')
##            elif 'you have dropped the' in response.lower():
##                alt = True
##                alt_response = response.replace('You', command[1].name)
##                alt_response = alt_response.replace('have', 'has')
##            elif 'you have unlocked the' in response.lower():
##                alt = True
##                alt_response = response.replace('You', command[1].name)
##                alt_response = alt_response.replace('have', 'has')
            
            if(response != "You can't go that way."): #If this happened they didn't need to get this response.
                return_queue[command[2].fileno()] = return_queue.get(command[2].fileno(), '')+response
##                if alt:
##                    for person in return_queue:
##                        if person != command[2].fileno(): #This is someone else
##                            return_queue[person] = return_queue.get(person, '') + alt_response

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
    c.send(description+'*')
    
    while(1):
        try:
            command = c.recv(4096)

            action_var = [command, player, c]
            if command != '':
                action_queue.put(action_var)
            
            if start_coords != player.coords: # Player changed rooms
                break
            
        except IOError, e:
            print 'Could not recieve command, assuming connection closed.'
            return True

def queue_loop(x):
    start_time = time.time()
    timeout = 1

    while(1):
        if(time.time() - start_time) > timeout:
            run_queue()
            start_time = time.time()

s = socket.socket()
host = socket.gethostname()
port = 12345
 
print 'Server started!'
print 'Waiting for clients...'
 
s.bind((host, port))
s.listen(5)
thread.start_new_thread(queue_loop, (1,)) #Loop for handling queue processing.
while(1):
    c, addr = s.accept()
    print 'Got connection from', addr
    client_map[c.fileno()] = c
    thread.start_new_thread(client_thread,(c,))
