#!/usr/bin/env python
"""Class and helpers for a python object that knows how to flatten itself to XML.
    Also, allows for child and parent objects and can flatten all children from
    the root down into a single string return
"""
import cgi
import types
import xml.sax.saxutils as SU

def make_attributes_safe_sql_quotes(attrs):
    """Make a well formed attribute block, ### needs validation and error handling."""
    if attrs is not None:
        tmp_attrs = []
        for a_name in attrs:
            entities = {'"': '&quot;' , "'": '&apos;'}
            # this should be reliable because we have escaped out both types of quotes already
            tmp_attrs.append(''.join([a_name, '=', '"', SU.escape(attrs[a_name], entities), '"']))
        return ' '.join(tmp_attrs)
    else:       # if no attrs were passed return an empty string
        return ''

def make_attributes(attrs):
    """Make a well formed attribute block, ### needs validation and error handling."""
    if attrs is not None:
        tmp_attrs = []
        for a_name in attrs:
            tmp_attrs.append(''.join([a_name, '=', SU.quoteattr(attrs[a_name])]))
        return ' '.join(tmp_attrs)
    else:       # if no attrs were passed return an empty string
        return ''

# probably need to filter the name characters here (except on invalid names or escape them)
def make_start(name, attrs):
    """Assemble the XML start tag (name and attrs block), ### needs validation."""
    tmp_start = []
    tmp_start.append('<'+name)
    if attrs != {} and attrs != None:
        tmp_start.append(' ')
        tmp_start.append(make_attributes(attrs))
    tmp_start.append('>')
    return ''.join(tmp_start)

def make_start_safe_sql_attrs(name, attrs):
    """Assemble the XML start tag (name and attrs block), ### needs validation."""
    tmp_start = []
    tmp_start.append('<'+name)
    if attrs != {} and attrs != None:
        tmp_start.append(' ')
        tmp_start.append(make_attributes_safe_sql_quotes(attrs))
    tmp_start.append('>')
    return ''.join(tmp_start)

def make_end(name):
    """Make an end tag from a node name."""    
    return '</'+name+'>'
    
# may want to replace cgi.escape with the sax escape
def flatten(name, attrs = None, content = ''):
    """Make an xml stream from an object. Function is aware of the types of "content"
        that it may have to serialize. If the content is string or int, it is simply
        placed in the string. If the content is a list of children, they are each
        asked to flatten themselves.
        KEY ASSUMPTION: this only works when all objects passed to the function in the
        list are actually xml_node objects or descendants that implement a .flatten_self
        method.
    
    """
    if (type(content) == types.ListType) or (type(content) == types.TupleType):     # if this is a list of child nodes
        tmp_list = []
        for element in content:
            try:
                tmp_list.append(element.flatten_self())
            except Exception, e:
                tmp_list.append(make_start('UNKNOWN_OBJECT_TYPE', {}) + cgi.escape(str((content, (Exception, e)))) + make_end('UNKNOWN_OBJECT_TYPE'))
        return make_start(name, attrs) + ''.join(tmp_list) + make_end(name)
    elif type(content) == types.StringType:     # if this is already a string
        return make_start(name, attrs) + cgi.escape(content) + make_end(name)
    elif type(content) == types.IntType:
        return make_start(name, attrs) + cgi.escape(str(content)) + make_end(name)
    elif type(content) == types.UnicodeType:     # unicode to string conversion
        return make_start(name, attrs) + cgi.escape(str(content)) + make_end(name)
    else:
        # let's take a different approach here
        return make_start('UNKNOWN_OBJECT_TYPE', {}) + cgi.escape(str(content)) + make_end('UNKNOWN_OBJECT_TYPE')

def flatten_safe_sql_attrs(name, attrs = None, content = ''):
    """Make an xml stream from an object. Function is aware of the types of "content"
        that it may have to serialize. If the content is string or int, it is simply
        placed in the string. If the content is a list of children, they are each
        asked to flatten themselves.
        KEY ASSUMPTION: this only works when all objects passed to the function in the
        list are actually xml_node objects or descendants that implement a .flatten_self
        method.
    
    """
    if (type(content) == types.ListType) or (type(content) == types.TupleType):     # if this is a list of child nodes
        tmp_list = []
        for element in content:
            try:
                tmp_list.append(element.flatten_self_sql_safe_attrs())
            except Exception, e:
                tmp_list.append(make_start('UNKNOWN_OBJECT_TYPE', {}) + cgi.escape(str((content, (Exception, e)))) + make_end('UNKNOWN_OBJECT_TYPE'))
        return make_start_safe_sql_attrs(name, attrs) + ''.join(tmp_list) + make_end(name)
    elif type(content) == types.StringType:     # if this is already a string
        return make_start_safe_sql_attrs(name, attrs) + cgi.escape(content) + make_end(name)
    elif type(content) == types.IntType:
        return make_start_safe_sql_attrs(name, attrs) + cgi.escape(str(content)) + make_end(name)
    elif type(content) == types.UnicodeType:     # unicode to string conversion
        return make_start_safe_sql_attrs(name, attrs) + cgi.escape(str(content)) + make_end(name)
    else:
        # let's take a different approach here
        return make_start('UNKNOWN_OBJECT_TYPE', {}) + cgi.escape(str(content)) + make_end('UNKNOWN_OBJECT_TYPE')

