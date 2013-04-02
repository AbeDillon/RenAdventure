'Item maker'
import engine
import validator
import textwrap
import makeScripts


#*************************************TO DO*****************************************
#    1.  Script builder function near the end

'''
    Attributes:
    - Name
    - Description (for printing in a room)
    - Inspect Description (for looking at the item)
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Portable (bool)
    - portable (bool)
    
    - Container (bool)
    - Locked (bool)
    - Key
    - Items
'''   
room_items = []  # list for all items

def makeItem():
    
    item = {} #dict of this item being built
    
    # ORIGINAL NAME      
    print ""
    print textwrap.fill('Enter a NAME for your item.  The name must not be used already and is not case sensative.', width=100).strip()
    #originality loop
    original = False
    while original == False:    # create original name for item
        name = raw_input('\n>').strip()
        if validator.original_name(name, validator.names) == True:  #  name in list
            print "\nSorry, that name has already been used by someone else.  Try Again."
        elif validator.original_name(name, room_items) == True:  #check against list in this newly created items.
            print "\nYou have already created a item with that name.  Try again."
        else:
            # write dict key and break from loop
            item[name] = {}
            original = True
            
    # DESCRIPTION
    print ''
    print textwrap.fill('Enter a DESCRIPTION for your item.  This is a generalized description that the players will see.', width = 100).strip()

    # loop to set General Description - Verify/Validate here
    desc_accept = False
    while desc_accept == False:
        desc = raw_input('\n>')
        if len(desc) < 1: # must contain something
            print "\nYour Description cannot be empty.  Try again."
        else:
            item[name]['desc'] = desc
            desc_accept = True

    # INSPECTION DESCRIPTION    
    print ""
    print textwrap.fill('The inspection description is what players will see when they give the inspect command on your item.  Enter '
                        'your INSPECTION DESCRIPTION now.', width=100).strip()
    # loop for inspection description
    desc_accept = False
    while desc_accept == False:
        inspect_desc = raw_input('\n>')
        if len(inspect_desc) < 1:
            print "\nYour Inspection Description cannot be empty.  Try again."
        else:
            item[name]['inspect_desc'] = inspect_desc
            desc_accept = True
            
            
    #  PORTABLE
    print ""
    print textwrap.fill('Your item can be portable meaning a player can pick it up.  Would you like your ITEM to be PORTABLE? (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        portable_state = True
    elif ans == 'no':
        portable_state = False
    item[name]['portable'] = portable_state

    # HIDDEN
    print ""
    print textwrap.fill('Your item can be hidden or visible.  Would you like your item to be HIDDEN? (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        hidden_state = True
    elif ans == 'no':
        hidden_state = False
    item[name]['hidden'] = hidden_state
    
    # CONTAINER???
    print ""
    print textwrap.fill('Some items hold other items.  Do you want this item to be a CONTAINER FOR OTHER ITEMS?  (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        container = True
    if ans == 'no':
        container = False
        lock_state = False
        item[name]['locked'] = lock_state
        key = None
        item[name]['key'] = key
        items = []
        item[name]['items'] = items
    item[name]['container'] = container
        
    # CONTAINER DEPENDANT ATTRIBUTES
    if container == True:
        
        # LOCKED
        print ""
        print textwrap.fill('Your container/item can be locked or unlocked which can then be opened using a key or other scripted method.  '  
                            'Think puzzle-type gameplay, do you want to LOCK THIS CONTAINER/ITEM? (Yes or No)', width=100).strip()
        ans = validator.validYesNo()
        if ans == 'yes':
            lock_state = True
        elif ans == 'no':
            lock_state = False
        # write to container dict
        item[name]['locked'] = lock_state
    
        #KEY
        print ""
        print textwrap.fill('Containers/items can have a key (which can be any item) associated with them that will lock or unlock it.  '
                            'Here you can (1) name an existing item that will unlock it or (2) not associate a key at all.  Which would '
                            'you like to do? (1 or 2)', width=100).strip()
        # loop for valid answer
        valid_ans = False
        while valid_ans == False:  # make sure answer is 1, 2, or 3
            ans = raw_input('\n>').strip().lower()
            
            tryFlag = True
            try:  #    cast as an integer if no error continues rest of error checking
                ans = int(ans)            
            except:
                print "\nYour response must be a 1 or 2.  Try again."    
                tryFlag = False
            if tryFlag == True:    
                # Player names key
                if ans == 1:
                    print ""
                    print textwrap.fill('Enter the name of the key (name of item) you want to open the container/item.  Names are not case sensitive.', width=100).strip()
                    valid_key = False
                    while valid_key == False:
                        key = raw_input('\n>').strip().lower()
                        # add compare key name to items on the map to verify the key name then build if necessary
                        if validator.validate_name(key, validator.names) == True: # name is in list
                            valid_key = True
                            valid_ans = True
                        else:
                            print '\nThat key does not exist.  Try again.'
                # No key
                elif ans == 2:
                    key = None
                    valid_ans = True # break loop
                else:
                    print "\nYour response must be a 1 or 2.  Try again."
                    
        # write key to container dict
        item[name]['key'] = key
        
        #ITEMS
        container_items = [] # list for items in this container
        print ""
        print textwrap.fill('You can place other items in the container/item, each container/item can hold as many items as you wish.  '
                            'Here you can (1) add an existing item by name, (2) not add an item at all.  Which would you like to do? '
                            '(1 or 2)', width=100).strip()
        # done with adding items loop
        items_done = False
        while items_done == False:  # make sure answer is 1, 2, or 3
            ans = raw_input('\n>').strip().lower()
            
            tryFlag = True
            try:  #    cast as an integer if no error continue
                ans = int(ans)
            except:
                print "\nYour response must be a 1 or 2.  Try again."    
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
                                print textwrap.fill('Now do you want to (1) add another item by name, or (2) I\'m done with items.  '
                                                    '(1 or 2)', width=100).strip()
                                valid_item = True  # break only first loop here
                        else:
                            print '\nThat item does not exist.  Try again.'
               #  Done with items
                elif ans == 2:
                    items_done = True  # Breaks out of all loops when 3 selected.
                else:
                    print "\nYour response must be a 1 or 2.  Try again."
               
        
        
    # SCRIPTS
    print ""
    print textwrap.fill('Scripts can be written that will override the commands given upon your item.  For example picking up (take) this item '
                        'could cause a portal in the room to open or a hidden item to be revealed.  This is where things can get really interesting.  '
                        'Would you like to build any scripts for this item?', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        scripts = makeScripts.makeScripts()
    if ans == 'no':
        scripts = {}
    # write scripts to portal dict
    item[name]['scripts'] = scripts
    
    # INSTANTIATE ITEM    
    tryFlag = True
    try:
        #engine.Item(name, desc, inspec_desc, scripts = scripts, portable = portable_state, hidden = hidden_state)
        print"\nINSTANTIATION LINE COMMENTED OUT IN makeItems for now....."
        print textwrap.fill('Congratulations!  Your ' + name + ' item was built successfully and is now ready to be inserted into the gameplay.')
    except:
        print ""
        print textwrap.fill('An error has occured and your Item did not build properly.  You will have to try again.', width=100).strip()
        tryFlag = False
        #need additional error handling here.
        
    if tryFlag == True:
        # append name to item list for room building function
        room_items.append(name)
        # append Item name to master list of names
        validator.names.append(name)
        # append Item to items list
        validator.item_list.append(name)
    
    #  Build more item(s)
    print""
    print textwrap.fill('Do you want to build another Item? (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        makeItem()
    elif ans == 'no':
        return room_items


if __name__ == '__main__':
    makeItem()   