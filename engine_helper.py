__author__ = 'EKing'

import engine_classes
import roomBuilderThread, sense_effect_filters
import threading, random
import Queue

valid_verbs = ['take', 'open', 'go', 'drop', 'unlock', 'lock', 'hide', 'reveal', 'add_status_effect', 'lose_status_effect']

def do_command(player_name, command, tags, engine):
    action_map = {'look': look,
                  'take': take,
                  'open': open,
                  'go': go,
                  'drop': drop,
                  'unlock': unlock,
                  'lock': lock,
                  'inventory': inventory,
                  'say': say,
                  'shout': shout,
                  'damage': damage,
                  'lol': lol,
                  'boo': boo,
                  'bad_command': bad_command,
                  'reveal': reveal,
                  'hide': hide,
                  'add_status_effect': add_status_effect,
                  'lose_status_effect': lose_status_effect}

    player = engine._Characters[player_name]
    room = engine._Rooms[player.coords]
    verb, nouns = parse_command(command, tags)
    
    if verb == 'damage' and 'npc' not in tags: # Only NPCs can use the damage command
        verb = 'bad_command'

    if 'script' in tags:
        all_objects = get_all_objects(player, verb, engine) # tuple of all objects and the room they are in

        valid_objects = []
        for object_room, object in all_objects:
            valid_objects.append(object)
    else:
        valid_objects = get_valid_objects(player, room, verb, engine) # Find the valid objects in the room that can be acted on by the verb
        
    objects = get_objects(nouns, valid_objects) # Get the object that the player is trying to act on
    if len(objects) != 0:
        object = objects[0] # this needs to be replaced when we add support for multiple objects in the command functions
    else:
        object = None

    if 'script' in tags: # We need to find which room the object is in
        for room, new_object in all_objects:
            if object is new_object:
                break

    messages = []
    if object != None and verb in object.scripts and 'script' not in tags: # Object has a script for this verb, break it into multiple commands
        for n, action in enumerate(object.scripts[verb]):
            action_verb = action[0]
            noun = action[1]
            delay = action[2]

            if delay > 0: # There is a delay for this script, spin off a timer thread
                object.scripts[verb][n] = (object.scripts[verb][n][0], object.scripts[verb][n][1], 0) # Set delay to zero so it doesn't spin off another timer
                timer = threading.Timer(float(delay), script_delay, args=[player, object.scripts[verb][n:], engine]) # Start a timer to run the remainder of the script in 'delay' seconds
                timer.start()
                break
            else:
                command = [player.name, action_verb + ' ' + noun, ['script']]
                engine.put_commands([command]) # Push the command to the command queue
    else:
        noun_string = ' '.join(nouns)
        action = action_map.get(verb, None)

        if action != None:
            messages = action(room, player, object, noun_string, tags, engine)

    return sense_effect_filters.filter_messages(messages, engine)

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

def get_room_text(player_name, coords, engine):
    room = engine._Rooms[coords]
    text = '<sight>' + room.desc

    # Add items to the text
    visible_items = get_visible(room.items, engine)

    if len(visible_items) > 0:
        text += " You see"

        for n, item in enumerate(visible_items):
            quantity = room.items[item.name]
            description = item.desc

            if quantity > 1:
                name = item.name

                # Pluralize the name
                if name[-1:] == 's':
                    name = name[:-1] +'es'
                elif name[-1:] == 'y':
                    name = name[:-1] + 'ies'
                else:
                    name = name + 's'

                description = str(quantity) + ' ' + name

            if len(visible_items) == 1:
                text += " %s in the room." % description
            elif n == (len(visible_items) - 1):
                text += " and %s in the room." % description
            else:
                text += " %s," % description

    # Add portals to the text
    visible_portals = get_visible(room.portals, engine)

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
    names = room.npcs + room.players
    names.remove(player_name)

    for n, name in enumerate(names):
        if len(names) == 1:
            text += " %s is in the room." % name.title()
        elif n == (len(names) - 1):
            text += " and %s are in the room." % name.title()
        else:
            text += " %s," % name.title()

    return text + '</sight>'

