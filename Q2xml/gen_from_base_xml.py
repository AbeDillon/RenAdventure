#!/usr/bin/env python
"""Code gen helpers and NodeHandler instance for parsing an XML
    example and creating a auto-generated python object.

"""

from xml.sax.handler import ContentHandler

def collect_node(in_dict, node_data):
    """Takes the node dictionary and a new node instance and returns an updated dict"""
    if node_data['name'] not in in_dict:
        in_dict[node_data['name']] = node_data
    else:
        print "WARNING: ", node_data, "found for node that already exists by that name", in_dict[node_data['name']]
        print "WARNING: will assume that the node is the same and that it can appear at many points in the hierarchy"
        # need to make sure that we don't already have this parent
        if node_data['parents'][0] not in in_dict[node_data['name']]['parents']:
            in_dict[node_data['name']]['parents'].append(node_data['parents'][0])
        else:
            print "Duplicate parent, do not need to add"

def eval_children(in_dict):
    """Identify (direct) children for each node, not just descendants"""
    for node_name in in_dict:
        this_node = in_dict[node_name]
        if this_node['parents'][0] != None: # if this node is not the root and no other node can have a None parent   
            for parent in this_node['parents']:
                if node_name not in in_dict[parent]['children']:
                    in_dict[parent]['children'].append(node_name)    # put this nodename in the parent's child list

def file_header(name):
    """Return a string code block with the "header" of the autogen class module"""
    tmp_block = []
    tmp_block.append('# XML Parser/Data Access Object '+str(name))
    tmp_block.append('"""AUTO-GENERATED Source file for '+str(name).replace('\\', '\\\\')+'"""')
    tmp_block.append(''.join(['import', ' ', 'xml.sax']))
    tmp_block.append(''.join(['import', ' ', 'Queue']))
    tmp_block.append(''.join(['import', ' ', 'Q2API.xml.base_xml']))
    tmp_block.append('')
    tmp_block.append('def process_attrs(attrs):')
    tmp_block.append('\t"""Process sax attribute data into local class namespaces"""')
    tmp_block.append('\tif attrs.getLength() == 0:')
    tmp_block.append('\t\treturn {}')
    tmp_block.append('\ttmp_dict = {}')
    tmp_block.append('\tfor name in attrs.getNames():')
    tmp_block.append('\t\ttmp_dict[name] = attrs.getValue(name)')
    tmp_block.append('\treturn tmp_dict')
    tmp_block.append('')
    return '\n'.join(tmp_block)+'\n'

def create_source(in_dict):
    """Create classes for XML nodes"""
    node_classes = {}   # used to maintain the order of the classes
    for node_name in in_dict:
        this_node = in_dict[node_name]
        tmp_class = []
        
        # class decl
        tmp_class.append(''.join(['class', ' ', node_name, '_q2class', '(Q2API.xml.base_xml.XMLNode):']))
        
        # docstring
        tmp_class.append(''.join(['\t', '"""', node_name, ' : ', str(this_node), '"""']))
        
        # init method
        if this_node['parents'][0] == None: # root node
            tmp_class.append(''.join(['\t', 'def', ' ', '__init__(self, attrs):']))
            tmp_class.append(''.join(['\t\t', 'self.level = ', str(this_node['level'])]))
            tmp_class.append(''.join(['\t\t', 'self.path = ', str(this_node['path'])]))
            for child in this_node['children']:
                tmp_class.append(''.join(['\t\t', 'self.', child, ' = []']))
            
            ### this is where the name of the node that will be "flattened to" is set
            #   we need to use the original name here
            tmp_class.append(''.join(['\t\t', 'Q2API.xml.base_xml.XMLNode.__init__(self, "'+this_node['original_name']+'", attrs, None, [])']))

        else:
            tmp_class.append(''.join(['\t', 'def', ' ', '__init__(self, attrs):']))
            tmp_class.append(''.join(['\t\t', 'self.level = ', str(this_node['level'])]))
            tmp_class.append(''.join(['\t\t', 'self.path = ', str(this_node['path'])]))
            if this_node['children'] != []:
                for child in this_node['children']:
                    tmp_class.append(''.join(['\t\t', 'self.', child, ' = []']))
                
                ### this is where the name of the node that will be "flattened to" is set
                #   we need to use the original name here
                tmp_class.append(''.join(['\t\t', 'Q2API.xml.base_xml.XMLNode.__init__(self, "'+this_node['original_name']+'", attrs, None, [])']))
            else:

                ### this is where the name of the node that will be "flattened to" is set
                #   we need to use the original name here
                tmp_class.append(''.join(['\t\t', 'Q2API.xml.base_xml.XMLNode.__init__(self, "'+this_node['original_name']+'", attrs, None, [])']))
 
        # aggregate for return
        if this_node['level'] not in node_classes:
            node_classes[this_node['level']] = {}
        node_classes[this_node['level']][node_name] = '\n'.join(tmp_class)+'\n'
    return node_classes

