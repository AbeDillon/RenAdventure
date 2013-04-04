"""Quick/dirty code to try to just get the root node"""
import Queue
from xml.sax import make_parser
from xml.sax import parseString
from xml.sax.handler import ContentHandler

class NodeHandler(ContentHandler):
    """Handler to extract only the XML root node"""
    def __init__(self, found_name):     # overridden in subclass
        self.found_node = False
        self.found_name = found_name
        self.found_name.append(False)
        ContentHandler.__init__(self)   # superclass init
    
    def startElement(self, name, attrs):
        """Override base class ContentHandler method"""
        if self.found_node == False:
            self.found_node = True
            self.found_name[0] = name            

def extract_root_node(xml_stream):
    """Make a "handler" class from an XML file for the wedge framework"""
    found_name = []
    saxparser = make_parser()
    parseString(xml_stream, NodeHandler(found_name))
    return found_name[0]

class NodeHandler2(ContentHandler):
    """Handler to extract only the XML root node"""
    def __init__(self, found_name):     # overridden in subclass
        self.found_node = False
        self.found_name = found_name
        ContentHandler.__init__(self)   # superclass init
    
    def startElement(self, name, attrs):
        """Override base class ContentHandler method"""
        if self.found_node == False:
            self.found_node = True
            self.found_name[0] = name
            self.found_name[1] = attrs

def extract_root_node_and_attrs(xml_stream):
    """Make a "handler" class from an XML file for the wedge framework"""
    found_name = [None, None]
    saxparser = make_parser()
    parseString(xml_stream, NodeHandler2(found_name))
    return (found_name[0], found_name[1])

def process_attrs_to_string(attrs):
    """Process sax attribute data into a string"""
    tmp_list = []
    if attrs.getLength() == 0:
        return ''
    for name in attrs.getNames():
        # tmp_dict[name] = attrs.getValue(name)
        tmp_list.extend([' ', name, '="', attrs.getValue(name), '"'])    
    return ''.join(tmp_list)

def process_attrs_to_dict(attrs):
    """Process sax attribute data into local class namespaces"""
    if attrs.getLength() == 0:
        return {}
    tmp_dict = {}
    for name in attrs.getNames():
        tmp_dict[name] = attrs.getValue(name)
    return tmp_dict

class NodeHandler3(ContentHandler):
    '''Handler to extract all non-root node data and flatten is back out to xml'''
    def __init__(self, return_q):
        self.return_q = return_q
        self.found_root_node = False
        self.in_value_tag = False
        self.char_buffer = []
        self.out_xml = []
        self.root_node_name = None
        self.root_attrs = None
        self.depth = 0
        ContentHandler.__init__(self)
    
    def startElement(self, name, attrs):
        self.depth += 1
        if self.found_root_node == False:           # root node
            self.found_root_node = True
            self.root_node_name = name
            self.root_attrs = attrs
        else:                                       # non-root node
            self.in_value_tag = True                # set flag indicating that we're in a tag
            self.char_buffer = []                   # discard whitespace that was accumulated
            self.out_xml.extend(['<', name, process_attrs_to_string(attrs),'>'])
    
    def endElement(self, name):
        self.out_xml.append(''.join(self.char_buffer))       # append the character data to the buffer        
        if self.depth != 1:
            self.out_xml.extend(['</', name, '>'])      # append the end tag
        self.in_value_tag = False                   # reset the flag 
        self.char_buffer = []                       # empty the character buffer
        self.depth -= 1
    
    def characters(self, in_chars):
        if self.in_value_tag == True:
            self.char_buffer.append(in_chars)

    def endDocument(self):
        tmp_xml = ''.join(self.out_xml)        # flatten the xml for return, discarding the last node
        self.return_q.put((self.root_node_name, self.root_attrs, tmp_xml))

def extract_root_node_attrs_and_content(xml_stream):
    """Make a "handler" class from an XML file for the wedge framework"""
    saxparser = make_parser()
    return_q = Queue.Queue()
    parseString(xml_stream, NodeHandler3(return_q))
    return return_q.get() 
