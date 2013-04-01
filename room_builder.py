__author__ = 'Andy Yeager', 'Sean Whitten'

import validator
import textwrap
import makePortals
import makeContainers
import makeItems
import engine

'''
This is a Room builder "module"  For players to build out rooms as they like.
Rooms must fit all room requirements for proper game play.
Follows structure of our Room Object

Attributes:
- Player (Tag of name of player creating room) pass in likely later.
- Long Description
- Short Description

Contains:
- Portals
- Containers
- Items
'''
room = {}
room_portals = []
room_containers = []
room_items = []


#    Entry Text
print textwrap.fill('In this module you will be building a "room" or "area" to your liking with some limits of course.  '
                    'We will walk you through the process of building and populating the room with things like Portals, '
                    'Containers, Items, and some other stuff.  So lets get started.', width=100).strip()

# begin room creation
def makeDescription(player):

    print ""
    print textwrap.fill ('Your room requires a description.  This will be what the player sees when they enter your room.  '
                         'Enter your description.', width=100).strip()

    # Loop to confirm user description
    confirm = False
    while confirm is False:
        desc = raw_input("\n>  ")    
        # Filter and validate description
        if len(desc) > 0:
            print '\n', desc    # show description
            print '\nIs this the room description you want?'
            ans = validator.validYesNo()
            if ans == 'yes':
                confirm = True
            else:
                print '\nEnter the description you want.'
    room['description'] = desc
    roomPortals(player)

def roomPortals(player):
    #  confirm they want to create portals
    print ''
    print textwrap.fill('Portals, also known as exits, need to be defined.  Do you want to create any portals?',  width=100).strip()
    ans = validator.validYesNo()
    if ans == 'no':
        assignContainers(player)
    elif ans == 'yes':  # anything other than yes or y
        portals = makePortals.makePortals()
        assignContainers(player)

def assignContainers(player):
    '''Function at this time will require player to create every container they place in room.
    when other code supports functionality to add existing containers to the room
    along with the items that the said container contains may be added.  Hence function title
    assign Containers'''
    
    #    Code to select containers should come before creation code
    #    because the select code could conceivably lead to creation code.
    #    for example  - If container selected/named/called does not exist
    #    would you like to create one?
    
    # begin code to begin container creation
    print ""
    print textwrap.fill('You can place containers in the "room" that can hold as many items as you wish.  '
                        'Here you can (1) add an existing container by name, (2) create a container, '
                        'or (3) not add a container at all.  Which would '
                        'you like to do? (1, 2, or 3)', width=100).strip()
    containers_done = False
    while containers_done == False:  # make sure answer is 1, 2, or 3
        ans = raw_input('\n>').strip().lower()
        try:  #    cast as an integer if no error continue
            ans = int(ans)
            if ans == 1: # player wants to name a container
                print ""
                print textwrap.fill('Enter the name of the container.  Names are not case sensitive.', width=100).strip()
                valid_container = False
                while valid_container == False:
                    name = raw_input('\n>').strip().lower()
                    if validator.validate_name(name, validator.names) == False:  # Name not in list
                        #append to room container list
                        room_containers.append(name) #append name to room_containers list
                        print "Do you want to add another container by name?  (yes or no)"
                        ans = validator.validYesNo() # returns a yes or no
                        if ans == 'yes':
                            print '\nEnter the name of the next container.'
                        elif ans == 'no':
                            print textwrap.fill('Now do you want to (1) add another container by name, (2) create a container, '
                                                'or (3) I\'m done with containers.  (1, 2, or 3)', width=100).strip()
                            valid_container = True
                    else:
                        print 'That container does not exist.  Try again.'
            elif ans == 2: #  Player wants to build a container
                containers = makeContainers.makeContainer()  # get room containers returned from make containers function
                for container in containers:
                    room_containers.append(container)   # append each container name (containers will have been instantiated in called function.
                print textwrap.fill('Now do you want to (1) add another container by name, (2) create a container, '
                                    'or (3) I\'m done with containers.  (1, 2, or 3)', width=100).strip()
            elif ans == 3:  # done
                containers_done = True
            else:
                print "Your response must be a 1, 2 or 3.  Try again."
        except:
            print "Your response must be a 1, 2 or 3.  Try again."
    assignItems(player)

def assignItems(player):
    '''Similar to the containers this function will require players to make the items they want
    to place in the room.  Functionality needs be added to allow players to add items that
    already exist'''
    
    print ""
    print textwrap.fill('You can place items in the room.  Here you can (1) add an existing item by name, (2) create an item, '
                        'or (3) not add an item at all.  Which would you like to do? (1, 2, or 3)', width=100).strip()
    items_done = False
    while items_done == False:  # make sure answer is 1, 2, or 3
        ans = raw_input('\n>').strip().lower()
        try:  #    cast as an integer if no error continues rest of error checking
            ans = int(ans)
            if ans == 1: # player wants to name a item
                print ""
                print textwrap.fill('Enter the name of the item.  Names are not case sensitive.', width=100).strip()
                valid_item = False
                while valid_item == False:
                    item = raw_input('\n>').strip().lower()
                    if validator.validate_name(item, validator.names) == True: # if item name not in list
                        room_items.append(item)
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
            elif ans == 2: #  Player wants to build a item
                items = makeItems.makeItem()
                for item in items:
                    room_items.append(item)
                print textwrap.fill('Now do you want to (1) add another item by name, (2) create an item, '
                                    'or (3) I\'m done with items.  (1, 2, or 3)', width=100).strip()
            elif ans == 3:  # done with items
                items_done = True
            else:
                print "Your response must be a 1, 2 or 3.  Try again."
            
        except:
            print "Error!  Your response must be a 1, 2 or 3.  Try again."
            
    submit_room(player)
             
def submit_room(player):
    
    print ""
    print room['description']
    print ""
    print room_portals
    print ""
    print room_containers
    print ""
    print room_items
    
makeDescription('john')