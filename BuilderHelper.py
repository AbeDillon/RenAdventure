
    
def description(obj_type):
    """
    function for adding a general description
    obj_type = type of object being worked on (portal, item, etc...)
    """
    self.logger.write_line('entered addDescription function')
    text = '\n' +textwrap.fill ('Enter a description for the ' + type , width=100).strip()
                                
    self.send_message_to_player(text)        
    desc = self.get_cmd_from_player()        
    
    self.logger.write_line('exiting description func returned = %s' % desc)

    return desc

def inspectionDescription(obj_type):
    """
    Function for adding Inspection Description
    obj_type = type of object being worked on (portal, item, etc...)
    """
    self.logger.write_line('entered addInspectionDescription function')
    text = '\n' +textwrap.fill ('Enter an inspection (more detailed) description for the ' + type , width=100).strip()
                                
    self.send_message_to_player(text)        
    i_desc = self.get_cmd_from_player()
    
    self.logger.write_line('exit inspection description')
    
    return i_desc

def getBool(obj_type, bool_type):
    """
    function for defining a bool attribute of a object
    Returns true or false
    """
    
    
    
