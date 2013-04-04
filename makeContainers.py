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


def makeContainer():
##### *******************************************TO DO*******************************************************
    #  dict for individual container attributes
    container = {}
    
    # ORIGINAL NAME
    print ""
    print textwrap.fill('What would you like to NAME this container?  All names in your room and the game need to be different.', width=100)
    # loop for originality
    original = False
    while original == False:    # create original name for container
        name = raw_input('\n>').strip()
        if validator.original_name(name, validator.names) == True:  #  Check against list of containers created in entire game
            print "\nSorry, that name has already been used by someone else.  Try Again."
        elif validator.original_name(name, room_containers) == True:  #check against list in this newly created containers.
            print "\nYou have already created a container with that name.  Try again."
        else:
            #container dict with name as key break loop
            container[name] = {}
            original = True
    
    # GENERAL DESCRIPTION
    print ''
    print textwrap.fill('Enter a DESCRIPTION for your container.  This is a generalized description that players will see.', width = 100).strip()

    # valid description loop
    desc_accept = False
    while desc_accept == False:
        desc = raw_input('\n>')
        if len(desc) == 0: # must contain something
            print "\nYour Description must contain at least 1 character.  Try again."
        else:
            container[name]['desc'] = desc
            desc_accept = True
            
    # INSPECTION DESCRIPTION    
    print ""
    print textwrap.fill('The inspection description is what players will see when they give the inspect command on your container.  Enter '
                        'your INSPECTION DESCRIPTION now.', width=100).strip()
    # valid inspec description loop
    desc_accept = False
    while desc_accept == False:
        inspect_desc = raw_input('\n>')
        if len(inspect_desc) > 0: 
            container[name]['inspect_desc'] = inspect_desc
            desc_accept = True
        else:
            print "\nYour Inspection Description must contain at least 1 character.  Try again."            

    # LOCK CONTAINER
    print ""
    print textwrap.fill('Your container can be locked or unlocked which can then be opened using a key or other scripted method adding to the '
                        'puzzle-type gameplay.  Do you want to LOCK THIS CONTAINER? (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        lock_state = True
    elif ans == 'no':
        lock_state = False
    # write to container dict
    container[name]['locked'] = lock_state

     
    #  KEY?
    print ""
    print textwrap.fill('Containers can have a key (which can be any item) associated with them that will lock or unlock it.  '
                        'Here you can (1) name an existing key that will unlock it, (2) create a key that will unlock it, '
                        'or (3) not associate a key at all.  Which would you like to do? (1, 2, or 3)', width=100).strip()
    # loop for valid answer
    valid_ans = False
    while valid_ans == False:  # make sure answer is 1, 2, or 3
        ans = raw_input('\n>').strip().lower()
        
        tryFlag = True
        try:  #    cast as an integer if no error continues rest of error checking
            ans = int(ans)            
        except:
            print "\nYour response must be a 1, 2 or 3.  Try again."    
            tryFlag = False
        if tryFlag == True:    
            # Player names key
            if ans == 1: # player wants to name a key
                print ""
                print textwrap.fill('Enter the name of the key (name of item) you want to open the container.  Names are not case sensitive.', width=100).strip()
                valid_key = False
                while valid_key == False:
                    key = raw_input('\n>').strip().lower()
                    # add compare key name to items on the map to verify the key name then build if necessary
                    if validator.validate_name(key, validator.names) == True: # name is in list
                        valid_ans = True # break both loops
                    else:
                        print '\nThat key does not exist.  Try again.'
            # player makes key
            elif ans == 2:
                key = makeItems.makeItem[0]  # in Item builder it is possible to build more than 1 item but Items that are built are appended to list uses only first item
                valid_ans = True # break loop
            # NO key assigned
            elif ans == 3:  
                key = None
                valid_ans = True # break loop
            else:
                print "\nYour response must be a 1, 2 or 3.  Try again."
    # write key to container dict
    container[name]['key'] = key

    #  CONTAINER HIDDEN?    
    print ""
    print textwrap.fill('Your container can be hidden or visible.  Would you like your container to be hidden? (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        hidden_state = True
    elif ans == 'no':
        hidden_state = False
    else:
        print '\nYour answer must be Yes or No.'
    container[name]['hidden'] = hidden_state

    #  CONTAINER ITEMS
    container_items = [] # list for items in this container
    print ""
    print textwrap.fill('You can place items in the container, each container can hold as many items as you wish.  '
                        'Here you can (1) add an existing item by name, (2) create a new item, '
                        'or (3) not add an at all.  Which would you like to do? (1, 2, or 3)', width=100).strip()
    # done with adding items loop
    items_done = False
    while items_done == False:  # make sure answer is 1, 2, or 3
        ans = raw_input('\n>').strip().lower()
        
        tryFlag = True
        try:  #    cast as an integer if no error continue
            ans = int(ans)
        except:
            print "\nYour response must be a 1, 2 or 3.  Try again."    
            tryFlag = False
        if tryFlag == True:            
            # player names item(s)
            if ans == 1:
                print ""
                print textwrap.fill('Enter the NAME OF THE ITEM.  Names are not case sensitive.', width=100).strip()
                # valid name loop
                valid_item = False
                while valid_item == False:
                    item_name = raw_input('\n>').strip().lower()
                    if validator.validate_name(item_name, validator.names) == True:
                        #append to room container items list
                        container_items.append(item_name)
                        print "\nDo you want to add ANOTHER ITEM BY NAME?  (yes or no)"
                        ans = validator.validYesNo() # returns a yes or no
                        if ans == 'yes':
                            print '\nEnter the ITEM NAME to be added.'
                        elif ans == 'no':
                            print ""
                            print textwrap.fill('Now do you want to (1) add another item by name, (2) create an item, '
                                                'or (3) I\'m done with items.  (1, 2, or 3)', width=100).strip()
                            valid_item = True  # break only first loop here
                    else:
                        print '\nThat item does not exist.  Try again.'
            # build item for container
            elif ans == 2:
                items = makeItems.makeItem()  # item(s) returned from make item function
                for item in items:
                    container_items.append(item)   # append each item to list only "name"(items were instantiated in item builder)                
                print ""
                print textwrap.fill('Now do you want to (1) add another item by name, (2) create an item, '
                                    'or (3) I\'m done with items.  (1, 2, or 3)', width=100).strip()
            # done with items
            elif ans == 3:
                items_done = True  # Breaks out of all loops when 3 selected.
            else:
                print "\nYour response must be a 1, 2 or 3.  Try again." 
    
    #  SCRIPTS
    print ""
    print textwrap.fill('\n\n\nNeed script builder!', width=100).strip()
    scripts = {}
    #  Drop script building here later
    container[name]['script'] = scripts
    
    
    #  INSTANTIATE CONTAINER
    try:
        #engine.Container(name, desc, inspect_desc, scripts, locked = lock_state, key = key, hidden = hidden_state, items = container_items )
        print "\nINSATANTIATION LINE COMMENTED OUT FOR NOW IN makeContainers...."
        print textwrap.fill('CONGRADULATIONS!  Your ' + name + ' container has been built and is ready for insertion into the game.', width=100).strip()
    except:
        #need additonal error handling!!
        print '\nAn error has occurred and your container has not been built.  You can try again...'
        pass
    
    #  Append container name to list
    room_containers.append(name)
    
    # FINISHED??    
    print""
    print textwrap.fill('Would you like to build another container?  (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        makeContainer()
    elif ans == 'no':
        return room_containers

if __name__ == '__main__':
    makeContainer()   