def get_visible(object_names, engine):
    visible_objects = []
    objects = []

    for name in object_names:
        for i in range(object_names[name]): # Appends the item name once for each item with that name
            engine._Objects_Lock.acquire()
            objects.append(engine._Objects[name])
            engine._Objects_Lock.release()

    for object in objects:
        if not object.hidden:
            visible_objects.append(object)

    return visible_objects

def check_key(player, key):
    for item in player.items:
        if item == key:
            return True

    return False

def add_item(container, item):
    if item in container.items:
        container.items[item] += 1
    else:
        container.items[item] = 1

def rem_item(container, item):
    if container.items[item] == 1:
        del container.items[item]
    else:
        container.items[item] -= 1

def parse_command(command, tags):
    # Create translation tables to make the command easier to parse
    global valid_verbs

    translate_one_word = {'i': 'inventory',
                          'l': 'look room',
                          'h': 'help',
                          'q': 'quit',
                          'n': 'go north',
                          's': 'go south',
                          'w': 'go west',
                          'e': 'go east',
                          'u': 'go up',
                          'd': 'go down'}

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
                      'inventory': 'inventory',
                      'lol': 'lol',
                      'boo': 'boo'}

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
    if verb not in valid_verbs or 'script' not in tags:
        verb = translate_verb.get(verb, 'bad_command')

    nouns = words[1:]
    for n, noun in enumerate(nouns):
        # convert short-hand nouns to their longer name (i.e. 's' => 'south')
        nouns[n] = translate_noun.get(noun, noun)

    return verb, nouns

def npc_action(npc, engine):
    room = engine._Rooms[npc.coords]

    if len(room.players) > 0: # There are players in the room, talk to them
        message = random.choice(npc.tweets)
        commands = []
        commands.append((npc.name, 'say %s' % message, ['npc']))
        commands.append((npc.name, 'damage say', ['npc']))
        engine.put_commands(commands)
    else: # No players in the room, choose a random portal and go through it
        valid_portals = get_valid_objects(npc, room, 'go', engine)

        portals = []
        for portal in valid_portals:    # Cull locked doors and doors that lead to an unbuilt room
            if not portal.locked and engine._Rooms.get(portal.coords, None) != None:
                portals.append(portal)

        if len(portals) > 0:
            portal = random.choice(portals)
            direction = portal.direction
            command_str = 'go %s' % direction
            command = (npc.name, command_str, ['npc'])
            engine.put_commands([command])

#Flags  'p' = portals
#       'r' = room items
#       'i' = player items

_ValidLookUp = {'look': ('pri', {'hidden': True}),
                'take': ('r', {'hidden': True}),
                'drop': ('i', {'hidden': True}),
                'go': ('p', {'hidden': True}),
                'open': ('ir', {'hidden': True}),
                'unlock': ('pri', {'hidden': True}),
                'lock': ('pri', {'hidden': True}),
                'hide': ('pr', {}),
                'reveal': ('pr', {})}

def get_valid_objects(player, room, verb, engine):
    global _ValidLookUp

    flags, cull = _ValidLookUp.get(verb, ('',{}))
    object_names = []
    valid_objects = []

    if 'p' in flags:
        for portal in room.portals:
            object_names.append(portal)

    if 'r' in flags:
        for item in room.items:
            object_names.append(item)

    if 'i' in flags:
        for item in player.items:
            object_names.append(item)

    for name in object_names:
        engine._Objects_Lock.acquire()
        valid_objects.append(engine._Objects[name])
        engine._Objects_Lock.release()

    for object in valid_objects:
        for attribute, value in enumerate(cull):
#            if isinstance(object, engine_classes.Item):    # Items are the only object that have all attributes
#                if attribute == 'portable' and object.portable == value:
#                    valid_objects.remove(object)
#                    break

            if attribute == 'hidden' and object.hidden == value:
                valid_objects.remove(object)
                break

    return valid_objects

