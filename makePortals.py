import validator
import textwrap


global_portals = {}


def makePortals():
##### *******************************************TO DO*******************************************************
    #    1.    Lock portal that the player just walked through to get into this room.  Player should have only 5 portals that are able to be made.
    #    the door they just traveled through to get to the "empty room".  Player should always be able to turn around the direction they just
    #    came from to exit the room.  Perhaps the room can have a setting where the door locks as they come through and a puzzle needs to
    #    be solved to exit.  That could be up to the room creator???
    #    2.    Make way to set default coords for portals players create.
    #    3.    Handle User scripts in locked/ unlocked portion.
    room_portals = []
    directions = ['north', 'south', 'east', 'west', 'up', 'down']


    # How many should we create
    qty = int(raw_input('\nHow many portals would you like to create? (max 6)\n>  '))

    #Enter loop for each door in qty
    for i in range(0, qty):
        portal = {}     #    dictionary fot this portal

        # Create original name for room commented out global requirment at this time
        original = False
        while original == False:    # create original name for portal
            name = raw_input('What would you like to name this portal?  All of the portal names in your room must be different.\n>  ').strip()
            if validator.validate_name(name, global_portals) == False:  #  Check against list of portals created in entire game
                print "Sorry that name has already been used by someone else."
            if validator.validate_name(name, room_portals) == False:  #check against list in this newly created room.
                print "You have already created a portal with that name.  Try again."
            else:
                portal[name] = {}
                room_portals.append(name)
                original = True  #  Set original to True to break out of validation loop

        # get user desired direction
        print ''
        avail_directions = str(directions).replace("'", '').strip('[]')
        print textwrap.fill('A portal is also defined by the direction it leads. Which direction do you want this door to lead?  %s .', width=100) %avail_directions

        dir_avail = False
        while dir_avail == False:
            direction = raw_input('\n>').strip().lower()
            if direction not in directions: #  direction must be in list of available to be valid.
                print "\nThat is not a valid direction.  Try again.\n"
            else:
                portal[name]['direction'] = direction
                directions.remove(direction) #  remove direction selected from available directions to prevent duplicate
                dir_avail = True # break from direction loop

        # get user descriptions
        print ''
        print textwrap.fill('Enter a description for your portal.  This is a generalized description that players will see.', width=100).strip()

        # loop to set General Description - Verify/Validate here
        desc_accept = False
        while desc_accept == False:
            desc = raw_input('\n>')
            if desc == None and desc == " " :  # must contain something
                print "Your Description cannot be empty.  Try again."
            else:
                portal[name]['desc'] = desc
                desc_accept = True

        # Loop to set Inspection Description - Verify/Validate Here
        desc_accept = False #  Reset to false for new loop
        print ""
        print textwrap.fill('The inspection description is what players will see when they give the inspect command on your door.  Enter '
                            'your inspection description now.', width=100).strip()
        while desc_accept == False:
            inspect_desc = raw_input('\n>')
            if inspect_desc == None and inspect_desc == " " :  # must contain something
                print "Your Inspection Description cannot be empty.  Try again."
            else:
                portal[name]['inspect_desc'] = desc
                desc_accept = True

        print "Assign Coordinates!!!!!"

        #  Get Coordinates (for where door should lead)
        # print""
        # print textwrap.fill('The door must lead to a coordinate address which is a 3 part address (x, y, z).  If you would like you can specify an '
        #                     'address that your door takes you to.  If you want us to set it to the default address according to the direction '
        #                     'your door leads, simply answer no.  Would you like to assign a address to your door?  (Yes or No)', width = 100).strip()
        # ans = raw_input('\n>').lower()
        # if ans == 'no' or ans == 'n':
        #     #### ******************************* TO DO*******************************************
        #     # We need define a function that will take the coordinates of the room and the direction of the door and create a default adress
        #     # That function should go here.  Assign default of 0,0,0 for now.
        #     portal[name]['coords'] = (0,0,0)  #   Could use some sort of default algorithm here (ie if direction north (x+1, y, z) from room coords)
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

        #  assign Door Lock State
        print ""
        print textwrap.fill('Your door can be locked or unlocked which can then be opened using a key or other scripted method adding to the '
                            'puzzle-type gameplay.  Remember, we do want players to be able to move about the map somewhat freely so please be '
                            'discerning about locking portals.  Do you want to lock this door? (Yes or No)', width=100).strip()
        ans = raw_input('\n>').strip().lower()
        if ans == 'yes' or ans == 'y':
            portal[name]['locked'] = True
        else:
            portal[name]['locked'] = False

        #  Define Key for Door BUT ONLY when the player has specified the door to be locked
        if portal[name]['locked'] == True:
            print ""
            print textwrap.fill('You have chosen to lock this door.  You can (1) create a key that will unlock it, (2) create a script that will '
                                'unlock it or (3) just leave the door locked forever.  Which do you want to do? (1, 2 or 3)', width=100).strip()
            valid_ans = False
            while valid_ans == False:
                ans = raw_input('\n>').strip().lower()
                try:  #    cast as an integer if no error continues rest of error checking
                    ans = int(ans)
                    if ans == 1:
                        print ""
                        print textwrap.fill('Enter the name of the key you want to open the door.  Names are not case sensitive.', width=100).strip()
                        key = raw_input('\n>').strip().lower()
                        # add compare key name to items on the map to verify the key name then build if necessary
                        if len(key) > 0:
                            portal[name]['key'] = key
                            print portal[name]['key']
                            valid_ans = True
                        else:
                            print 'Key names must not be blank.  Try again.'
                    elif ans == 2:
                    #  *************************Need to handle user inputed scripts here
                        portal[name]['key'] = 'script'
                        valid_ans = True
                    elif ans == 3:
                        portal[name]['key'] = None
                        valid_ans = True
                    else:
                        print "Your response must be a 1, 2 or 3.  Try again."
                except:
                    print "Your response must be a 1, 2 or 3.  Try again."
                    pass

                    #  Define hidden state of the door
        print ""
        print textwrap.fill('Your portal can be hidden or visible.  Would you like your portal to be hidden? (Yes or No)', width=100).strip()
        valid_ans = False
        while valid_ans == False:
            ans = raw_input('\n>').lower().strip()
            if ans == 'yes' or ans == 'y':
                portal[name]['hidden'] = True
                valid_ans = True
            elif ans == 'no' or ans == 'n':
                portal[name]['hidden'] = False
                valid_ans = True
            else:
                print '\nYour answer must be Yes or No.'
                #  Enter the scripts here
        print ""
        print textwrap.fill('Need script builder!')
        #  script = {}
        #  Drop script building here later