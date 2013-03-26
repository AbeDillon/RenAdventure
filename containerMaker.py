import validator
import textwrap

'''
- Name
- Description (for printing in a room)
- Inspect Description (for looking at the item)
- Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
- Locked (bool)
- Key
- Hidden (bool)
'''


def makeContainers():
##### *******************************************TO DO*******************************************************
    #  all containers in the room
    room_containers = []
    #  temporary list for testing
    global_containers = []
    
    #  individual container attributes
    container = {}
    
    # Create original name for container
    original = False
    while original == False:    # create original name for container
        name = raw_input('What would you like to name this container?  All of the container names in your room must be different.\n>  ').strip()
        if validator.validate_name(name, global_containers) == False:  #  Check against list of containers created in entire game
            print "Sorry that name has already been used by someone else."
        if validator.validate_name(name, room_containers) == False:  #check against list in this newly created containers.
            print "You have already created a container with that name.  Try again."
        else:
            container[name] = {}
            room_containers.append(name)
            original = True  #  Set original to True to break out of validation loop
    
    # get user descriptions
    print ''
    print textwrap.fill('Enter a description for your container.  This is a generalized description that players will see.', width = 100).strip()

    # loop to set General Description - Verify/Validate here
    desc_accept = False
    while desc_accept == False:
        desc = raw_input('\n>')
        if desc == None and desc == " ":  # must contain something
            print "Your Description cannot be empty.  Try again."
        else:
            container[name]['desc'] = desc
            desc_accept = True

    # Loop to set Inspection Description - Verify/Validate Here
    desc_accept = False
    print ""
    print textwrap.fill('The inspection description is what players will see when they give the inspect command on your container.  Enter '
                        'your inspection description now.', width=100).strip()
    while desc_accept == False:
        inspect_desc = raw_input('\n>')
        if len(inspect_desc) > 0:
            container[name]['inspect_desc'] = desc
            desc_accept = True
        else:
            print "Your Inspection Description cannot be empty.  Try again."            

    #  assign container Lock State
    print ""
    print textwrap.fill('Your container can be locked or unlocked which can then be opened using a key or other scripted method adding to the '
                        'puzzle-type gameplay.  Do you want to lock this container? (Yes or No)', width=100).strip()
    ans = raw_input('\n>').strip().lower()
    if ans == 'yes' or ans == 'y':
        container[name]['locked'] = True
    else:
        container[name]['locked'] = False

    #  Define Key for container BUT ONLY when the player has specified the container to be locked
    if container[name]['locked'] == True:
        print ""
        print textwrap.fill('You have chosen to lock this container.  You can (1) create a key that will unlock it, (2) create a script that will '
                            'unlock it or (3) just leave the container locked forever.  Which do you want to do? (1, 2 or 3)', width=100).strip()
        valid_ans = False
        while valid_ans == False:
            ans = raw_input('\n>').strip().lower()
            try:  #    cast as an integer if no error continues rest of error checking
                ans = int(ans)
                if ans == 1:
                    print ""
                    print textwrap.fill('Enter the name of the key you want to open the container.  Names are not case sensitive.', width=100).strip()
                    key = raw_input('\n>').strip().lower()
                    # add compare key name to items on the map to verify the key name then build if necessary
                    if len(key) > 0:
                        container[name]['key'] = key
                        print container[name]['key']
                        valid_ans = True
                    else:
                        print 'Key names must not be blank.  Try again.'
                elif ans == 2:
                #  *************************Need to handle user inputed scripts here
                    container[name]['key'] = 'script'
                    valid_ans = True
                elif ans == 3:
                    container[name]['key'] = None
                    valid_ans = True
                else:
                    print "Your response must be a 1, 2 or 3.  Try again."
            except:
                print "Your response must be a 1, 2 or 3.  Try again."
                pass

                #  Define hidden state of the container
    print ""
    print textwrap.fill('Your container can be hidden or visible.  Would you like your container to be hidden? (Yes or No)', width=100).strip()
    valid_ans = False
    while valid_ans == False:
        ans = raw_input('\n>').lower().strip()
        if ans == 'yes' or ans == 'y':
            container[name]['hidden'] = True
            valid_ans = True
        elif ans == 'no' or ans == 'n':
            container[name]['hidden'] = False
            valid_ans = True
        else:
            print '\nYour answer must be Yes or No.'
            #  Enter the scripts here
    print ""
    print textwrap.fill('Need script builder!')
    #  script = {}
    #  Drop script building here later