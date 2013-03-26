__author__ = 'Andy Yeager', 'Sean Whitten'

import textwrap
import engine

# Room builder

class BuildRoom(object, player):
    
    '''This is a Room builder "module"  For players to build out rooms as they like.
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
    
    def __init__(self):
        
        print textwrap.fill('In this module you will be building a "room or area" to your liking with some limits of course.  We will walk you through the process building '
                            'and populating the room with things like Portals, Containers, Items, and even some other cool stuff.  So lets get started.', width = 150).strip()
        print ''
        self.lng_desc = ''
        #print self.desc,'\n'
        self.portals = {}
        #print self.portals, '\n'
        self.containers = {}
        #print self.containers, '\n'
        self.items = {}
        #print self.items, '\n'
        self.make_description(desc)
    
    def make_description():
       
        print ""
        print textwrap.fill ('Tell us you what you would like the user to see as they enter your room for the first time.  This will be your "long description".', width = 150).strip()

       
       #  confirm loop for User description
       
        confirm = False
        while confirm is False:
           lng_desc = raw_input("\n>  ")
           
           #  Filter out unwanted room descriptions and other stuff
           if lng_desc == "" or usr_desc == " ":  # no Empty Strings
               lng_desc = raw_input('Description cannot be empty.  Try again.\n>  ')
                              
           else:
               print '\n',lng_desc 
               print ''
               ans = raw_input('Is this the room description you want?\n>  ').lower()
               if ans == 'yes' or ans == 'y':
                   confirm = True 
               else:
                   lng_desc = raw_input("Enter your description.\n>  ")
               
        desc = lng_desc
        self.make_Portals()
    
    def make_Portals():  
        ##### ********* Is 1 portal per room going to be predefined because the player just came through a door? I left it as making 6 exits thus we have a free floating room.
        portals = []
        directions = ['north', 'south', 'east', 'west', 'up', 'down']
        print ''
        print textwrap.fill('Portals also known as exits from your room need to be defined.  Do you want to define any exits?',  width= 100).strip()
        print ''
        ans = raw_input('>  ').lower()
        print ""
        # Check user answer and continue as they desire
        if ans != 'yes' or ans != 'y':
            # Go to next function
            pass
        else: # how many
            qty = raw_input('How many would you like to create?\n>  ')
            print ''
        while qty > 0 : # Make as many doors as player specified
            
            # Door Name create dictionary for door
            name = raw_input('What would you like to call this door?\n>  ')
            print ""
            # Verification of door name has to happen here.
            #if != Global list/dict of all portals ever created  (Check name function???  used to check all items from a list/dict passed in?)
                #deny creation
            #else:
            portal = {name:qty} # Make dictionary for this door to be added to later Name is dictionary key with door number for room as value.
            
            
       
         
    
    
       
        
    
            
BuildRoom()      