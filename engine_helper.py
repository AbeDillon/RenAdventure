__author__ = 'EKing'

import engine
from math import *
import threading, random

valid_verbs = ['take', 'open', 'go', 'drop', 'unlock', 'lock', 'reveal']


def do_command(player, room, verb, nouns, object, tags):
    messages = []
    if 'start_script' in tags: # Object has a script for this verb, break it into multiple commands
        for n, action in enumerate(object.scripts[verb]):
            action_verb = action[0]
            noun = action[1]
            delay = action[2]

            if delay > 0: # There is a delay for this script, spin off a timer thread
                object.scripts[verb][n] = (object.scripts[verb][n][0], object.scripts[verb][n][1], 0) # Set delay to zero so it doesn't spin off another timer
                timer = threading.Timer(float(delay), script_delay, args=[player, object.scripts[verb][n:]]) # Start a timer to run the remainder of the script in 'delay' seconds
                timer.start()
                break
            else:
                command = [player.name, action_verb + ' ' + noun]
                engine.put_commands([command], script=True) # Push the command to the command queue
    else:
        noun_string = ' '.join(nouns)

        script = verb + "(room, player, object, noun_string, tags)"

        text, alt_text, player_messages = eval(script) # player_messages are player specific messages, needed when a different message is sent to each player

        if len(text) > 0 and player.name in room.players:
            messages.append((player.name, text))

        if len(player_messages) > 0:
            for player, message in player_messages:
                messages.append((player.name, message))
        elif len(alt_text) > 0:
            for alt_player in room.players.values():
                if alt_player is not player:
                    messages.append((alt_player.name, alt_text))

            if verb == 'go': # Player entered a new room, pass messages to all players in the new room
                room = engine._Rooms[player.coords]
                messages.append((player.name, text))

                for alt_player in room.players.values():
                    if alt_player is not player:
                        messages.append((alt_player.name, "%s has entered the room." % player.name))

    return messages

def scrub(scripts):
    # Scrubs the verbs in the script to make sure they are valid, no sneaky code injection
    global valid_verbs
     
    for script in scripts.keys():
        for action in scripts[script]:
            verb = action[0]
            if verb not in valid_verbs:
                del scripts[script]
                break

    return scripts

def get_room_text(player_name, coords):
    room = engine._Rooms[coords]
    text = room.desc

    # Add items to the text
    visible_items = get_visible(room.items)

    if len(visible_items) > 0:
        text += " You see"

        for n, item in enumerate(visible_items):
            if len(visible_items) == 1:
                text += " %s in the room." % item.desc
            elif n == (len(visible_items) - 1):
                text += " and %s in the room." % item.desc
            else:
                text += " %s," % item.desc

    # Add portals to the text
    visible_portals = get_visible(room.portals)

    if len(visible_portals) > 0:
        text += " There is"

        for n, portal in enumerate(visible_portals):
            if len(visible_portals) == 1:
                text += " %s to the %s." % (portal.desc, portal.direction)
            elif n == (len(visible_portals) - 1):
                text += " and %s to the %s." % (portal.desc, portal.direction)
            else:
                text += " %s to the %s," % (portal.desc, portal.direction)

    # Add NPCs and players to the text
    names = room.npcs.keys() + room.players.keys()
    names.remove(player_name)

    for n, name in enumerate(names):
        if len(names) == 1:
            text += " %s is in the room." % name.title()
        elif n == (len(names) - 1):
            text += " and %s are in the room." % name.title()
        else:
            text += " %s," % name.title()

    return text

def get_visible(objects):
    visible_objects = []

    for object in objects.values():
        if not object.hidden:
            visible_objects.append(object)

    return visible_objects

def check_key(player, key):
    for item in player.items.values():
        if item.name == key:
            return True

    return False

