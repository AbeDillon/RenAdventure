import validator
import textwrap
import engine
import makeItems

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
container_items = []

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
        if validator.original_name(name, validator.names) == True:  #  Check against list of containers created in entire game
            print "Sorry, that name has already been used by someone else.  Try Again."
        elif validator.original_name(name, room_containers) == True:  #check against list in this newly created containers.
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
            print "\nYour Inspection Description cannot be blank.  Try again."            

    #  assign container Lock State
    print ""
    print textwrap.fill('Your container can be locked or unlocked which can then be opened using a key or other scripted method adding to the '
                        'puzzle-type gameplay.  Do you want to lock this container? (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        lock_state = True
        container[name]['locked'] = True
    elif ans == 'no':
        lock_state = False
        container[name]['locked'] = False

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
                print textwrap.fill('Enter the name of the key (name of item) you want to open the container.  Names are not case sensitive.', width=100).strip()
                valid_key = False
                while valid_key == False:
                    key = raw_input('\n>').strip().lower()
                    # add compare key name to items on the map to verify the key name then build if necessary
                    if validator.validate_name(key, validator.names) == True: # name is in list
                        valid_ans = True
                        valid_key = True
                    else:
                        print 'That key does not exist.  Try again.'
            elif ans == 2: #  Player wants to build a key
                key = makeItems.makeItem[0]  # in Item builder it is possible to build more than 1 item but Items that are built are appended to list
                # only allow for first item created to be the key
                valid_ans = True
            elif ans == 3:  # do not assign a key
                key = None
                valid_ans = True
            else:
                print "Your response must be a 1, 2 or 3.  Try again."
            
        except:
            print "Your response must be a 1, 2 or 3.  Try again."
    
    container[name]['key'] = key

    #  Define hidden state of the container
    
    print ""
    print textwrap.fill('Your container can be hidden or visible.  Would you like your container to be hidden? (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes' or ans == 'y':
        hidden_state = True
        container[name]['hidden'] = True
    elif ans == 'no' or ans == 'n':
        hidden_state = False
        container[name]['hidden'] = False
    else:
        print '\nYour answer must be Yes or No.'
    

    #  Add items to container
    print ""
    print textwrap.fill('You can place items in the container, each container can hold as many items as you wish.  '
                        'Here you can (1) add an existing item by name, (2) create a new item, '
                        'or (3) not add an at all.  Which would you like to do? (1, 2, or 3)', width=100).strip()
    items_done = False
    while items_done == False:  # make sure answer is 1, 2, or 3
        ans = raw_input('\n>').strip().lower()
        try:  #    cast as an integer if no error continue
            ans = int(ans)
            if ans == 1: # player wants to name a container
                print ""
                print textwrap.fill('Enter the name of the item.  Names are not case sensitive.', width=100).strip()
                valid_item = False
                while valid_item == False:
                    item_name = raw_input('\n>').strip().lower()
                    # add compare key name to items on the map to verify the key name then build if necessary
                    if validator.validate_name(item_name, validator.names) == True:
                        #append to room container list
                        container_items.append(item_name) #append name to room_containers list
                        print "Do you want to add another item by name?  (yes or no)"
                        ans = validator.validYesNo() # returns a yes or no
                        if ans == 'yes':
                            print '\nEnter the name of the next item.'
                        elif ans == 'no':
                            print textwrap.fill('Now do you want to (1) add another item by name, (2) create an item, '
                                                'or (3) I\'m done with items.  (1, 2, or 3)', width=100).strip()
                            valid_item = True
                    else:
                        print 'That item does not exist.  Try again.'
            elif ans == 2: #  Player wants to build a container
                items = makeItems.makeItem()  # get room containers returned from make containers function
                for item in items:
                    container_items.append(item)   # append each container name (containers will have been instantiated in called function.
                print textwrap.fill('Now do you want to (1) add another item by name, (2) create an item, '
                                    'or (3) I\'m done with items.  (1, 2, or 3)', width=100).strip()
            elif ans == 3:  # done
                items_done = True
            else:
                print "Your response must be a 1, 2 or 3.  Try again."
            
        except:
            print "Your response must be a 1, 2 or 3.  Try again."



    #  Enter the scripts here
    
    print ""
    print textwrap.fill('\n\n\nNeed script builder!', width=100).strip()
    scripts = {}
    #  Drop script building here later
    container[name]['script'] = scripts
    
    #  Instantiate the new container
    try:
        engine.Container(name, desc, inspect_desc, scripts, locked = lock_state, key = key, hidden = hidden_state, items = container_items )
    except:
        #need error handling!!
        pass
    
    #  Append container name to list
    room_containers.append(name)
    
    print '\n', room_containers
    
    # Finished??    
    print""
    print textwrap.fill('You have built the ' + name + ' container.  Do you want to build another? (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        makeContainer()
    elif ans == 'no':
        return room_containers

if __name__ == '__main__':
    makeContainer()   