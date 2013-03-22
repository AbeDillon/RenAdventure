#Room maker?

import engine
import loader

room_desc = ''
room_portals = []
room_containers = []
room_items = []

avail_items = []


def initiate_maker():

    print "Welcome, this room is not yet built."

    ans = raw_input('Would you like to make this room?\r\n').lower()

    if ans == 'y' or ans == 'yes': #initiate room building.

        make_room()

    else: #No or other answer, accept as no for now?
        pass
        #Move player coords back one room, exit maker


def make_room():
    global room_desc

    print "Rooms have a description, portals, containers and items"

    desc = raw_input("Please enter a description for your room:\r\n")

    if desc != '':
        room_desc = desc
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

            #Eventually will have to check if this name already exists.

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

            loc = (-1,-1,-1) #Use for non-made room? ###################### Needs to be an identifier for having the location presently "undefined" as where these go is unknown.

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

            
            
            if i == 0: #First door
                if not is_locked and not is_hidden and not has_script: #Basic.
                    portal_0 = engine.Portal(name, direction, door_desc, inspect_desc, loc)
                    room_portals.append(portal_0)
                    
                elif not is_locked and not is_hidden and has_script: #Just script
                    portal_0 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script)
                    room_portals.append(portal_0)

                elif not is_locked and is_hidden and not has_script: #Just is hidden
                    portal_0 = engine.Portal(name, direction, door_desc, inspect_desc, loc, hidden=True)
                    room_portals.append(portal_0)

                elif is_locked and not is_hidden and not has_script: #Just locked
                    portal_0 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, key = key_id)
                    room_portals.append(portal_0)

                elif not is_locked and is_hidden and has_script: #Hidden with script:
                    portal_0 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script, hidden = True)
                    room_portals.append(portal_0)

                elif is_locked and not is_hidden and has_script: #Locked with script:
                    portal_0 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts=script, locked = True, key = key_id)
                    room_portals.append(portal_0)

                elif is_locked and is_hidden and not has_script: #Locked and hidden:
                    portal_0 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, hidden = True, key = key_id)
                    room_portals.append(portal_0)

                else:
                    portal_0 = engine.Portal(name, direciton, door_desc, inspect_desc, loc, scripts=script, locked=True, hidden=True, key=key_id)
                    room_portals.append(portal_0)


            elif i==1: #Second door
                if not is_locked and not is_hidden and not has_script: #Basic.
                    portal_1 = engine.Portal(name, direction, door_desc, inspect_desc, loc)
                    room_portals.append(portal_1)
            
                elif not is_locked and not is_hidden and has_script: #Just script
                    portal_1 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script)
                    room_portals.append(portal_1)

                elif not is_locked and is_hidden and not has_script: #Just is hidden
                    portal_1 = engine.Portal(name, direction, door_desc, inspect_desc, loc, hidden=True)
                    room_portals.append(portal_1)

                elif is_locked and not is_hidden and not has_script: #Just locked
                    portal_1 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, key = key_id)
                    room_portals.append(portal_1)

                elif not is_locked and is_hidden and has_script: #Hidden with script:
                    portal_1 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script, hidden = True)
                    room_portals.append(portal_1)

                elif is_locked and not is_hidden and has_script: #Locked with script:
                    portal_1 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts=script, locked = True, key = key_id)
                    room_portals.append(portal_1)

                elif is_locked and is_hidden and not has_script: #Locked and hidden:
                    portal_1 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, hidden = True, key = key_id)
                    room_portals.append(portal_1)

                else:
                    portal_1 = engine.Portal(name, direciton, door_desc, inspect_desc, loc, scripts=script, locked=True, hidden=True, key=key_id)
                    room_portals.append(portal_1)


            elif i==2: #Third door
                if not is_locked and not is_hidden and not has_script: #Basic.
                    portal_2 = engine.Portal(name, direction, door_desc, inspect_desc, loc)
                    room_portals.append(portal_2)
            
                elif not is_locked and not is_hidden and has_script: #Just script
                    portal_2 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script)
                    room_portals.append(portal_2)

                elif not is_locked and is_hidden and not has_script: #Just is hidden
                    portal_2 = engine.Portal(name, direction, door_desc, inspect_desc, loc, hidden=True)
                    room_portals.append(portal_2)

                elif is_locked and not is_hidden and not has_script: #Just locked
                    portal_2 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, key = key_id)
                    room_portals.append(portal_2)

                elif not is_locked and is_hidden and has_script: #Hidden with script:
                    portal_2 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script, hidden = True)
                    room_portals.append(portal_2)

                elif is_locked and not is_hidden and has_script: #Locked with script:
                    portal_2 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts=script, locked = True, key = key_id)
                    room_portals.append(portal_2)

                elif is_locked and is_hidden and not has_script: #Locked and hidden:
                    portal_2 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, hidden = True, key = key_id)
                    room_portals.append(portal_2)

                else:
                    portal_2 = engine.Portal(name, direciton, door_desc, inspect_desc, loc, scripts=script, locked=True, hidden=True, key=key_id)
                    room_portals.append(portal_2)



            elif i==3: #Fourth door
                if not is_locked and not is_hidden and not has_script: #Basic.
                    portal_3 = engine.Portal(name, direction, door_desc, inspect_desc, loc)
                    room_portals.append(portal_3)
            
                elif not is_locked and not is_hidden and has_script: #Just script
                    portal_3 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script)
                    room_portals.append(portal_3)

                elif not is_locked and is_hidden and not has_script: #Just is hidden
                    portal_3 = engine.Portal(name, direction, door_desc, inspect_desc, loc, hidden=True)
                    room_portals.append(portal_3)

                elif is_locked and not is_hidden and not has_script: #Just locked
                    portal_3 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, key = key_id)
                    room_portals.append(portal_3)

                elif not is_locked and is_hidden and has_script: #Hidden with script:
                    portal_3 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script, hidden = True)
                    room_portals.append(portal_3)

                elif is_locked and not is_hidden and has_script: #Locked with script:
                    portal_3 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts=script, locked = True, key = key_id)
                    room_portals.append(portal_3)

                elif is_locked and is_hidden and not has_script: #Locked and hidden:
                    portal_3 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, hidden = True, key = key_id)
                    room_portals.append(portal_3)

                else:
                    portal_3 = engine.Portal(name, direciton, door_desc, inspect_desc, loc, scripts=script, locked=True, hidden=True, key=key_id)
                    room_portals.append(portal_3)

            elif i==4: #Fifth door
                if not is_locked and not is_hidden and not has_script: #Basic.
                    portal_4 = engine.Portal(name, direction, door_desc, inspect_desc, loc)
                    room_portals.append(portal_4)
            
                elif not is_locked and not is_hidden and has_script: #Just script
                    portal_4 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script)
                    room_portals.append(portal_4)

                elif not is_locked and is_hidden and not has_script: #Just is hidden
                    portal_4 = engine.Portal(name, direction, door_desc, inspect_desc, loc, hidden=True)
                    room_portals.append(portal_4)

                elif is_locked and not is_hidden and not has_script: #Just locked
                    portal_4 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, key = key_id)
                    room_portals.append(portal_4)

                elif not is_locked and is_hidden and has_script: #Hidden with script:
                    portal_4 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script, hidden = True)
                    room_portals.append(portal_4)

                elif is_locked and not is_hidden and has_script: #Locked with script:
                    portal_4 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts=script, locked = True, key = key_id)
                    room_portals.append(portal_4)

                elif is_locked and is_hidden and not has_script: #Locked and hidden:
                    portal_4 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, hidden = True, key = key_id)
                    room_portals.append(portal_4)

                else:
                    portal_4 = engine.Portal(name, direciton, door_desc, inspect_desc, loc, scripts=script, locked=True, hidden=True, key=key_id)
                    room_portals.append(portal_4)

            elif i==5: #Sixth door
                if not is_locked and not is_hidden and not has_script: #Basic.
                    portal_5 = engine.Portal(name, direction, door_desc, inspect_desc, loc)
                    room_portals.append(portal_5)
            
                elif not is_locked and not is_hidden and has_script: #Just script
                    portal_5 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script)
                    room_portals.append(portal_5)

                elif not is_locked and is_hidden and not has_script: #Just is hidden
                    portal_5 = engine.Portal(name, direction, door_desc, inspect_desc, loc, hidden=True)
                    room_portals.append(portal_5)

                elif is_locked and not is_hidden and not has_script: #Just locked
                    portal_5 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, key = key_id)
                    room_portals.append(portal_5)

                elif not is_locked and is_hidden and has_script: #Hidden with script:
                    portal_5 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts = script, hidden = True)
                    room_portals.append(portal_5)

                elif is_locked and not is_hidden and has_script: #Locked with script:
                    portal_5 = engine.Portal(name, direction, door_desc, inspect_desc, loc, scripts=script, locked = True, key = key_id)
                    room_portals.append(portal_5)

                elif is_locked and is_hidden and not has_script: #Locked and hidden:
                    portal_5 = engine.Portal(name, direction, door_desc, inspect_desc, loc, locked = True, hidden = True, key = key_id)
                    room_portals.append(portal_5)

                else:
                    portal_5 = engine.Portal(name, direciton, door_desc, inspect_desc, loc, scripts=script, locked=True, hidden=True, key=key_id)
                    room_portals.append(portal_5)

    ans = raw_input('Would you like this room to have a container?\r\n').lower() #Presently only allows 1 container to be made.

    if ans == 'y' or ans == 'yes':
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
        ans = raw_input('Would you like this chest to be locked?\r\n').lower()

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
                    cont_items.append(ans)
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
            

    ans = raw_input('Would you like to add items to this room?\r\n').lower()

    if ans == 'y' or ans == 'yes':
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


    room = engine.Room(room_desc, portals = room_portals, containers = room_containers, items = room_items) #Make the room.
    test = raw_input('Please enter the 3 parts of the tuple for the room in form "x y z":\r\n')

    vals = test.split()

    coords = (int(vals[0]), int(vals[1]), int(vals[2]))
    
    loader.save_room(room, coords)

    #Send the room in?

    print 'The room description is:\r\n %s' % room.desc
    print 'The following portals are in this room:'

    for portal in room.portals:
        print "Name = %s, direction = %s, desc = %s, \r\ninspect_desc = %s, scripts = %s, \r\nlocked = %s, hidden = %s, key = %s" % (room.portals[portal].name, room.portals[portal].direction, room.portals[portal].desc, room.portals[portal].inspect_desc, room.portals[portal].scripts, str(room.portals[portal].locked), str(room.portals[portal].hidden), room.portals[portal].key)
    print 'The following containers are in this room:'
    for container in room.containers:
        print 'Name = %s, desc = %s, inspect_desc = %s, \r\nscripts = %s, \r\nlocked = %s, hidden = %s, key =%s' % (room.containers[container].name, room.containers[container].desc, room.containers[container].inspect_desc, room.containers[container].scripts, str(room.containers[container].locked), str(room.containers[container].hidden), room.containers[container].key)

    print 'The following items are in this room:'
    for item in room.items:
        print 'Name = %s' % room.items[item].name

    
    

initiate_maker()

    
raw_input('Finished with program. Hit enter to exit.')