def parse_command(command):
    # Create translation tables to make the command easier to parse
    translate_one_word = {'i': 'inventory',
                          'l': 'look room',
                          'h': 'help',
                          'q': 'quit',
                          'n': 'go north',
                          's': 'go south',
                          'w': 'go west',
                          'e': 'go east'}

    translate_verb = {'look': 'look',
                      'l': 'look',
                      'examine': 'look',
                      'inspect': 'look',
                      'search': 'look',
                      'take': 'take',
                      'grab': 'take',
                      'get': 'take',
                      'open': 'open',
                      'go': 'go',
                      'head': 'go',
                      'enter': 'go',
                      'walk': 'go',
                      'drop': 'drop',
                      'unlock': 'unlock',
                      'lock': 'lock',
                      'say': 'say',
                      's': 'say',
                      'shout': 'shout',
                      'damage': 'damage',
                      'inventory': 'inventory'}

    translate_noun = {'n': 'north',
                      's': 'south',
                      'w': 'west',
                      'e': 'east',
                      'u': 'up',
                      'd': 'down'}

    command = command.lower()
    command = translate_one_word.get(command, command) # This compares command against the 'translate_one_word' dictionary and translates the command

    words = command.split()

    verb = words[0]
    verb = translate_verb.get(verb, 'bad_command')

    nouns = words[1:]
    for n, noun in enumerate(nouns):
        # convert short-hand nouns to their longer name (i.e. 's' => 'south')
        nouns[n] = translate_noun.get(noun, noun)

    return verb, nouns

def npc_action(npc):
    room = engine._Rooms[npc.coords]
    if len(room.players) > 0: # There are players in the room, talk to them
        message = "Something" # Replace with tweet
        commands = []
        commands.append((npc.name, 'say %s' % message))
        commands.append((npc.name, 'damage say'))
        engine.put_commands(commands, npc=True)
    else: # No players in the room, choose a random portal and go through it
        valid_portals = get_valid_objects(npc, room, 'go')

        if len(valid_portals) > 0:
            portal = random.choice(valid_portals)
            direction = portal.direction
            command_str = 'go %s' % direction
            command = (npc.name, command_str)
            engine.put_commands([command], npc=True)

#Flags  'p' = portals
#       'r' = room items
#       'i' = player items

_ValidLookUp = {'look': ('pri', {'hidden': True}),
                'take': ('r', {'hidden': True, 'portable': False}),
                'drop': ('i', {'hidden': True}),
                'go': ('p', {'hidden': True}),
                'open': ('ir', {'hidden': True}),
                'unlock': ('pri', {'hidden': True}),
                'lock': ('pri', {'hidden': True}),
                'reveal': ('pr', {'hidden': False})}

def get_valid_objects(player, room, verb):
    global _ValidLookUp

    flags, cull = _ValidLookUp.get(verb, ('',{}))
    valid_objects = []

    if 'p' in flags:
        for portal in room.portals:
            valid_objects.append(room.portals[portal])

    if 'r' in flags:
        for item in room.items:
            valid_objects.append(room.items[item])

    if 'i' in flags:
        for item in player.items:
            valid_objects.append(player.items[item])

    for object in valid_objects:
        for attribute, value in enumerate(cull):
            if isinstance(object, engine.Item):    # Items are the only object that have all attributes
                if attribute == 'portable' and object.portable == value:
                    valid_objects.remove(object)
                    break

            if attribute == 'hidden' and object.hidden == value:
                valid_objects.remove(object)
                break

    return valid_objects

def get_all_objects(player, verb):
    # Returns all valid objects in the game for a verb and the room they are in
    global _ValidLookUp

    flags, cull = _ValidLookUp.get(verb, ('',{}))
    valid_objects = []

    for room in engine._Rooms.values():
        if 'r' in flags:
            for item in room.items.values():
                valid_objects.append((room, item))

        if 'p' in flags:
            for portal in room.portals.values():
                valid_objects.append((room, portal))

    if 'i' in flags:
        for item in player.items.values():
            valid_objects.append((None, item))

    for room, object in valid_objects:
        for attribute, value in enumerate(cull):
            if isinstance(object, engine.Item):    # Items are the only object that have all attributes
                if attribute == 'portable' and object.portable == value:
                    valid_objects.remove((room, object))
                    break

            if attribute == 'hidden' and object.hidden == value:
                valid_objects.remove((room, object))
                break

    return valid_objects

