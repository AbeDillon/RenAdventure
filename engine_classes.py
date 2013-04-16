class Room:
    '''
    Attributes:
    - Description

    Contains:
    - Portals
    - Items
    - Players
    - NPCs
    '''
    def __init__(self, desc, portals, items, players, npcs):
        self.desc = desc
        self.players = players
        self.npcs = npcs

        self.portals = {}
        for portal in portals:
            if portal in self.portals:
                self.portals[portal] += 1
            else:
                self.portals[portal] = 1

        self.items = {}
        for item in items:
            if item in self.items:
                self.items[item] += 1
            else:
                self.items[item] = 1

class Portal:
    '''
    Attributes:
    - Name
    - Direction (north, south, east, west, up and down)
    - Description
    - Inspect Description
    - Coordinates (coordinates that the portal lead to (x,y,z))
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Locked (bool)
    - Key
    - Hidden (bool)
    '''
    def __init__(self, name, direction, desc, inspect_desc, coords, scripts = {}, locked = False, hidden = False, key = ''):
        self.name = name.lower()
        self.direction = direction
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.coords = coords
        self.scripts = scripts
        self.locked = locked
        self.hidden = hidden
        self.key = key

class Item:
    '''
    Attributes:
    - Name
    - Description (for printing in a room)
    - Inspect Description (for looking at the item)
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Portable (bool)
    - Hidden (bool)

    - Container (bool)
    - Locked (bool)
    - Key
    - Items
    '''
    def __init__(self, name, desc, inspect_desc, scripts = {}, portable = True, hidden = False, container = False, locked = False, key = '', items = {}):
        self.name = name.lower()
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.portable = portable
        self.hidden = hidden
        self.container = container
        self.locked = locked
        self.key = key
        self.scripts = scripts

        self.items = {}
        for item in items:
            if item in self.items:
                self.items[item] += 1
            else:
                self.items[item] = 1

class Player:
    '''
    Attributes:
    - Name
    - Coordinates
    - Faith in Humanity
    - Affiliation (dictionary of opinion of each person)
    - Senses (Sight, Sound, Smell, Seeing Dead People)

    Contains:
    - Items
    '''
    def __init__(self, name, coords, prev_coords, affiliation, sense_effects = {}, items = {}, fih = 30):
        self.name = name.lower()
        self.coords = coords
        self.prev_coords = prev_coords
        self.fih = fih
        self.affiliation = affiliation
        self.sense_effects = sense_effects

        self.items = {}
        for item in items:
            if item in self.items:
                self.items[item] += 1
            else:
                self.items[item] = 1

class NPC:
    '''
    Attributes:
    - Name
    - Coordinates
    - Affiliation (dictionary of opinion of each person)
    '''
    def __init__(self, name, coords, affiliation, tweets = None):
        self.name = name.lower()
        self.coords = coords
        self.affiliation = affiliation
        self.tweets = []
        self.lifespan = 20 # Number of cycles the NPC lasts before they are recycled
        self.cycles = 0 # Number of cycles the NPC has been alive for

        twitter_file = open('twitterfeeds/%s.txt' % self.name, 'a')
        twitter_file.close()