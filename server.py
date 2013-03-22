__author__ = 'eking'

import engine
import socket
import thread
import threading

def client_thread(c):
    player = engine.Player('player', (0,0,1))
    player_quit = False
    
    while not player_quit:
        player_quit = room_loop(c, player)
        
def room_loop(c, player):
    start_coords = player.coords
    description = engine.get_room_text(player.coords)
    c.send(description + '*')
    
    while(1):
        command = c.recv(4096)
        
        if command == 'did_nothing':
            response = "did_nothing_got_it"
        else:
            response = engine.do_command(command, player)
        
        if len(response) > 0:
            c.send(response + '*')
        
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
    thread.start_new_thread(client_thread,(c,))
