import xml.etree.ElementTree as ET
import engine_classes
import Q2xml.base_xml as xml

############## LOAD METHODS #############
# Loads a player from an xml file
def load_player(path):
    player_attributes = {}
    xml = ET.parse(path)
    root = xml.getroot()
    
    player_attributes['coords'] = (int(root.attrib['x']), int(root.attrib['y']), int(root.attrib['z']), int(root.attrib['a']))
    player_attributes['prev_coords'] = (int(root.attrib['prev_x']), int(root.attrib['prev_y']), int(root.attrib['prev_z']), int(root.attrib['prev_a']))
    player_attributes['fih'] = int(root.attrib['fih'])
    player_attributes['name'] = root.attrib['name']
    player_attributes['items'] = []
    player_attributes['affiliation'] = {}
    player_attributes['sense_effects'] = {}

    affiliation_people = ['Obama', 'Kanye', 'OReilly', 'Gottfried', 'Burbiglia']
    for node in root:
        if node.tag == 'item':
            player_attributes['items'].append(node.text)
        elif node.tag in affiliation_people:
            player_attributes['affiliation'][node.tag] = int(node.text)
        else:
            player_attributes['sense_effects'][node.tag] = int(node.text)

    return engine_classes.Player(**player_attributes)
    
# Loads a room from an xml file
def load_room(path):
    room_attributes = {}
    room_attributes['items'] = []
    room_attributes['portals'] = []
    room_attributes['npcs'] = []
    room_attributes['players'] = []
    
    xml = ET.parse(path)
    root = xml.getroot()

    room_attributes['desc'] = root.attrib['desc']
    
    for node in root:
        if node.tag == 'item':
            room_attributes['items'].append(node.text)
        elif node.tag == 'portal':
            room_attributes['portals'].append(node.text)
    
    return engine_classes.Room(**room_attributes)

# Loads an item from a node
def load_item(root):
    item_attributes = {}
    item_attributes['scripts'] = {}
    item_attributes['items'] = []

    for attribute in root.attrib:
        value = root.attrib[attribute]
        if value.isdigit():
            value = bool(int(value))

        item_attributes[attribute] = value
    
    for node in root:
        if node.tag == 'item':
            item_attributes['items'].append(node.text)
        elif '_script' in node.tag:
            item_attributes['scripts'][node.tag.replace('_script', '')] = load_script(node)

    return engine_classes.Item(**item_attributes)

# Loads a portal from a node
def load_portal(root):
    portal_attributes = {}
    portal_attributes['coords'] = (int(root.attrib['x']), int(root.attrib['y']), int(root.attrib['z']), int(root.attrib['a']))
    portal_attributes['scripts'] = {}

    for attribute in root.attrib:
        if attribute not in 'xyza': # Ignore the coordinate attributes
            value = root.attrib[attribute]
            if value.isdigit():
                value = bool(int(value))

            portal_attributes[attribute] = value
    
    for node in root:
        if '_script' in node.tag:
            portal_attributes['scripts'][node.tag.replace('_script', '')] = load_script(node)

    return engine_classes.Portal(**portal_attributes)

# Loads a script from a node
def load_script(root):
    script = []
    
    for node in root:
        script.append((node.tag, node.text, node.attrib['delay']))
    
    return script

# Loads a dictionary of objects from an xml file
def load_objects(path):
    xml = ET.parse(path)
    root = xml.getroot()
    objects = {}

    for node in root:
        if node.tag == 'item':
            item = load_item(node)
            objects[item.name] = item
        elif node.tag == 'portal':
            portal = load_portal(node)
            objects[portal.name] = portal

    return objects

############# SAVE METHODS ##############
# Writes object list to a save file
def save_objects(objects, directory):
    child_nodes = []
    for object in objects:
        if isinstance(object, engine_classes.Item):
            child_nodes.append(create_item_node(object))    # Create an item node
        elif isinstance(object, engine_classes.Portal):
            child_nodes.append(create_portal_node(object))  # Create a portal node

    objects_node = xml.XMLNode('objects', children=child_nodes)

    save = open(directory + '/objects/objects.xml', 'w')
    save.write(objects_node.flatten_self())
    save.close()

