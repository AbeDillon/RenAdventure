import validator
import makeItems
import textwrap
import makeScripts


def makePortals():
##### *******************************************TO DO*******************************************************
    #    have script creator and insert it in bottom portion
    
    room_portals = []
    directions = ['north', 'south', 'east', 'west', 'up', 'down']

    # QTY TO CREATE
    print ""
    print textwrap.fill('How many portals would you like to create?  (max 6)')
    valid_qty = False
    while valid_qty == False:
        qty = raw_input('\n>')
        
        tryFlag = True
        try:
            qty = int(qty)
        except:
            print '\nYou must enter a number between 1 and 6.  Try again.'
            tryFlag = False
        
        if tryFlag == True:
            if qty > 0 and qty < 7:
                valid_qty = True
            else:
                print '\nYou must enter a number between 1 and 6.  Try again.'
        
    count = qty
    # PORTAL CREATION LOOP
    for i in range(0, qty):
        portal = {}  #dict for this door
        
        # GET ORIGINAL NAME
        print ""
        print textwrap.fill('What would you like to name this portal?  All of the portal names must be different in your room and across the entire game.', width=100).strip()
        original = False
        while original == False:    # create original name for portal
            name = raw_input('\n>').strip()
            if validator.original_name(name, validator.names) == True:  #  Check against list names in entire game
                print "\nSorry that name has already been used in the game.  Try Again."
            elif validator.original_name(name, room_portals) == True:
                print "\nSorry you have already used that name in this room.   Try Again."
            else:
                #make dictionary for door with name as key
                portal[name] = {}
                original = True  #  Set original to True to break out of validation loop

        # DIRECTION OF PORTAL
        print ''
        avail_directions = str(directions).replace("'", '').strip('[]')  #  Dynamic printable list of directions remaining
        print textwrap.fill('A portal is also defined by the direction it leads. Which direction do you want this door to lead?  %s .', width=100) %avail_directions
        # Loop to select available direction
        dir_avail = False
        while dir_avail == False:
            direction = raw_input('\n>').strip().lower()
            if direction not in directions: #  direction must be in list of available to be valid.
                print "\nThat is not an available direction.  Try again."
            else:
                #  write to portal dict
                portal[name]['direction'] = direction
                directions.remove(direction) #  remove direction selected from available directions to prevent duplicate
                dir_avail = True # break from direction loop

        # PRIMARY DESCRIPTION
        print ''
        print textwrap.fill('Enter a description for your portal.  This is a generalized description that players will see.', width=100).strip()
        # accept loop
        desc_accept = False
        while desc_accept == False:
            desc = raw_input('\n>')
            if len(desc) == 0:  # must contain something
                print "\nYour Description must conatain at least 1 character.  Try again."
            else:
                #copy to portal dict and break loop
                portal[name]['desc'] = desc
                desc_accept = True

        # INSPECTION DESCRIPTION
        print ""
        print textwrap.fill('The inspection description is what players will see when they give the inspect command on your door.  Enter '
                            'your inspection description now.', width=100).strip()
        # accept loop
        desc_accept = False 
        while desc_accept == False:
            inspect_desc = raw_input('\n>')
            if len(inspect_desc) == 0:  # must contain something
                print "\nYour Inspection Description must contain at least 1 character.  Try again."
            else:
                # Copy to portal Dict and break loop
                portal[name]['inspect_desc'] = desc
                desc_accept = True

        #  COORDINATES (WHERE DOOR SHOULD LEAD)
        player_coords = (0,0,0)
        #player_coords = engine.player.coords  # (3 part tuple format (x, y, z)
        #x = player_coords[0]
        #y = player_coords[1]
        #z = player_coords[2]
        x, y, z = player_coords  # thanks Abe
        
        #print ""
        #print textwrap.fill('The portal must lead to a coordinate address which is a 3 part address (x, y, z).  If you would like you can specify an '
        #                     'address that your portal takes you to.  If you want us to set it to the default address according to the direction '
        #                     'your door leads, simply answer no.  Would you like to assign a special address to your door?  (Yes or No)', width = 100).strip()
        # ans = validator.validYesNo()
        # if ans == 'no':
        if direction == 'north':
            portal_coords = (x, y + 1, z) 
        elif direction == 'south':
            portal_coords = (x, y-1, z)
        elif direction == 'west':
            portal_coords = (x-1, y, z)
        elif direction == 'east':
            portal_coords = (x+1, y, z)
        elif direction == 'up':
            portal_coords = (x, y,z+1)
        elif direction == 'down':
            portal_coords = (x,y,z-1)
        #  write to portal dict
        print '\n****TEST COORDINATES USED AS BASE CHANGE UNCOMMENT CODE TO USE DYNAMIC PLAYER LOCATION****'
        print portal_coords, 'DELETE OR COMMENT THESE OUT LATER?!'
        portal[name]['coords'] = portal_coords  #   Could use some sort of default algorithm here (ie if direction north (x+1, y, z) from room coords)
        print '\nDefault coordinates assigned according to direction chosen.'
        # if ans == 'yes' or ans == 'y':
        #     print '\nEnter your 3 part coordinates seperated by a space. For example...  12 4 1'
        #     valid_coords = False
        #     while valid_coords == False:
        #         coords = raw_input('\n>')
        #         coords = coords.strip().split()
        #         if validator.validate_coords(coords) == True:
        #             good_coords = (int(coords[0]), int(coords[1]), int(coords[2]))
        #             portal[name]['coords'] = good_coords
        #             valid_coords = True # break out of validation loop.
        #         else:
        #             print '\nThe Coordinates you entered are not valid for the reason stated above.  Try Again.'
        
        #  DOOR LOCKED
        print ""
        print textwrap.fill('Your door can be locked or unlocked which can then be opened using a key or other scripted method adding to the '
                            'puzzle-type gameplay.  Remember, we do want players to be able to move about the map somewhat freely so please be '
                            'discerning about locking portals.  DO YOU WANT TO LOCK THIS DOOR? (Yes or No)', width=100).strip()
        ans = validator.validYesNo() # returns only a yes or no
        if ans == 'yes':
            lock_state = True
        else:
            lock_state = False
        # write to portal dict
        portal[name]['locked'] = False

        #  KEY
        print ""
        print textwrap.fill('Portals can have a KEY (which can be any item) associated with them that will lock or unlock the door.  '
                            'Here you can (1) name an existing key that will unlock it, (2) create a KEY that will unlock it, '
                            'or (3) not associate a KEY at all.  Which would '
                            'you like to do? (1, 2, or 3)', width=100).strip()
        # valid answer loop
        valid_ans = False
        while valid_ans == False:
            ans = raw_input('\n>').strip().lower()
            tryFlag = True
            try:  #    cast as an integer if no error continue
                ans = int(ans)
            except:
                tryFlag = False
                print "\nYour response must be a 1, 2 or 3.  Try again."    
            
            if tryFlag == True:                
                # player wants to name key
                if ans == 1:
                    print ""
                    print textwrap.fill('Enter the NAME of the key you want to open the door.  Names are not case sensitive.', width=100).strip()
                    valid_key = False
                    while valid_key == False:
                        key = raw_input('\n>').strip().lower()
                        if validator.validate_name(key, validator.names) == True:
                            valid_key = True
                            valid_ans = True # break both loops
                        else:
                            print '\nThat key does not exist.  Try again.'
                # player wants to build key
                elif ans == 2:
                    key = makeItems.makeItem()
                    valid_ans = True  # break both loops
                # Do not assign key
                elif ans == 3:
                    key = None
                    valid_ans = True # break both loops
                else:
                    print "\nYour response must be a 1, 2 or 3.  Try again."
        # write key to portal dict
        portal[name]['key'] = key
            
        #  HIDDEN?
        print ""
        print textwrap.fill('Your portal can be hidden or visible.  Would you like your portal to be HIDDEN? (Yes or No)', width=100).strip()
        ans = validator.validYesNo()
        if ans == 'yes':
            hidden_state = True
        elif ans == 'no':
            hidden_state = False
        # write hidden state to dict
        portal[name]['hidden']  = hidden_state
        
        # SCRIPTS        
        print ""
        print textwrap.fill('Scripts can be written that will override the commands given upon your portal.  For example unlock door could cause '
                            'another door in the room to unlock or be revealed.  This is where things can get really interesting.  Would you like to '
                            'build any scripts for this portal?', width=100).strip()
        ans = validator.validYesNo()
        if ans == 'yes':
            scripts = makeScripts.makeScripts()
        if ans == 'no':
            scripts = {}
        # write scripts to portal dict
        portal[name]['scripts'] = scripts        
        
        # INSTANTIATE PORTAL
        tryFlag = True
        try:
            print textwrap.fill('COMMENTED OUT PORTAL INSTANTIATION uncomment before live use', width=100)
            #engine.Portal(name, desc, inspect_desc, portal_coords, scripts = scripts, locked = lock_state, hidden = hidden_state, key = key )
        except:
            print "\nSomething has gone wrong in your portal creation.  Sorry but you will have to try again."
            #  Need better error handling    
            tryFlag = False
        if tryFlag == True:
            print textwrap.fill('Congratultions your ' + name + ' portal has been built!')
            # append name to master list of names
            validator.names.append(name)
            # append name to portal list
            validator.portal_list.append(name)
            # append portal dict to room portals list
            room_portals.append(portal)
            count -= 1
            if count > 1:                
                print '\nYou have ' + str(count) + ' more portals to make.'
            elif count == 1:
                print '\nNow let\'s finish up that last portal'
            elif count == 0:
                print'\nBe Thankful!  You have finished the portals section!'
    # return list of dicts with portal attributes.  Do not want to instantiate until time room is instantiated as portals should be linked to rooms strictly
    return room_portals 

if __name__ == "__main__":
    makePortals()        