def create_handler(in_dict):
    """Generate the handler for sax-parsing the input XML"""
    tmp_block = []
    tmp_block.append('class NodeHandler(xml.sax.handler.ContentHandler):')
    tmp_block.append('\t"""SAX ContentHandler to map XML input class/object"""')
    tmp_block.append('\tdef __init__(self, return_q):     # overridden in subclass')
    tmp_block.append('\t\tself.obj_depth = [None]')
    tmp_block.append('\t\tself.return_q = return_q')
    tmp_block.append('\t\tself.in_value_tag = False')
    tmp_block.append('\t\tself.char_buffer = []')
    tmp_block.append('\t\txml.sax.handler.ContentHandler.__init__(self)   # superclass init')
    tmp_block.append('')
    
    # startElement
    tmp_block.append('\tdef startElement(self, name, attrs): # creating the node along the path being tracked')
    tmp_block.append('\t\t"""Override base class ContentHandler method"""')
    tmp_block.append("\t\tif ':' in name:\n\t\t\tname = name.replace(':', '_')")
    tmp_block.append("\t\tif '-' in name:\n\t\t\tname = name.replace('-', '_')")
    tmp_block.append("\t\tif '.' in name:\n\t\t\tname = name.replace('.', '_')")
    tmp_block.append('\t\tif name == "":')
    tmp_block.append('\t\t\traise ValueError, "XML Node name cannot be empty"\n')
    for node_name in in_dict:
        this_node = in_dict[node_name]
        if this_node['parents'][0] == None:
            tmp_block.append('\t\telif name == "'+node_name+'":')   # grab each node
            tmp_block.append('\t\t\tp_attrs = process_attrs(attrs)')
            tmp_block.append('\t\t\tself.obj_depth.append('+node_name+'_q2class(p_attrs))')
        else:
            tmp_block.append('\t\telif name == "'+node_name+'":')   # grab each node
            tmp_block.append('\t\t\tp_attrs = process_attrs(attrs)')
            tmp_block.append('\t\t\tself.obj_depth.append('+node_name+'_q2class(p_attrs))')
            if this_node['children'] == []:
                # tmp_block.append('\t\t\tself.charbuffer = []')
                tmp_block.append('\t\t\tself.in_value_tag = True')
        tmp_block.append('')
    
    # endElement
    tmp_block.append('\tdef endElement(self, name): # need to append the node that is closing in the right place')
    tmp_block.append('\t\t"""Override base class ContentHandler method"""')
    tmp_block.append("\t\tif ':' in name:\n\t\t\tname = name.replace(':', '_')")
    tmp_block.append("\t\tif '-' in name:\n\t\t\tname = name.replace('-', '_')")
    tmp_block.append("\t\tif '.' in name:\n\t\t\tname = name.replace('.', '_')")
    tmp_block.append('\t\tif name == "":')
    tmp_block.append('\t\t\traise ValueError, "XML Node name cannot be empty"\n')
    for node_name in in_dict:
        this_node = in_dict[node_name]
        if this_node['parents'][0] == None:
            tmp_block.append('\t\telif name == "'+node_name+'":')   # grab each node
            tmp_block.append('\t\t\tif len(self.char_buffer) != 0:')
            tmp_block.append('\t\t\t\tself.obj_depth[-1].value = "".join(self.char_buffer)')
            tmp_block.append('\t\t\t# root node is not added to a parent; stays on the "stack" for the return_object')
        else:
            tmp_block.append('\t\telif name == "'+node_name+'":')   # grab each node
            tmp_block.append('\t\t\tif len(self.char_buffer) != 0:')
            tmp_block.append('\t\t\t\tself.obj_depth[-1].value = "".join(self.char_buffer)')
            tmp_block.append('\t\t\tself.obj_depth[-2].'+node_name+'.append(self.obj_depth[-1]) #  make this object a child of the next object up...')
            tmp_block.append('\t\t\tself.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well')
            tmp_block.append('\t\t\tself.obj_depth.pop() # remove this node from the list, processing is complete')
            if this_node['children'] == []:
                tmp_block.append('\t\t\tself.in_value_tag = False')
                tmp_block.append('\t\t\tself.char_buffer = []')        
        tmp_block.append('')
    
    # characters
    tmp_block.append('\tdef characters(self, in_chars):')
    tmp_block.append('\t\t"""Override base class ContentHandler method"""')
    tmp_block.append('\t\tif self.in_value_tag == True:')
    tmp_block.append('\t\t\tself.char_buffer.append(in_chars)')
    tmp_block.append('')    

    # end document
    tmp_block.append('\tdef endDocument(self):')
    tmp_block.append('\t\t"""Override base class ContentHandler method"""')
    tmp_block.append('\t\tself.return_q.put(self.obj_depth[-1])')
    return '\n'.join(tmp_block)+'\n'

