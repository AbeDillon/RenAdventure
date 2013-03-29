import xml.etree.ElementTree as ET
import engine

############## LOAD METHODS #############
# Loads a player from an xml file
def load_player(path):
    player_attributes = {}
    
    xml = ET.parse(path)
    root = xml.getroot()
    
    player_attributes['coords'] = (int(root.attrib['x']), int(root.attrib['y']), int(root.attrib['z']))
    
    for node in root:
        if node.tag == 'affiliation':
            affiliation = {}
            for tag in node:
                affiliation[tag.tag] = int(tag.text)

            player_attributes['affiliation'] = affiliation
        else:
            player_attributes[node.tag] = node.text
    
    return engine.Player(**player_attributes)
    
# Loads a room from an xml file
def load_room(path):
    room_attributes = {}
    room_attributes['items'] = []
    room_attributes['containers'] = []
    room_attributes['portals'] = []
    
    xml = ET.parse(path)
    root = xml.getroot()
    
    for node in root:
        if node.tag == 'item':
            room_attributes['items'].append(load_item(node))
        elif node.tag == 'container':
            room_attributes['containers'].append(load_container(node))
        elif node.tag == 'portal':
            room_attributes['portals'].append(load_portal(node))
        else:
            room_attributes[node.tag] = node.text
    
    return engine.Room(**room_attributes)

# Loads an item from a node
def load_item(root):
    item_attributes = {}
    item_attributes['scripts'] = {}
    
    for node in root:
        if '_script' in node.tag:
            tag = node.tag.replace('_script', '')
            item_attributes['scripts'][tag] = load_script(node)
        else:
            text = node.text
            
            if text.isdigit():
                text = bool(text)
        
            item_attributes[node.tag] = text

    return engine.Item(**item_attributes)

# Loads a portal from a node
def load_portal(root):
    portal_attributes = {}
    portal_attributes['coords'] = (int(root.attrib['x']), int(root.attrib['y']), int(root.attrib['z']))
    portal_attributes['scripts'] = {}
    
    for node in root:
        if '_script' in node.tag:
            tag = node.tag.replace('_script', '')
            portal_attributes['scripts'][tag] = load_script(node)
        else:
            text = node.text
            
            if text != None and text.isdigit():
                text = bool(int(text))
        
            portal_attributes[node.tag] = text

    return engine.Portal(**portal_attributes)

# Loads a container from a node
def load_container(root):
    container_attributes = {}
    container_attributes['items'] = []
    container_attributes['scripts'] = {}
    
    for node in root:
        if '_script' in node.tag:
            tag = node.tag.replace('_script', '')
            container_attributes['scripts'][tag] = load_script(node)
        elif node.tag == 'item':
            container_attributes['items'].append(load_item(node))
        else:
            text = node.text
            
            if text.isdigit():
                text = bool(text)
        
            container_attributes[node.tag] = text

    return engine.Container(**container_attributes)

# Loads a script from a node
def load_script(root):
    script = []
    
    for node in root:
        delay = 0
        if 'delay' in node.attrib:
            delay = int(node.attrib['delay'])

        script.append((node.tag, node.text, delay))
    
    return script

############# SAVE METHODS ##############
# Writes a player to a save file
def save_player(player):
    save = open('players/%s.xml' % player.name, 'w')
    save.write('<?xml version="1.0"?>\n')
    save.write('<player x="%d" y="%d" z="%d">\n' % player.coords)
    
    save.write('<name>%s</name>\n' % player.name)
    save.write('<fih>%d</fih>\n' % player.fih)

    save.write('<affiliation>')
    for person in player.affiliation:
        save.write('<%s>%d</%s>' % (person, player.affiliation[person], person))
    save.write('</affiliation>')
    
    for item in player.items.values():
        save_item(save, item)
    
    save.write('</player>')
    save.close()

# Writes a room to a save file
def save_room(room, path):
    save = open(path, 'w')
    save.write('<?xml version="1.0"?>\n')
    save.write('<room>\n')
    
    save.write('<desc>%s</desc>\n' % room.desc)
    
    for item in room.items.values():
        save_item(save, item)
    
    for portal in room.portals.values():
        save_portal(save, portal)
    
    for container in room.containers.values():
        save_container(save, container)
    
    save.write('</room>')
    save.close()

# Writes an item to a save file
def save_item(save, item):
    save.write('<item>\n')
    save.write('<name>%s</name>\n' % item.name)
    save.write('<desc>%s</desc>\n' % item.desc)
    save.write('<inspect_desc>%s</inspect_desc>\n' % item.inspect_desc)
    save.write('<portable>%d</portable>\n' % int(item.portable))
    save.write('<hidden>%d</hidden>\n' % int(item.hidden))
    
    # Save scripts
    save_scripts(save, item.scripts)
    
    save.write('</item>\n')

# Writes a portal to a save file
def save_portal(save, portal):
    save.write('<portal x="%d" y="%d" z="%d">\n' % portal.coords)
    save.write('<name>%s</name>\n' % portal.name)
    save.write('<direction>%s</direction>\n' % portal.direction)
    save.write('<desc>%s</desc>\n' % portal.desc)
    save.write('<inspect_desc>%s</inspect_desc>\n' % portal.inspect_desc)
    save.write('<locked>%d</locked>\n' % int(portal.locked))
    save.write('<hidden>%d</hidden>\n' % int(portal.hidden))
    save.write('<key>%s</key>\n' % portal.key)
    
    # Save scripts
    save_scripts(save, portal.scripts)
    
    save.write('</portal>\n')

# Writes a container to a save file
def save_container(save, container):
    save.write('<container>\n')
    save.write('<name>%s</name>\n' % container.name)
    save.write('<desc>%s</desc>\n' % container.desc)
    save.write('<inspect_desc>%s</inspect_desc>\n' % container.inspect_desc)
    save.write('<locked>%d</locked>\n' % int(container.locked))
    save.write('<hidden>%d</hidden>\n' % int(container.hidden))
    save.write('<key>%s</key>\n' % container.key)
    
    # Save scripts
    save_scripts(save, container.scripts)
    
    for item in container.items.values():
        save_item(save, item)
    
    save.write('</container>\n')

# Writes the scripts to a save file
def save_scripts(save, scripts):
    for script in scripts:
        save.write('<%s_script>\n' % script)
        for action in scripts[script]:
            save.write('<%s>%s</%s>\n' % (action[0], action[1], action[0]))
        save.write('</%s_script>\n' % script)