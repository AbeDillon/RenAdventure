#Room maker?

import engine
import loader

room_desc = ''
room_portals = []
room_containers = []
room_items = []

avail_items = {}


def initiate_maker():
    global room_desc
    global room_portals
    global room_containers
    global room_items

    print "Welcome, this room is not yet built."

    while 1:

        ans = raw_input('Would you like to make a room or items? (or type "done" to exit)\r\n').lower()

        if ans == 'room' or ans == 'a room': #initiate room building.

            make_room() #Make the room. After that, clear out the cache of other things so another room could be made.
            room_desc = ''
            room_portals = []
            room_containers = []
            room_items = []

        elif ans == 'items' or ans == 'item': #Initiate item building
            make_items()
        elif ans == 'done':
            break
        else:
            print 'That is not a valid choice'

def make_items():
    while 1:
        has_script = False
        is_port = False
        is_hidden = False
        
        print 'Making items.'
        name = raw_input('What would you like to name this item?(or type "done" to end)\r\n')

        if name == 'done': #Done
            break
        else:
            print "Items have the following attributes:\r\n\tdescription, \r\n\tinspection_description,\r\n\tscripts,\r\n\tportable, \r\n\thidden"

            desc = raw_input('Please enter a description for this item:\r\n')

            insp_desc = raw_input('Please enter an inspection description too:\r\n')

            ans = raw_input('Would you like to add scripting to this?\r\n').lower

            if ans == 'yes' or ans == 'y':
                has_script = True
                print "The format for scripts is: \r\n\t {'verb': (('verb', 'noun'),('verb,'noun))}"

                script = raw_input('Please type your script out here:\r\n')
            ans = raw_input('Would you like this item to be portable?\r\n').lower()
            if ans == 'yes' or ans == 'y':
                is_port = True

            ans = raw_input('Would you like this item to be hidden?\r\n').lower()
            if ans == 'yes' or ans=='y':
                is_hidden = True

            if not has_script and not is_port and not is_hidden: #Basic
                item = engine.Item(name, desc, insp_desc)
            elif not has_script and not is_port and is_hidden: #Just hidden
                item = engine.Item(name, desc, insp_desc, hidden=True)
            elif not has_script and is_port and not is_hidden: #Just portable
                item = engine.Item(name, desc, insp_desc, portable=True)
            elif has_script and not is_port and not is_hidden: #Just script
                item = engine.Item(name, desc, insp_desc, scripts=script)
            elif not has_script and is_port and is_hidden: #Just no script:
                item = engine.Item(name, desc, insp_desc, portable=True, hidden=True)
            elif has_script and is_port and not is_hidden: #Just not hidden:
                item = engine.Item(name, desc, insp_desc, scripts=script, portable=True)
            elif has_script and not is_port and is_hidden: #Just not portable
                item = engine.Item(name, desc, insp_desc, scripts=script, hidden=True)
            else: #Is scripted, portable, and hidden
                item = engine.Item(name, desc, insp_desc, scripts=script, hidden=True, portable=True)


            avail_items[name] = item