def get_object(nouns, valid_objects):
    """
    Recognizes short hand for nouns (i.e. if there is a gold key in the room, and the command is "get key", the
    game will recognize that you meant "get gold key" so long as there is only one key in the room.

    Returns the object pertaining to the noun.
    """

    # break the nouns into individual words
    noun_bits = []
    for noun in nouns:
        noun = noun.replace('_', ' ')
        noun = noun.replace('-', ' ')
        noun_bits.append(noun)

    # break the list of valid objects into individual words
    object_bits = {}
    for object in valid_objects:
        if isinstance(object, engine.Portal):
            name = object.direction + ' ' + object.name # So we can detect both direction and name as an identifier for a portal
        else:
            name = object.name
        name = name.replace('_', ' ')
        name = name.replace('-', ' ')
        name = name.split()
        for bit in name:
            if bit in object_bits:
                object_bits[bit].append(object)
            else:
                object_bits[bit] = [object]

    # find unique matches between the nouns and the valid items
    for bit in noun_bits:
        if bit in object_bits:
            if len(object_bits[bit]) == 1:
                return object_bits[bit][0]

########### ACTIONS #############
def look(room, player, object, noun, tags):
    if object == None:
        if 'room' in noun or noun == '':
            text = get_room_text(player.name, player.coords)
        else:
            text = "There is no %s here." % noun
    else:
        text = object.inspect_desc

    return text, '', [] # Empty string is alt_text, we don't need to tell other players about a player looking at something

def take(room, player, object, noun, tags):
    alt_text = ''

    if object == None:
        text = "There is no %s to take." % noun
    else:
        # Move object from room to player
        player.items[object.name] = object
        del room.items[object.name]
        text = "You have taken the %s." % object.name
        alt_text = "%s has taken the %s." % (player.name, object.name)

    return text, alt_text, []

def open(room, player, object, noun, tags):
    alt_text = ''

    if object == None:
        text = "There is no %s to open." % noun
    elif object.locked and 'script' not in tags:
        text = "You can't open the %s, it is locked." % object.name
    elif not object.container:
        text = "You can't open the %s." % object.name
    else:
        if len(object.items) > 0:
            text = "You have opened the %s, inside you find:" % object.name
            alt_text = "%s has opened the %s, inside there is:" % (player.name, object.name)

            if 'script' in tags:
                text = alt_text = "The %s has opened, inside there is:" % object.name

            # Open the container and move its contents to the room
            for item in object.items.keys():
                room.items[item] = object.items[item]
                del object.items[item]
                text += "\n\t%s" % item
                alt_text += "\n\t%s" % item
        else:
            text = "You have opened the %s, but there is nothing inside." % object.name
            alt_text = "%s has opened the %s, but there is nothing inside." % (player.name, object.name)

            if 'script' in tags:
                text = alt_text = "The %s has opened, but there is nothing inside." % object.name

    return text, alt_text, []

def go(room, player, object, noun, tags):
    alt_text = ''

    if object == None:
        text = "You can't go that way."
    elif object.locked and 'script' not in tags:
        text = "That way is locked."
    else:
        # Move player to the coordinates the portal leads to
        player.coords = object.coords
        if 'npc' not in tags:
            del room.players[player.name] # Remove player from last room
            engine._Rooms[player.coords].players[player.name] = player # Add player to new room
        else:
            del room.npcs[player.name] # Remove NPC from the last room
            engine._Rooms[player.coords].npcs[player.name] = player # Add the NPC to the new room

        text = get_room_text(player.name, player.coords)
        alt_text = "%s has left the room through the %s door." % (player.name, noun)

    return text, alt_text, []

def drop(room, player, object, noun, tags):
    alt_text = ''

    if object == None:
        text = "You have no %s to drop." % noun
    else:
        # Move item from player to the room
        room.items[object.name] = object
        del player.items[object.name]
        text = "You have dropped the %s." % object.name
        alt_text = "%s has dropped a %s." % (player.name, object.name)

    return text, alt_text, []

def unlock(room, player, object, noun, tags):
    alt_text = ''

    if object == None:
        text = "There is no %s to unlock." % noun
    elif not object.locked:
        text = "The %s is already unlocked." % object.name
    else:
        if check_key(player, object.key) or 'script' in tags:
            object.locked = False

            if isinstance(object, engine.Portal):
                for portal in engine._Rooms[object.coords].portals.values(): # Unlock the portal from the other side as well
                    if portal.coords == player.coords:
                        portal.locked = False

            text = "You have unlocked the %s." % object.name
            alt_text = "%s has unlocked the %s." % (player.name, object.name)

            if 'script' in tags:
                text = alt_text = "The %s has unlocked." % object.name
        else:
            text = "You don't have the key to unlock the %s." % object.name

    return text, alt_text, []

