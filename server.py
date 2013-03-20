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
    description = engine.get_room_text(rooms[player.coords])
    c.send(description + '*')
    
    while(1):
        command = c.recv(4096)
        
        if command == 'did_nothing':
            response = "That is not a valid command."
        else:
            response = engine.do_command(command, player, rooms[player.coords], rooms)
        
        if len(response) > 0:
            c.send(response + '*')
        
        if start_coords != player.coords: # Player changed rooms
            break

rooms = {}

portal = engine.Portal('north', 'a wooden door', 'an old creaky door', (0,1,1))
apple1 = engine.Item('small apple', 'a small apple', 'blah', scripts={'take': [['take', 'small apple'], ['reveal', 'large sword'], ['print_text', 'You have picked up the small apple, a large sword appears in the room.']]})
apple2 = engine.Item('large apple', 'a large apple', 'blah')
sword = engine.Item('large sword', 'a large sword', 'blah', hidden=True)
key = engine.Item('small key', 'a small key', 'a shiny gold key')
chest = engine.Container('chest', 'a small chest', 'blah', items=[key])
room = engine.Room('You are in an empty jail cell, there is a cot bolted into the south wall.', portals=[portal], items=[apple1, apple2, sword], containers=[chest])
rooms[(0,0,1)] = room

portal = engine.Portal('south', 'an iron door', 'an old creaky door', (0,0,1))
room = engine.Room('You are in a guard room, there is a table on the north end of the room.', [portal])
rooms[(0,1,1)] = room

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