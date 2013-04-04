#!/usr/bin/env python
"""Script to autogen a class for input parsing from an XML file"""
import sys
from xml.sax import make_parser
# from Q2API.xml.gen_class_from_xml import NodeHandler  ### this is the legacy version
from Q2API.xml.gen_from_base_xml import NodeHandler
"""This tool now uses the base_xml as the base class to get the flatten capability
    as long as new nodes added are also added to the 'children' data structure.
    
"""

def generate_class(target_name):
    """Make a "handler" class from an XML file for the wedge framework"""
    saxparser = make_parser()
    saxparser.setContentHandler(NodeHandler(target_name+'.py'))
    saxparser.parse(sys.argv[1])

if __name__ == '__main__':
    if sys.argv[1][-4:] != '.xml':
        print "mk_class operates on '.xml' files to make python classes"
        sys.exit(-1)
    generate_class(sys.argv[1][:-4])

