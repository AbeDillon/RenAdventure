#NOTE: Presently not working properly, issues with communicating actions that one player makes to another player.

import time
import engine
import socket
import thread
import threading
import Queue

action_queue = Queue.Queue() #Queue user actions as [command, player, c]
return_queue = Queue.Queue() #Queue response for user as [command, c]
client_map = {} #Map of c.fileno() -> c

def push_queue():
    cnt = return_queue.qsize()
    for i in range(0, cnt):
        outgoing = return_queue.get()
        response = outgoing[1]
        address = outgoing[0]
        client_map[address].send(response+'*')



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
            
        if response != '': #Non-blank response
            return_queue.put([command[2].fileno(), response])

            if 'You have' in response:
                alt_response = response.replace('You', command[1].name)
                alt_response = alt_response.replace('have', 'has')
                for person in client_map:
                    if person != command[2].fileno(): #This is someone else's queue
                        return_queue.put([person, alt_response])

   
        else: #Response was blank

            response = engine.do_command(command[0], command[1])
            if(response != "You can't go that way."): #If this happened they didn't need to get this response.
                return_queue.put([command[2].fileno(), response])
                if 'You have' in response:
                    alt_response = response.replace('You', command[1].name)
                    alt_response = alt_response.replace('have', 'has')
                    for person in client_map:
                        if person != command[2].fileno(): #This is someone else's queue
                            return_queue.put([person, alt_response])                               


    push_queue()

    
def client_thread(c):
    player = engine.Player('player', (0,0,1))
    player_quit = False
    #return_queue[c.fileno()] = ''
    print 'Player fileno is : %d' % c.fileno()
    
    while not player_quit:
        player_quit = room_loop(c, player)
    print 'Ending client thread %s' % c.fileno()
    del client_map[c.fileno()]
    
    return 1 #Exit code 1

def room_loop(c, player):
    start_time = time.time()
    timeout = 0.5
    start_coords = player.coords
    description = engine.get_room_text(player.coords)
    c.send(description + '*')
    
    while(1):
        try:
            command = c.recv(4096)

            action_var = [command, player, c]
            if command != '':
                action_queue.put(action_var)
            if(time.time()-start_time)>timeout:
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
