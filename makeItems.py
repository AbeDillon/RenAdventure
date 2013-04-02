'Item maker'
import engine
import validator
import textwrap



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
        if len(desc) > 0: # must contain something
            print "\nYour Description cannot be empty.  Try again."
        else:
            item[name]['desc'] = desc
            desc_accept = True

    # INSPECTION DESCRIPTION    
    print ""
    print textwrap.fill('The inspection description is what players will see when they give the inspect command on your item.  Enter '
                        'your inspection description now.', width=100).strip()
    # loop for inspection description
    desc_accept = False
    while desc_accept == False:
        inspect_desc = raw_input('\n>')
        if len(inspect_desc) > 0:
            item[name]['inspect_desc'] = inspect_desc
            desc_accept = True
        else:
            print "\nYour Inspection Description cannot be empty.  Try again."
            
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
    
    # SCRIPTS
    print ""
    print textwrap.fill('\n\n\nNeed script builder!', width=100).strip()
    scripts = {}
    #  Drop script building here later
    item[name]['script'] = scripts
    
    # INSTANTIATE ITEM
    try:
        #engine.Item(name, desc, inspec_desc, scripts = scripts, portable = portable_state, hidden = hidden_state)
        print"\nINSTANTIATION LINE COMMENTED OUT IN makeItems for now....."
        print textwrap.fill('CONGRADUALTIONS!  Your ' + name + ' item was built successfully and is now ready to be inserted into the gameplay.')
    except:
        print ""
        print textwrap.fill('An error has occured and your Item did not build properly.  You will have to try again.', width=100).strip()
        #need additional error handling here.
        
    # append name to item list for room building
    room_items.append(name)
    
    
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