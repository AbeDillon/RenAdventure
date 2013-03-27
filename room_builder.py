__author__ = 'Andy Yeager', 'Sean Whitten'

import validator
import textwrap
import makePortals
import containerMaker
import engine

# Room builder

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

global_portals = {'bob', 'juan'}
room_portals = {}

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
            ans = raw_input('\n>  ').lower()
            if ans == 'yes' or ans == 'y':
                confirm = True
            else:
                print 'Enter the description you want.'
                
    makePortals(player)

def makePortals(player):
    #  confirm they want to create portals
    print ''
    print textwrap.fill('Portals, also known as exits, need to be defined.  Do you want to create any portals?',  width=100).strip()
    right_ans = False
    while right_ans == False: #  Loop to validate answer and send in proper direction for continued creation.
        ans = raw_input('\n>  ').lower().strip()
        if  ans != 'no' and ans != 'n' and ans != 'yes' and ans != 'y':  # answer must be one of these
            print "Please answer Yes or No."
        elif ans == 'no' or ans == 'n':
            right_ans = True
            #  need to send to next Method later when defined pass for now.
        elif ans == 'yes' or ans == 'y':  # anything other than yes or y
            portals = makePortals.makePortals(player)
            # get return from makePortals and do what with it...
            # return should be 
            
    assignContainers()

def assignContainers():
    '''Function at this time will require player to create every container they place in room.
    when other code supports functionality to add existing containers to the room
    along with the items that the said container contains may be added.  Hence function title
    assign Containers'''
    
    #    Code to select containers should come before creation code
    #    because the select code could conceivably lead to creation code.
    #    for example  - If container selected/named/called does not exist
    #    would you like to create one?
    
    # begin code to begin container creation
    print ''
    print textwrap.fill('Containers can be placed in your room to hold various items.  Do you want to create any containers?',  width=100).strip()
    right_ans = False
    while right_ans == False:
        ans = raw_input('\n>  ').lower().strip()
        if  ans != 'no' and ans != 'n' and ans != 'yes' and ans != 'y':
            print "Please answer Yes or No."
        elif ans == 'no' or ans == 'n':
            right_ans = True  #  need to send to next Method later when defined pass for now.
        elif ans == 'yes' or ans == 'y':  # anything other than yes or y
            containers = containerMaker.makeContainers()
            # get return from makeContainers and do what with it...
            
            
    assignItems()

def assignItems():
    '''Similar to the containers this function will require players to make the items they want
    to place in the room.  Functionality needs be added to allow players to add items that
    already exist'''
    
    # select items first
    
    # make item second
    
    print 'Assign items function needs fininshed'


make_description()