import time
import engine
import socket
import thread
import threading

action_queue = {} #Queue user actions as player.name ->[[command, player]]
return_queue = {} #Queue responses as player.name -> response
clients_list = {} #Mapping of socket -> player.name
client_map = {}

def push_queue():
    print 'Pushing response queue.'
    for client in clients_list: #For each person...
        person = clients_list[client] #Get name of person.
        client_map[client].send(return_queue[person]) #Send persons's queue to them.
        return_queue[person] = '' #Clear queue for person.
        client_map[client].send('*') #End of transmission

def run_queue():
    print 'Running the command queue.'
    for command_list in action_queue.values(): #Actions
        for command in command_list:
            
            if command[0] == 'did_nothing':
                response = "did_nothing_got_it"
            elif command[0] == 'quit':
                response = 'quit_accepted'
            else:
                response = engine.do_command(command[0], command[1])
            if response != '': #Non-blank response
                return_queue[command[1].name] = return_queue.get(command[1].name, '') + response
            else:
                response = engine.do_command(command[0], command[1])
                return_queue[command[1].name] = return_queue.get(command[1].name, '')+response
        action_queue[command[1].name] = [] #Empty the action queue for this person.

    push_queue()

def client_thread(c):
    player = engine.Player('player', (0,0,1))
    player_quit = False
    clients_list[c.fileno()] = player.name
    action_queue[player.name] = []
    return_queue[player.name] = ''
    
    while not player_quit:
        player_quit = room_loop(c, player)


def room_loop(c, player):
    start_coords = player.coords
    description = engine.get_room_text(player.coords)
    c.send(description + '*')
    start_time = time.time()
    timeout = 0.01
    
    while(1):
        command = c.recv(4096)
        action_var = [command, player]
        action_queue[player.name].append(action_var)
        
        if (time.time() - start_time) > timeout: #more than x seconds passed
            run_queue()
            start_time = time.time()
        
        if start_coords != player.coords: # Player changed rooms
            break

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
    clients_list[c.fileno()] = '' #Add this socket to list of sockets, not presently tagged with person's name.
    thread.start_new_thread(client_thread,(c,))
