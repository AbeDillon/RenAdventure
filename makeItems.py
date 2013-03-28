'Item maker'


#*************************************TO DO*****************************************
#    1.  Test this baby out
#    2.  Script builder function near the end

'''
    Attributes:
    - Name
    - Description (for printing in a room)
    - Inspect Description (for looking at the item)
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Portable (bool)
    - portable (bool)
'''   
room_items = {}

def makeItem():
    item = {}
    
    # assign name       
    print ""
    print textwrap.fill('What would you like this item to be named.  The item name must be used by someone else, '
                        'and is not case sensative.', width=100).strip()
    original = False
    while original == False:    # create original name for item
        name = raw_input('\n>').strip()
        if validator.original_name(name, validator.names) == False:  #  Check against list of items created in entire game
            print "Sorry, that name has already been used by someone else.  Try Again."
        elif validator.original_name(name, room_items) == False:  #check against list in this newly created items.
            print "You have already created a item with that name.  Try again."
        else:
            item[name] = {}
            original = True  #  Set original to True to break out of validation loop
            
    # assign description
    print ''
    print textwrap.fill('Enter a description for your item.  This is a generalized description that players will see.', width = 100).strip()

    # loop to set General Description - Verify/Validate here
    desc_accept = False
    while desc_accept == False:
        desc = raw_input('\n>')
        if len(desc) == 0: # must contain something
            print "\nYour Description cannot be empty.  Try again."
        else:
            item[name]['desc'] = desc
            desc_accept = True

    # Loop to set Inspection Description - Verify/Validate Here
    desc_accept = False
    print ""
    print textwrap.fill('The inspection description is what players will see when they give the inspect command on your item.  Enter '
                        'your inspection description now.', width=100).strip()
    while desc_accept == False:
        inspect_desc = raw_input('\n>')
        if len(inspect_desc) > 0:
            item[name]['inspect_desc'] = inspect_desc
            desc_accept = True
        else:
            print "\nYour Inspection Description cannot be empty.  Try again."
            
    #  Define portable state of the item
    print ""
    print textwrap.fill('Your item can be portable meaning a player can pick it up.  Would you like your item to be portable? (Yes or No)', width=100).strip()
    valid_ans = False
    while valid_ans == False:
        ans = raw_input('\n>').lower().strip()
        if ans == 'yes' or ans == 'y':
            item[name]['portable'] = True
            valid_ans = True
        elif ans == 'no' or ans == 'n':
            item[name]['portable'] = False
            valid_ans = True
        else:
            print '\nYour answer must be Yes or No.'        
            
    #  Define hidden state of the item
    
    print ""
    print textwrap.fill('Your item can be hidden or visible.  Would you like your item to be hidden? (Yes or No)', width=100).strip()
    valid_ans = False
    while valid_ans == False:
        ans = raw_input('\n>').lower().strip()
        if ans == 'yes' or ans == 'y':
            item[name]['hidden'] = True
            valid_ans = True
        elif ans == 'no' or ans == 'n':
            item[name]['hidden'] = False
            valid_ans = True
        else:
            print '\nYour answer must be Yes or No.'
            
    #  Enter the scripts here
    print ""
    print textwrap.fill('\n\n\nNeed script builder!', width=100).strip()
    scripts = {}
    #  Drop script building here later
    item[name]['script'] = scripts
    
    
    room_items.append(item)
    print room_itemss
    
    print""
    print textwrap.fill('You have built the ' + name + ' item.  Do you want to build another? (Yes or No)', width=100).strip()
    valid_ans = False
    while valid_ans == False:
        ans = raw_input('\n>').lower().strip()
        if ans == 'yes' or ans == 'y':
            makeItem()
            valid_ans = True
        elif ans == 'no' or ans == 'n':
            return room_items
        else:
            print '\nYour answer must be Yes or No.  Try  Again'

#makeItem()   