# may want to replace cgi.escape with the sax escape    
def flatten_to_unicode(name, attrs = None, content = ''):
    """Make an xml stream from an object. Function is aware of the types of "content"
        that it may have to serialize. If the content is string or int, it is simply
        placed in the string. If the content is a list of children, they are each
        asked to flatten themselves.

        KEY ASSUMPTION: this only works when all objects passed to the function in the
        list are actually xml_node objects or descendants that implement a .flatten_self
        method.

        MODIFIED TO ATTEMPT TO OUTPUT IN UNICODE
    
    """
    if (type(content) == types.ListType) or (type(content) == types.TupleType):     # if this is a list of child nodes
        tmp_list = []
        for element in content:
            try:
                tmp_list.append(unicode(element.flatten_self_to_utf8()))
            except Exception, e:
                tmp_list.append(unicode(make_start('UNKNOWN_OBJECT_TYPE', {})) + cgi.escape(unicode(str((content, (Exception, e))))) + unicode(make_end('UNKNOWN_OBJECT_TYPE')))
        return unicode(make_start(name, attrs)) + u''.join([unicode(x) for x in tmp_list]) + unicode(make_end(name))

    elif type(content) == types.StringType:     # if this is already a string
        return unicode(make_start(name, attrs)) + cgi.escape(unicode(content)) + unicode(make_end(name))

    elif type(content) == types.IntType:
        return unicode(make_start(name, attrs)) + cgi.escape(unicode(str(content))) + unicode(make_end(name))

    elif type(content) == types.UnicodeType:     # unicode to string conversion
        return unicode(make_start(name, attrs)) + cgi.escape(content) + unicode(make_end(name))

    else:
        return unicode(make_start('UNKNOWN_OBJECT_TYPE', {})) + cgi.escape(unicode(content)) + unicode(make_end('UNKNOWN_OBJECT_TYPE'))

class XMLNode(object):
    """Base class for creating XML node objects that can hold attributes, values and
        children and knows how to flatten itself.
    
    """
    def __init__(self, name, attrs = None, value = None, children = None):
        self.name = name
        self.attrs = attrs      # attribute dictionary
        self.value = value      # value as string (could be serialization of children...)
        self.children = children    # if this is a parent node
        
    def flatten_self(self):
        """Method on base object for creating XML representation of the object.
            The logic here is to determine how to call the flatten helper function.
        
        """
        if self.value == None and self.children is not None:
            return flatten(self.name, self.attrs, self.children)
        elif self.value != None and (self.children is None or self.children == []):
            return flatten(self.name, self.attrs, self.value)
        elif  self.value == None and self.children is None:
            return flatten(self.name, self.attrs, '')
        else:
            raise ValueError, 'XML Node object does not have expected data '+str(self.value)+' '+str(self.children)

    def flatten_self_sql_safe_attrs(self):
        '''
            U:\>python
            ActivePython 2.5.1.1 (ActiveState Software Inc.) based on
            Python 2.5.1 (r251:54863, May  1 2007, 17:47:05) [MSC v.1310 32 bit (Intel)] on
            win32
            Type "help", "copyright", "credits" or "license" for more information.
            >>> import Q2API.xml.base_xml as BX
            >>> t1 = BX.XMLNode('test', {'r1': """test's "test" """}, None, None)
            >>> t1.flatten_self()
            '<test r1="test\'s &quot;test&quot; "></test>'
            >>> print t1.flatten_self()
            <test r1="test's &quot;test&quot; "></test>
            >>> print t1.flatten_self_sql_safe_attrs()
            <test r1="test&apos;s &quot;test&quot; "></test>
            >>> t1 = BX.XMLNode('exterior', None, None, [t1])
            >>> t1 = BX.XMLNode('test', {'r1': """test's "test" """}, None, None)
            >>> t2 = BX.XMLNode('exterior', None, None, [t1])
            >>> t2.flatten_self()
            '<exterior><test r1="test\'s &quot;test&quot; "></test></exterior>'
            >>> t2.flatten_self_sql_safe_attrs()
            '<exterior><test r1="test&apos;s &quot;test&quot; "></test></exterior>'
            >>>
        '''
        
        if self.value == None and self.children is not None:
            return flatten_safe_sql_attrs(self.name, self.attrs, self.children)
        elif self.value != None and (self.children is None or self.children == []):
            return flatten_safe_sql_attrs(self.name, self.attrs, self.value)
        elif  self.value == None and self.children is None:
            return flatten_safe_sql_attrs(self.name, self.attrs, '')
        else:
            raise ValueError, 'XML Node object does not have expected data '+str(self.value)+' '+str(self.children)

    def flatten_self_to_utf8(self):

        if self.value == None and self.children is not None:
            return flatten_to_unicode(self.name, self.attrs, self.children).encode('ascii', 'xmlcharrefreplace')

        elif self.value != None and (self.children is None or self.children == []):
            return flatten_to_unicode(self.name, self.attrs, self.value).encode('ascii', 'xmlcharrefreplace')

        elif  self.value == None and self.children is None:
            return flatten_to_unicode(self.name, self.attrs, '').encode('ascii', 'xmlcharrefreplace')

        else:
            raise ValueError, 'XML Node object does not have expected data '+unicode(self.value)+' '+unicode(self.children)