def get_all_objects(player, verb, engine):
    # Returns all valid objects in the game for a verb and the room they are in
    global _ValidLookUp

    flags, cull = _ValidLookUp.get(verb, ('',{}))
    valid_objects = []

    for room in engine._Rooms.values():
        if 'r' in flags:
            for item in room.items:
                valid_objects.append((room, engine._Objects[item]))

        if 'p' in flags:
            for portal in room.portals:
                valid_objects.append((room, engine._Objects[portal]))

    if 'i' in flags:
        for item in player.items:
            valid_objects.append((None, engine._Objects[item]))

    for room, object in valid_objects:
        for attribute, value in enumerate(cull):
            if isinstance(object, engine_classes.Item):    # Items are the only object that have all attributes
                if attribute == 'portable' and object.portable == value:
                    valid_objects.remove((room, object))
                    break

            if attribute == 'hidden' and object.hidden == value:
                valid_objects.remove((room, object))
                break

    return valid_objects

def get_objects(nouns, valid_objects):
    """
    Recognizes short hand for nouns (i.e. if there is a gold key in the room, and the command is "get key", the
    game will recognize that you meant "get gold key" so long as there is only one key in the room.

    Returns the object pertaining to the noun.
    """

    # break the list of valid objects into individual words
    unique = dict()
    for obj in valid_objects:
        if isinstance(obj, engine_classes.Portal):
            name = obj.direction + ' ' + obj.name # So we can detect both direction and name as an identifier for a portal
        else:
            name = obj.name

        ngrams = getNgrams(name)

        for ngram in ngrams:
            unique[ngram] = unique.get(ngram, set()) | {obj}

    # break the nouns into individual words
    nounStr = " ".join(nouns)
    nouns = nounStr.split(",")

    objects = []
    for noun in nouns:
        noun = noun.strip().rstrip()
        noun = noun.replace("_", " ")
        noun = noun.replace("-", " ")
        items = unique.get(noun, set())
        if len(items) == 1:
            objects.extend(set(items))
        else:
            print "no unique match found for: " + noun

    return objects

def getNgrams(text):
    """

    """

    text = text.replace("_", " ")
    text = text.replace("-", " ")
    words = text.split()

    ngrams = []
    for n in range(len(words)):
        for w in range(0, len(words) - n):
            ngram = words[w: (w + n +1)]
            ngram = " ".join(ngram)
            ngrams.append(ngram)

    return ngrams

########### ACTIONS #############
def look(room, player, object, noun, tags, engine):
    if object == None:
        if 'room' in noun or noun == '':
            text = get_room_text(player.name, player.coords, engine)
        else:
            text = "There is no %s here." % noun
    else:
        text = object.inspect_desc

    return [(player.name, text)]

def take(room, player, object, noun, tags, engine):
    alt_text = ''
    sound = '_play_ outlaw'

    if object == None:
        text = "There is no %s to take." % noun
    elif not object.portable:
        text = "You can't take the %s." % noun
    else:
        # Move object from room to player
        add_item(player, object.name)
        rem_item(room, object.name)
        text = "You have taken the %s." % object.name
        alt_text = "%s has taken the %s." % (player.name, object.name)
        sound = '_play_ pickup'

    text = '<sight>' + text + '</sight>'
    alt_text = '<sight>' + alt_text + '</sight>'

    messages = []
    messages.append((player.name, text))    # Message to send to the player
    messages.append((player.name, sound))

    for alt_player in room.players:
        if alt_player != player.name:
            messages.append((alt_player, alt_text))

    return messages

def open(room, player, object, noun, tags, engine):
    alt_text = ''
    sound = '_play_ outlaw'

    if object == None:
        text = "There is no %s to open." % noun
    elif object.locked and 'script' not in tags:
        text = "You can't open the %s, it is locked." % object.name
    elif not object.container:
        text = "You can't open the %s." % object.name
    else:
        sound = '_play_ open_sound'
        if len(object.items) > 0:
            text = "You have opened the %s, inside you find:" % object.name
            alt_text = "%s has opened the %s, inside there is:" % (player.name, object.name)

            if 'script' in tags:
                text = alt_text = "The %s has opened, inside there is:" % object.name

            if object.name in room.items: # Container is in a room
                for item in object.items.keys(): # Open the container and move its contents to the room
                    add_item(room, item)
                    rem_item(object, item)
                    text += "\n\t%s" % item
                    alt_text += "\n\t%s" % item
            else: # Container is in the player's inventory
                for item in object.items.keys(): # Open the container and move its contents to the player's inventory
                    add_item(player, item)
                    rem_item(object, item)
                    text += "\n\t%s" % item
                    alt_text += "\n\t%s" % item
        else:
            text = "You have opened the %s, but there is nothing inside." % object.name
            alt_text = "%s has opened the %s, but there is nothing inside." % (player.name, object.name)

            if 'script' in tags:
                text = alt_text = "The %s has opened, but there is nothing inside." % object.name

    text = '<sight>' + text + '</sight>'
    alt_text = '<sight>' + alt_text + '</sight>'

    messages = []
    messages.append((player.name, text))
    messages.append((player.name, sound))

    for alt_player in room.players:
        if alt_player != player.name:
            messages.append((alt_player, alt_text))

    return messages