def create_wrapper():
    """Wrapper function in the file to kick off the sax parse, class autogen and
        return the object instance
    
    """
    tmp_block = []
    tmp_block.append('def obj_wrapper(xml_stream):')
    tmp_block.append('\t"""Call the handler against the XML, then get the returned object and pass it back up"""')
    tmp_block.append('\ttry:')
    tmp_block.append('\t\treturn_q = Queue.Queue()')
    tmp_block.append('\t\txml.sax.parseString(xml_stream, NodeHandler(return_q))')
    tmp_block.append('\t\treturn (True, return_q.get())')
    tmp_block.append('\texcept Exception, e:')
    tmp_block.append('\t\treturn (False, (Exception, e))')
    
    tmp_block.append('')
    return '\n'.join(tmp_block)+'\n'

class NodeHandler(ContentHandler):
    """Handler to map XML input file into a class 'factory' to parse and create a python obj from XML"""
    def __init__(self, output_name):     # overridden in subclass
        self.depth = [None]
        self.nodes = {}
        self.output_name = output_name
        ContentHandler.__init__(self)   # superclass init
    
    def startDocument(self):
        """Override base class ContentHandler method"""
        print "Starting document parsing"
    
    def startElement(self, name, attrs):
        """Override base class ContentHandler method"""
        print "Start element:", name, self.depth
        print "\tParent at this point:", self.depth[-1]
        collect_node(self.nodes, {'name': name.replace(':', '_').replace('-', '_').replace('.', '_'),
                                  'original_name': name,    # added for preservation in the creation of the XML node for later flattening
                                  'parents': [self.depth[-1]], 'level': len(self.depth),
                                  'path': self.depth[:], 'children': []})
        self.depth.append(name.replace(':', '_').replace('-', '_').replace('.', '_'))
        
    def endElement(self, name):
        """Override base class ContentHandler method"""
        print "End element:", name
        if self.depth[-1] == name.replace(':', '_').replace('-', '_').replace('.', '_'):
            self.depth.pop()
        else: print "ERROR: unexpected node", name.replace(':', '_').replace('-', '_').replace('.', '_'), "found instead of", self.depth[-1]
        
    def endDocument(self):
        """Override base class ContentHandler method"""
        print "End of document parsing"
        eval_children(self.nodes)
        print "Results:"
        for node_name in self.nodes:
            print node_name
            print self.nodes[node_name]
            print
        class_dict = create_source(self.nodes)
        levels = class_dict.keys()
        levels.sort(reverse = True)
        
        # stream source to file
        out_file = open(self.output_name, 'w')
        out_file.write(file_header(self.output_name).replace('\t', '    ')) # swap tabs for spaces
        for level in levels:
            class_names = class_dict[level].keys()
            class_names.sort()
            for class_name in class_names:
                out_file.write(class_dict[level][class_name].replace('\t', '    ')+'\n')
        out_file.write(create_handler(self.nodes).replace('\t', '    ')+'\n')
        out_file.write(create_wrapper().replace('\t', '    ')+'\n')
        # write root node
        out_file.close()