def lock(room, player, object, noun, tags):
    alt_text = ''

    if object == None:
        text = "There is no %s to lock." % noun
    elif object.locked:
        text = "The %s is already unlocked." % object.name
    else:
        if check_key(player, object.key) or 'script' in tags:
            object.locked = True

            if isinstance(object, engine.Portal):
                for portal in engine._Rooms[object.coords].portals.values(): # Lock the portal from the other side as well
                    if portal.coords == player.coords:
                        portal.locked = True

            text = "You have locked the %s." % object.name
            alt_text = "%s has locked the %s." % (player.name, object.name)

            if 'script' in tags:
                text = alt_text = "The %s has locked." % object.name
        else:
            text = "You don't have the key to lock the %s." % object.name

    return text, alt_text, []

def inventory(room, player, object, noun, tags):
    if len(player.items) > 0:
        text = "Inventory:"
        for item in player.items.values():
            text += "\n\t%s" % item.name
    else:
        text = "Your inventory is empty."

    return text, '', [] # Empty string is alt_text, we don't need to tell other players about a player looking at their inventory

def say(room, player, object, noun, tags):
    text = "You say %s" % noun
    alt_text = "%s says %s" % (player.name, noun)

    return text, alt_text, []

def shout(room, player, object, noun, tags):
    text = "You shout %s" % noun
    alt_text = "%s shouted %s" % (player.name, noun)

    bubble_coords = []
    for i in range(-2,3): # Create a 5x5 bubble around the player
        for j in range(-2,3):
            bubble_coords.append((player.coords[0]+i, player.coords[1]+j, player.coords[2]))

    trimmed_bubble = []
    for coords in bubble_coords: # Remove coords from the bubble that don't have room with players in them
        if coords in engine._Rooms and len(engine._Rooms[coords].players) > 0:
            trimmed_bubble.append(coords)

    player_messages = []
    for coords in trimmed_bubble:
        for alt_player in engine._Rooms[coords].players.values():
            player_messages.append((alt_player, alt_text))

    return text, alt_text, player_messages

def damage(room, attacker, object, noun, tags):
    player_messages = []

    for player in room.players.values():
        difference = 0
        for person in attacker.affiliation: # Calculate the total difference between the player and the npc
            difference += -abs(attacker.affiliation[person] - player.affiliation[person])

        difference += 6 # Shift the difference over to put the mid point at 0 (this will need to be changed if the number of people changes)

        if (player.fih + difference) > 30: # Player cannot exceed 30 'Faith in Humanity' points
            player.fih = 30
        else:
            player.fih += difference

        if difference > 0:
            text = "Your Faith in Humanity is increased by %d." % difference
        elif difference < 0:
            text = "Your Faith in Humanity is decreased by %d." % abs(difference)
        else:
            text = "Your Faith in Humanity is unaffected."

        player_messages.append((player, text))

    return '', '', player_messages

def bad_command(room, player, object, noun, tags):
    return "That is not a valid command.", '', [] # Empty string is alt_text, we don't need to tell other players about a failed command execution.
############# SCRIPT METHODS ##########
def script_delay(player, script):
    # Runs the remainder of a script after a delay
    for n, action in enumerate(script):
        verb = action[0]
        noun = action[1]
        delay = action[2]

        if delay > 0: # There is a delay for this script, spin off a timer thread
            script[n] = (script[n][0],  script[n][1], 0) # Set delay to zero so it doesn't spin off another timer
            timer = threading.Timer(float(delay), script_delay, args=[player, script[n:]]) # Start a timer to run the remainder of the script in 'delay' seconds
            timer.start()
            break
        else:
            command = [player.name, verb + ' ' + noun]
            engine.put_commands([command], script=True) # Push the command to the command queue

def reveal(room, player, object, noun, tags):
    # Reveals a hidden object
    object.hidden = False
    text = "A %s appears in the room." % object.name

    return text, text

def hide(room, player, object, noun, tags):
    # Hides an object
    object.hidden = True
    text = "The %s disappears from the room." % object.name

    return text, text