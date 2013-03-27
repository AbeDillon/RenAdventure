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
room_containers = []

def makeContainer():
##### *******************************************TO DO*******************************************************
    #  all containers in the room
   
        
    #  individual container attributes
    container = {}
    
    # Create original name for container
    print ""
    print textwrap.fill('What would you like to name this container?  All names in your room and the game need to be different.', width=100)
    
    original = False
    while original == False:    # create original name for container
        name = raw_input('\n>').strip()
        if validator.original_name(name, validator.names) == False:  #  Check against list of containers created in entire game
            print "Sorry, that name has already been used by someone else.  Try Again."
        elif validator.original_name(name, room_containers) == False:  #check against list in this newly created containers.
            print "You have already created a container with that name.  Try again."
        else:
            container[name] = {}
            original = True  #  Set original to True to break out of validation loop
    
    # get user descriptions
    print ''
    print textwrap.fill('Enter a description for your container.  This is a generalized description that players will see.', width = 100).strip()

    # loop to set General Description - Verify/Validate here
    desc_accept = False
    while desc_accept == False:
        desc = raw_input('\n>')
        if len(desc) == 0: # must contain something
            print "\nYour Description cannot be empty.  Try again."
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
            container[name]['inspect_desc'] = inspect_desc
            desc_accept = True
        else:
            print "\nYour Inspection Description cannot be empty.  Try again."            

    #  assign container Lock State
    print ""
    print textwrap.fill('Your container can be locked or unlocked which can then be opened using a key or other scripted method adding to the '
                        'puzzle-type gameplay.  Do you want to lock this container? (Yes or No)', width=100).strip()
    valid_ans = False
    while valid_ans == False:
        ans = raw_input('\n>').strip().lower()
        if ans == 'yes' or ans == 'y':
            container[name]['locked'] = True
            valid_ans = True
        elif ans == 'no' or ans == 'n':
            container[name]['locked'] = False
            valid_ans = True
        else:
            print '\nYour Answer must be yes or no.  Try Again.'
    
    #  Define Key for container 
    
    print ""
    print textwrap.fill('Containers can have a key (which can be any item) associated with them that will lock or unlock it.  '
                        'Here you can (1) name an existing key that will unlock it, (2) create a key that will unlock it, '
                        'or (3) not associate a key at all.  Which would you like to do? (1, 2, or 3)', width=100).strip()
    valid_ans = False
    while valid_ans == False:  # make sure answer is 1, 2, or 3
        ans = raw_input('\n>').strip().lower()
        try:  #    cast as an integer if no error continues rest of error checking
            ans = int(ans)
            if ans == 1: # player wants to name a key
                print ""
                print textwrap.fill('Enter the name of the key you want to open the container.  Names are not case sensitive.', width=100).strip()
                valid_key = False
                while valid_key == False:
                    key = raw_input('\n>').strip().lower()
                    # add compare key name to items on the map to verify the key name then build if necessary
                    if validator.validate_name(key, validator.names) == True:
                        valid_ans = True
                        valid_key = True
                    else:
                        print 'That key does not exist.  Try again.'
            elif ans == 2: #  Player wants to build a key
                # function for building key not complete
                #key = makeItems.makeItem()
                key = "made key"
                valid_ans = True
            elif ans == 3:  # do not assign a key
                key = None
                valid_ans = True
            else:
                print "Your response must be a 1, 2 or 3.  Try again."
            
        except:
            print "Your response must be a 1, 2 or 3.  Try again."
            pass
    
    container[name]['key'] = key

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
    print textwrap.fill('\n\n\nNeed script builder!', width=100).strip()
    scripts = {}
    #  Drop script building here later
    container[name]['script'] = scripts
    
    
    room_containers.append(container)
    print room_containers
    
    
    
    print""
    print textwrap.fill('You have built the ' + name + ' container.  Do you want to build another? (Yes or No)', width=100).strip()
    valid_ans = False
    while valid_ans == False:
        ans = raw_input('\n>').lower().strip()
        if ans == 'yes' or ans == 'y':
            makeContainer()
            valid_ans = True
        elif ans == 'no' or ans == 'n':
            return room_containers
        else:
            print '\nYour answer must be Yes or No.  Try  Again'

#makeContainer()   