def make_portals():
    try:
        cnt = int(raw_input("How many portals would you like this room to have? (max 6)\r\n"))
    except:
        pass
        #Failed make, exit?

    if cnt <= 6: #Is a valid amount
        dir_list = ['north', 'south', 'east', 'west', 'up', 'down']
        print "Portals have the following attributes:"
        print "\tName\r\n\tDirection (north, south, east, west, up and down)"
        print "\tDoor description\r\n\tInspection description"
        print "\tAction scripts\r\n\tLocked status\r\n\tA potential key\r\n\tAnd a hidden property"

        for i in range(0, cnt): #For the number of portals they want to make:
            has_script = False

            is_locked = False

            is_hidden = False

            print "Making portal %d" % (i+1)

            name = raw_input('What would you like to name this portal?\r\n').lower()

            #Eventually will have to check if this name already exists?

            print "The following directions are presently available for portals:"
            for direction in dir_list:
                print '\t',direction
            while 1:
                direction = raw_input('Which direction would you like this portal to go?\r\n').lower()
                if direction in dir_list: #Is a valid direction
                    dir_list.remove(direction) #Not any more though.
                    break
                else: #Not a valid direction
                    print "That is not an available direction."

            door_desc = raw_input("What general description would you like this portal to have?\r\n")

            print "When someone inspects a portal, a more detailed description is given."

            inspect_desc = raw_input("What inspection description would you like this portal to have?\r\n")

            ans = raw_input('Do you know the location of the room this portal points to? (as a tuple)\r\n')

            if ans == 'yes' or ans == 'y':
                location = raw_input('Please enter the tuple in the form x y z:\r\n')
                location = location.split()
                loc = (location[0], location[1], location[2]) #Make a tuple from the location

            else:

                loc = (0,0,0) #Use for non-made room? ###################### Needs to be an identifier for having the location presently "undefined" as where these go is unknown.

            print "Portals may have scripts which cause other things to happen."

            print "The format for scripts is: \r\n\t {'verb': (('verb', 'noun'),('verb,'noun))}"

            ans = raw_input('Would you like to make a special script for this portal?\r\n').lower()

            if ans == 'y' or ans == 'yes':

                script = raw_input('Please type your script out here:\r\n')
                has_script = True

            print "Portals may be locked or not."
            ans = raw_input('Would you like to have this portal be locked?\r\n')

            if ans == 'y' or ans=='yes':

                is_locked = True

                print "Locked portals mush have a key."

                key_id = raw_input('Please enter the name of the key this portal uses:\r\n')


            print "Portals may also be hidden or not hidden."

            ans = raw_input('Would you like this portal to be hidden?\r\n').lower()

            if ans == 'y' or ans == 'yes':
                is_hidden = True

            
            
            if not is_locked and not is_hidden and not has_script: #Basic.
                portal = engine.Portal(name, direction, door_desc, inspect_desc, loc)
                room_portals.append(portal)
                
            elif not is_locked and not is_hidden and has_script: #Just script
                portal = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script)
                room_portals.append(portal)

            elif not is_locked and is_hidden and not has_script: #Just is hidden
                portal = engine.Portal(name, direction, door_desc, inspect_desc, loc, hidden=True)
                room_portals.append(portal)

            elif is_locked and not is_hidden and not has_script: #Just locked
                portal = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, key = key_id)
                room_portals.append(portal)

            elif not is_locked and is_hidden and has_script: #Hidden with script:
                portal = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script, hidden = True)
                room_portals.append(portal)

            elif is_locked and not is_hidden and has_script: #Locked with script:
                portal = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts=script, locked = True, key = key_id)
                room_portals.append(portal)

            elif is_locked and is_hidden and not has_script: #Locked and hidden:
                portal = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, hidden = True, key = key_id)
                room_portals.append(portal)

            else:
                portal = engine.Portal(name, direciton, door_desc, inspect_desc, loc, scripts=script, locked=True, hidden=True, key=key_id)
                room_portals.append(portal)

