class Room:
    '''
    Attributes:
    - ID
    - Description
    - Up Votes
    - Down Votes

    Contains:
    - Portals
    - Items
    - Players
    - NPCs
    - Editors = []
    '''
    def __init__(self, id, desc, portals, items, players, npcs, up_votes = 0, down_votes = 0, editors = []):
        self.id = id
        self.desc = desc
        self.up_votes = up_votes
        self.down_votes = down_votes
        self.players = players
        self.npcs = npcs
        self.editors = editors

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
    - Coordinates (coordinates that the portal lead to (x,y,z,a))
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Locked (bool)
    - Key
    - Hidden (bool)
    - Editors
    '''
    def __init__(self, name, direction = None, desc = "", inspect_desc = "", coords = (0,0,0,0), scripts = {}, locked = False, hidden = False, key = '', editors=[]):
        self.name = name.lower()
        self.direction = direction
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.coords = coords
        self.scripts = scripts
        self.locked = locked
        self.hidden = hidden
        self.key = key
        self.editors = editors

class Item:
    '''
    Attributes:
    - Name
    - Description (for printing in a room)
    - Inspect Description (for looking at the item)
    - Action Scripts (ex. {'take': [['move', 'boulder'], ['move', 'monster']})
    - Portable (bool)
    - Hidden (bool)
    - Editors = []

    - Container (bool)
    - Locked (bool)
    - Key
    - Items
    '''
    def __init__(self, name, desc, inspect_desc, scripts = {}, portable = True, hidden = False, container = False, locked = False, key = '', items = {}, editors = []):
        self.name = name.lower()
        self.desc = desc
        self.inspect_desc = inspect_desc
        self.portable = portable
        self.hidden = hidden
        self.container = container
        self.locked = locked
        self.key = key
        self.scripts = scripts
        self.editors = editors
        
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
    - Vote History

    Contains:
    - Items
    '''
    def __init__(self, name, coords, prev_coords, affiliation, sense_effects = {}, items = {}, fih = 30, editors=[], vote_history = {}):
        self.name = name.lower()
        self.coords = coords
        self.prev_coords = prev_coords
        self.fih = fih
        self.affiliation = affiliation
        self.sense_effects = sense_effects
        self.editors = editors
        self.vote_history = vote_history

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
    - Editors
    - Coordinates
    - Affiliation (dictionary of opinion of each person)
    - Up Votes
    - Down Votes
    '''
    def __init__(self, name, coords, affiliation, up_votes = 1, down_votes = 0, tweets = None, textID = "not_provided", editors = []):
        self.name = name.lower()
        self.editors = editors
        self.coords = coords
        self.textID = textID
        self.affiliation = affiliation
        self.up_votes = up_votes
        self.down_votes = down_votes
        self.tweets = []
        self.lifespan = 20 # Number of cycles the NPC lasts before they are recycled
        self.cycles = 0 # Number of cycles the NPC has been alive for

        twitter_file = open('twitterfeeds/%s.txt' % self.textID, 'a')
        twitter_file.close()