def go(room, player, object, noun, tags, engine):
    alt_text = ''
    messages = []

    if object == None:
        text = "You can't go that way."
        return [(player.name, text)]
    else:
        new_room = engine._Rooms.get(object.coords, "Build")

    if new_room == "Build": # Room does not exist, spin off builder thread
        room.players.remove(player.name)    # Remove player from the room
        player.coords = object.coords   # Change player coordinates to new room
        engine._Rooms[object.coords] = None # Set new room to None

        engine._Characters_In_Builder_Lock.acquire()
        engine._Characters_In_Builder[player.name] = player
        engine._Characters_In_Builder_Lock.release()

        engine._Characters_Lock.acquire()
        del engine._Characters[player.name]
        engine._Characters_Lock.release()

        engine._BuilderQueues[player.name] = Queue.Queue()    # Create builder queue for the player to use
        builder_thread = roomBuilderThread.BuilderThread(engine, 'room', engine._BuilderQueues[player.name], engine._MessageQueue, engine._CommandQueue, object.coords, player.name)
        builder_thread.start()  # Spin off builder thread
    elif new_room == None: # Room is being built, cannot enter the room
        messages.append((player.name, "This room is under construction, you cannot enter it at this time."))
    else: # Room is built, enter it
        if object.locked and 'script' not in tags:
            text = "That way is locked."
        else:
            # Move player to the coordinates the portal leads to
            player.prev_coords = player.coords
            player.coords = object.coords
            if 'npc' not in tags:
                room.players.remove(player.name) # Remove player from last room
                engine._Rooms[player.coords].players.append(player.name) # Add player to new room
            else:
                room.npcs.remove(player.name) # Remove NPC from the last room
                engine._Rooms[player.coords].npcs.append(player.name) # Add the NPC to the new room

            text = get_room_text(player.name, player.coords, engine)
            alt_text = "%s has left the room through the %s door." % (player.name.title(), noun)

        alt_text = '<sight>' + alt_text + '</sight>'

        messages.append((player.name, text))

        for alt_player in room.players: # Give players in room that was left a message
            messages.append((alt_player, alt_text))

        for alt_player in engine._Rooms[player.coords].players: # Give players in the new room a message
            if alt_player != player.name:
                messages.append((alt_player, '%s has entered the room.' % player.name.title()))

    return messages

def drop(room, player, object, noun, tags, engine):
    alt_text = ''

    if object == None:
        text = "You have no %s to drop." % noun
        sound = '_play_ outlaw'
    else:
        # Move item from player to the room
        add_item(room, object.name)
        rem_item(player, object.name)
        text = "You have dropped the %s." % object.name
        alt_text = "%s has dropped a %s." % (player.name, object.name)
        sound = '_play_ drop'

    text = '<sight>' + text + '</sight>'
    alt_text = '<sight>' + alt_text + '</sight>'

    messages = []
    messages.append((player.name, text))
    messages.append((player.name, sound)) # Sound to send to the player

    for alt_player in room.players:
        if alt_player != player.name:
            messages.append((alt_player, alt_text))

    return messages