def make_containers():
    ans = raw_input('Would you like this room to have containers?\r\n').lower() 

    if ans == 'y' or ans == 'yes':
        cnt = int(raw_input('How many containers would you like this room to have?\r\n'))
        for i in range(0, cnt):
            has_script = False
            is_locked = False
            is_hidden = False
            cont_items = []
            
            name = raw_input('What would you like this container to be called?\r\n')
            desc = raw_input('Please enter a description for your container:\r\n')
            inspect_desc = raw_input('Please enter a description to be provided upon inspection too:\r\n')

            print "The format for scripts is: \r\n\t {'verb': (('verb', 'noun'),('verb,'noun))}"

            ans = raw_input('Would you like to make a special script for this container?\r\n').lower()

            if ans == 'y' or ans == 'yes':

                script = raw_input('Please type your script out here:\r\n')
                has_script = True
            ans = raw_input('Would you like this container to be locked?\r\n').lower()

            if ans == 'y' or ans == 'yes':
                is_locked = True
                print 'Locked containers have a key which unlocks them.'
                key_id = raw_input("Please enter the ID of the key that unlocks this container:\r\n")

            ans = raw_input('Would you like this container to be hidden?\r\n').lower()

            if ans =='y' or ans=='yes':
                is_hidden = True

            if avail_items == []: #Empty list of items
                print 'There are presently no items which you may put in this container.'

            else: #List with some items
                print 'The following items are pre-defined and may be added to this container:'
                for item in avail_items:
                    print '\t',item
                while 1:
                    ans = raw_input('Which item would you like to add first? (or type "done" to end)\r\n').lower()
                    if ans == 'done':
                        break
                    elif ans in avail_items:
                        cont_items.append(avail_items[ans])
                    else:
                        print 'That is not a valid item'
            if not has_script and not is_locked and not is_hidden: #Basic
                container = engine.Container(name, desc, inspect_desc, items = cont_items)

            elif not has_script and not is_locked and is_hidden: #Just hidden
                container = engine.Container(name, desc, inspect_desc, items=cont_items, hidden=True)
            elif not has_script and is_locked and not is_hidden: #Just locked
                container = engine.Container(name, desc, inspect_desc, items=cont_items, locked=True, key = key_id)
            elif has_script and not is_locked and not is_hidden: #Just script
                container = engine.Container(name, desc, inspect_desc, items=cont_items, scripts = script)
            elif not has_script and is_locked and is_hidden: #Only no script
                container = engine.Container(name, desc, inspect_desc, items=cont_items, hidden=True, locked=True, key=key_id)
            elif has_script and not is_locked and is_hidden: #Only not locked
                container = engine.Container(name, desc, inspect_desc, items=cont_items, scripts=script, hidden=True)
            elif has_script and is_locked and not is_hidden: #Only not hidden
                container = engine.Container(name, desc, inspect_desc, items=cont_items, scripts=script, locked=True, key=key_id)
            else: #All are true
                container = engine.Container(name, desc, inspect_desc, items=cont_items, scripts=script, locked=True, hidden=True, key=key_id)

            room_containers.append(container)


def make_room():
    global room_desc

    print "Rooms have a description, portals, containers and items"

    desc = raw_input("Please enter a description for your room:\r\n")

    if desc != '':
        room_desc = desc

    make_portals()
    
    make_containers()
            

    ans = raw_input('Would you like to add items to this room?\r\n').lower()

    if ans == 'y' or ans == 'yes':
        if avail_items != []: #There are items to add.
            print 'The following items are available to be placed here:'
            for item in avail_items:
                print '\t',item
            while 1:
                ans = raw_input('Which item would you like to place here first? (or type "done" to end)\r\n').lower()

                if ans == 'done':
                    break
                elif ans in avail_items:
                    room_items.append(avail_items[ans])
                else:
                    print 'That is not a valid item'
        else:
            print "Sorry, there are presently no items you may add to this room."
            


    room = engine.Room(room_desc, portals = room_portals, containers = room_containers, items = room_items) #Make the room.
    test = raw_input('Please enter the 3 parts of the tuple for the room in form "x y z":\r\n') ###Only Temporary.

    vals = test.split()

    coords = (int(vals[0]), int(vals[1]), int(vals[2]))
    
    loader.save_room(room, coords)

    
###DEBUG CALLS
##    print 'The room description is:\r\n %s' % room.desc
##    print 'The following portals are in this room:'
##
##    for portal in room.portals:
##        print "Name = %s, direction = %s, desc = %s, \r\ninspect_desc = %s, scripts = %s, \r\nlocked = %s, hidden = %s, key = %s" % (room.portals[portal].name, room.portals[portal].direction, room.portals[portal].desc, room.portals[portal].inspect_desc, room.portals[portal].scripts, str(room.portals[portal].locked), str(room.portals[portal].hidden), room.portals[portal].key)
##    print 'The following containers are in this room:'
##    for container in room.containers:
##        print 'Name = %s, desc = %s, inspect_desc = %s, \r\nscripts = %s, \r\nlocked = %s, hidden = %s, key =%s' % (room.containers[container].name, room.containers[container].desc, room.containers[container].inspect_desc, room.containers[container].scripts, str(room.containers[container].locked), str(room.containers[container].hidden), room.containers[container].key)
##
##    print 'The following items are in this room:'
##    for item in room.items:
##        print 'Name = %s' % room.items[item].name

    
    

initiate_maker()

    
raw_input('Finished with program. Hit enter to exit.')