# Writes a player to a save file
def save_player(player):
    attributes = {}
    attributes['x'] = str(player.coords[0])
    attributes['y'] = str(player.coords[1])
    attributes['z'] = str(player.coords[2])
    attributes['a'] = str(player.coords[3])
    attributes['prev_x'] = str(player.prev_coords[0])
    attributes['prev_y'] = str(player.prev_coords[1])
    attributes['prev_z'] = str(player.prev_coords[2])
    attributes['prev_a'] = str(player.prev_coords[3])
    attributes['name'] = player.name
    attributes['fih'] = str(player.fih)

    child_nodes = []
    for person in player.affiliation: # Create the affiliation nodes
        person_node = xml.XMLNode(person, value=player.affiliation[person])
        child_nodes.append(person_node)

    for item in player.items: # Create the item nodes
        item_node = xml.XMLNode('item', value=item)
        child_nodes.append(item_node)

    for effect in player.sense_effects: # Create the sense nodes
        sense_node = xml.XMLNode(effect, value=player.sense_effects[effect])
        child_nodes.append(sense_node)

    player_node = xml.XMLNode('player', attributes, children=child_nodes)

    save = open('players/%s.xml' % player.name, 'w')
    save.write(player_node.flatten_self())
    save.close()

# Writes a room to a save file
def save_room(room, path):
    attributes = {}
    attributes['desc'] = room.desc

    child_nodes = []
    for item in room.items:
        item_node = xml.XMLNode('item', value=item)
        child_nodes.append(item_node)

    for portal in room.portals:
        portal_node = xml.XMLNode('portal', value=portal)
        child_nodes.append(portal_node)

    room_node = xml.XMLNode('room', attributes, children=child_nodes)

    save = open(path, 'w')
    save.write(room_node.flatten_self())
    save.close()

# Creates an item node
def create_item_node(item):
    attributes = {}
    attributes['name'] = item.name
    attributes['desc'] = item.desc
    attributes['inspect_desc'] = item.inspect_desc
    attributes['portable'] = str(int(item.portable))
    attributes['hidden'] = str(int(item.hidden))
    attributes['container'] = str(int(item.container))
    attributes['locked'] = str(int(item.locked))
    attributes['key'] = item.key

    child_nodes = []
    for container_item in item.items:   # Create the container item nodes
        container_item_node = xml.XMLNode('item', value=container_item)
        child_nodes.append(container_item_node)

    child_nodes.append(create_scripts_node(item.scripts))   # Create the scripts node

    item_node = xml.XMLNode('item', attributes, children=child_nodes)
    return item_node

# Creates a portal node
def create_portal_node(portal):
    attributes = {}
    attributes['name'] = portal.name
    attributes['x'] = str(portal.coords[0])
    attributes['y'] = str(portal.coords[1])
    attributes['z'] = str(portal.coords[2])
    attributes['z'] = str(portal.coords[3])
    attributes['direction'] = portal.direction
    attributes['desc'] = portal.desc
    attributes['inspect_desc'] = portal.inspect_desc
    attributes['locked'] = str(int(portal.locked))
    attributes['hidden'] = str(int(portal.hidden))
    attributes['key'] = portal.key

    scripts_node = create_scripts_node(portal.scripts)  # Create the scripts node

    portal_node = xml.XMLNode('portal', attributes, children=[scripts_node])
    return portal_node

# Creates a scripts node
def create_scripts_node(scripts):
    script_nodes = []
    for script in scripts:
        child_nodes = []
        for action in scripts[script]:
            action_node = xml.XMLNode(action[0], attrs={'delay': str(action[2])}, value=action[1])
            child_nodes.append(action_node)

        script_node = xml.XMLNode(script + '_script', children=child_nodes)
        script_nodes.append(script_node)

    scripts_node = xml.XMLNode('scripts', children=script_nodes)
    return scripts_node