def unlock(room, player, object, noun, tags, engine):
    alt_text = ''
    sound = '_play_ outlaw'

    if object == None:
        text = "There is no %s to unlock." % noun
    elif not object.locked:
        text = "The %s is already unlocked." % object.name
    else:
        if check_key(player, object.key) or 'script' in tags:
            object.locked = False

            if isinstance(object, engine_classes.Portal):
                for portal_name in engine._Rooms[object.coords].portals: # Unlock the portal from the other side as well
                    engine._Objects_Lock.acquire()
                    portal = engine._Objects[portal_name]
                    engine._Objects_Lock.release()

                    if portal.coords == player.coords:
                        portal.locked = False

            text = "You have unlocked the %s." % object.name
            alt_text = "%s has unlocked the %s." % (player.name, object.name)
            sound = '_play_ door_unlock' #NEEDS A VALID SOUND

            if 'script' in tags:
                text = alt_text = "The %s has unlocked." % object.name
        else:
            text = "You don't have the key to unlock the %s." % object.name

    text = '<sight>' + text + '</sight>'
    alt_text = '<sight>' + alt_text + '</sight>'

    messages = []
    messages.append((player.name, text))
    messages.append((player.name, sound))

    for alt_player in room.players:
        if alt_player != player.name:
            messages.append((alt_player, alt_text))

    return messages

def lock(room, player, object, noun, tags, engine):
    alt_text = ''
    sound = '_play_ outlaw'

    if object == None:
        text = "There is no %s to lock." % noun
    elif object.locked:
        text = "The %s is already unlocked." % object.name
    else:
        if check_key(player, object.key) or 'script' in tags:
            object.locked = True

            if isinstance(object, engine_classes.Portal):
                for portal in engine._Rooms[object.coords].portals.values(): # Lock the portal from the other side as well
                    if portal.coords == player.coords:
                        portal.locked = True

            text = "You have locked the %s." % object.name
            alt_text = "%s has locked the %s." % (player.name, object.name)
            sound = '_play_ door_lock' # NEEDS A VALID SOUND

            if 'script' in tags:
                text = alt_text = "The %s has locked." % object.name
        else:
            text = "You don't have the key to lock the %s." % object.name

    text = '<sight>' + text + '</sight>'
    alt_text = '<sight>' + alt_text + '</sight>'

    messages = []
    messages.append((player.name, text))
    messages.append((player.name, sound))

    for alt_player in room.players:
        if alt_player != player.name:
            messages.append((alt_player, alt_text))

    return messages

def inventory(room, player, object, noun, tags, engine):
    if len(player.items) > 0:
        text = "Inventory:"
        for item in player.items:
            text += "\n\t%s" % item

            if player.items[item] > 1:
                text += " x%d" % player.items[item]
    else:
        text = "Your inventory is empty."

    return [(player.name, text)]

def say(room, player, object, noun, tags, engine):
    text = "<sound> You say %s </sound>" % noun
    alt_text = "<sound> %s says %s </sound>" % (player.name, noun)

    messages = []
    messages.append((player.name, text))

    for alt_player in room.players:
        if alt_player != player.name:
            messages.append((alt_player, alt_text))

    return messages

def shout(room, player, object, noun, tags, engine):
    text = "<sound>You shout %s</sound>" % noun
    alt_text = "<sound>%s shouted %s</sound>" % (player.name, noun)
    sound = "_play_ shout_sound"
    
    bubble_coords = []
    for i in range(-2,3): # Create a 5x5 bubble around the player
        for j in range(-2,3):
            bubble_coords.append((player.coords[0]+i, player.coords[1]+j, player.coords[2], player.coords[3]))

    trimmed_bubble = []
    for coords in bubble_coords: # Remove coords from the bubble that don't have room with players in them
        if coords in engine._Rooms and len(engine._Rooms[coords].players) > 0:
            trimmed_bubble.append(coords)

    messages = []
    messages.append((player.name, text))
    messages.append((player.name, sound))
    for coords in trimmed_bubble:
        for alt_player in engine._Rooms[coords].players:
            if alt_player != player.name:
                messages.append((alt_player, alt_text))

    return messages

def damage(room, attacker, object, noun, tags, engine):
    messages = []

    for player_name in room.players:
        engine._Characters_Lock.acquire()
        player = engine._Characters[player_name]
        engine._Characters_Lock.release()

        difference = 0
        for person in attacker.affiliation: # Calculate the total difference between the player and the npc
            difference += -abs(attacker.affiliation[person] - player.affiliation[person])

        difference += 6 # Shift the difference over to put the mid point at 0 (this will need to be changed if the number of people changes)

