__author__ = 'eking'

import engine
import socket
import thread
import threading

import random

def client_thread(c):
    name = 'player' + str(random.randint(0, 1000))
    affiliation = {'Obama': 5, 'Kanye': 4, 'OReilly': 3, 'Gottfried': 2, 'Burbiglia': 1}
    player = engine.Player(name, (0,0,1), affiliation)
    player_quit = False
    
    affiliation = {'Obama': 1, 'Kanye': 2, 'OReilly': 3, 'Gottfried': 4, 'Burbiglia': 5}
    npc = engine.NPC('test', (3,4,1), affiliation)
    
    while not player_quit:
        player_quit = room_loop(c, player, npc)
        
def room_loop(c, player, npc):
    start_coords = player.coords
    description = engine.get_room_text(player.coords)
    c.send(description + '*')
    
    while(1):
        command = c.recv(4096)
        
        if command == 'did_nothing':
            response = "did_nothing_got_it"
        else:
            response = engine.do_command(command, player, npc)
        
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
