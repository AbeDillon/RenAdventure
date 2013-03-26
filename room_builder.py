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



print textwrap.fill('In this module you will be building a "room" or "area" to your liking with some limits of course.  We will walk you through the process of building '
                    'and populating the room with things like Portals, Containers, Items, and even some other cool stuff.  So lets get started.', width=100).strip()

def make_description():

    print ""
    print textwrap.fill ('Tell us you what you would like the user to see as they enter your room for the first time.  This will be your "long description".', width=100).strip()


   #  confirm loop for User description
    confirm = False
    while confirm is False:
        desc = raw_input("\n>  ")

       #  Filter out unwanted room descriptions and other stuff
        if len(desc) > 0:
            print '\n', desc
            print '\nIs this the room description you want?'
            ans = raw_input('\n>  ').lower()
            if ans == 'yes' or ans == 'y':
                confirm = True
            else:
                print 'Enter your description.'

    #  make_Portals()
    #  Ask if they want to create doors
    print ''
    print textwrap.fill('Portals, also known as exits, need to be defined.  Do you want to create any portals?',  width=100).strip()
    right_ans = False
    while right_ans == False:
        ans = raw_input('\n>  ').lower().strip()
        if  ans != 'no' and ans != 'n' and ans != 'yes' and ans != 'y':
            print "Please answer Yes or No."
        # Check user answer and continue as they desire
        elif ans == 'no' or ans == 'n':
            right_ans = True  #  need to send to next Method later when defined pass for now.
        elif ans == 'yes' or ans == 'y':  # anything other than yes or y
            makePortals.makePortals()

    #  containerCreation()
    print ''
    print textwrap.fill('Containers can be placed in your room to hold various items.  Do you want to create any containers?',  width=100).strip()
    right_ans = False
    while right_ans == False:
        ans = raw_input('\n>  ').lower().strip()
        if  ans != 'no' and ans != 'n' and ans != 'yes' and ans != 'y':
            print "Please answer Yes or No."
        # Check user answer and continue as they desire
        elif ans == 'no' or ans == 'n':
            right_ans = True  #  need to send to next Method later when defined pass for now.
        elif ans == 'yes' or ans == 'y':  # anything other than yes or y
            containerMaker.makeContainers()




make_description()