#        if not player.senses['sound']: # Player can't hear very well, they take half damage
#            difference = difference/2

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

        death_msgs = ["You attempt suicide with a straight razor. You fail, but a quick trip to the mental hospital will fix you right up.",
                      "You cower in the corner of the room, rocking back and forth chanting 'I will let you finish...Fo heezi, I will let you finish. The nice men come and take you to the mental hospital.",
                      "You pass out from trying to make sense of everything. You are taken to the mental hospital for a quick round of shock therapy."]

        if player.fih <= 0: # Check if the player has died
            text += "\nYour Faith in Humanity has reached 0."
            text += "\n%s" % random.choice(death_msgs)

            # Reset player
            player.fih = 30
            player.coords = (1,1,1,0)
            room.players.remove(player.name) # Remove player from room
            engine._Rooms[(1,1,1,0)].players.append(player.name) # Add player to new room
            text += "\n%s" % get_room_text(player.name, (1,1,1,0), engine)    # Send the room description
            messages.append((player.name, '_play_ death'))    # Send the death sound

        messages.append((player.name, text))

    return messages

def lol(room, player, object, noun, tags, engine, modifier = 1):
    # Player upvotes a room or NPC
    if noun == 'room':
        if player.vote_history.get(room.id, 0) != modifier:
            room.score += modifier
            player.vote_history[room.id] = modifier
            text = "You have voted for the room."
        else:
            text = "You have already voted for this room."
    else:
        engine._Characters_Lock.acquire()
        if noun in engine._Characters and isinstance(engine._Characters[noun], engine_classes.NPC):
            if engine._Characters[noun].coords == player.coords:    # Verify in the same room
                if player.vote_history.get(noun, 0) != modifier:
                    engine._Characters[noun].score += modifier
                    player.vote_history[noun] = modifier
                    text = "You have voted for %s." % noun.title()
                else:
                    text = "You have already voted for %s." % noun.title()
            else:
                text = "You can't vote for a person in a different room."
        else:
            text = "You can't vote for that person."
        engine._Characters_Lock.release()

    messages = []
    messages.append((player.name, text))

    return messages

def boo(room, player, object, noun, tags, engine):
    # Player downvotes a room or NPC
    return lol(room, player, object, noun, tags, engine, modifier=-1)

def bad_command(room, player, object, noun, tags, engine):
    messages = []
    messages.append((player.name, "That is not a valid command."))
    messages.append((player.name, '_play_ outlaw'))

    return messages
############# SCRIPT METHODS ##########
def script_delay(player, script, engine):
    # Runs the remainder of a script after a delay
    for n, action in enumerate(script):
        verb = action[0]
        noun = action[1]
        delay = action[2]

        if delay > 0: # There is a delay for this script, spin off a timer thread
            script[n] = (script[n][0],  script[n][1], 0) # Set delay to zero so it doesn't spin off another timer
            timer = threading.Timer(float(delay), script_delay, args=[player, script[n:], engine]) # Start a timer to run the remainder of the script in 'delay' seconds
            timer.start()
            break
        else:
            command = (player.name, verb + ' ' + noun, ['script'])
            engine.put_commands([command]) # Push the command to the command queue

def reveal(room, player, object, noun, tags, engine):
    # Reveals a hidden object
    messages = []
    sound = "_play_ reveal_sound"
    if object != None:
        object.hidden = False
        text = "<sight>A %s appears in the room.</sight>" % object.name

        for player in room.players:
            messages.append((player, text))
            messages.append((player, sound))

    return messages

def hide(room, player, object, noun, tags, engine):
    # Hides an object
    messages = []
    sound = "_play_ reveal_sound"
    if object != None:
        object.hidden = True
        text = "<sight>The %s disappears from the room.</sight>" % object.name

        for player in room.players:
            messages.append((player, text))
            messages.append((player, sound))
    return messages

def add_status_effect(room, player, object, noun, tags, engine):
    if noun in player.sense_effects:
        player.sense_effects[noun] += 1
    else:
        player.sense_effects[noun] = 1

    return []

def lose_status_effect(room, player, object, noun, tags, engine):
    if noun in player.sense_effects:
        player.sense_effects[noun] -= 1

    if player.sense_effects[noun] <= 0:
        del player.sense_effects[noun]

    return []