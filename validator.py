
names = ['door', 'sword', 'key', 'piano', 'chest']

def validate_name(name, list):  #  function to validate if name is in a given list
    if name in list:  # If the name is in list it returns False
        return False
    elif name not in list:  #  If the name is not in the list returns True
        return True
    
    
def original_name(name, list):  #  Function to validate a given name against a given list/dictionary for originality.
    '''Names of things must be unique this will take a given name and validate it against a given list/dictionary '''
    if len(name) <= 0:
        print 'Names must contain at least 1 character to be valid.'
        return False
    if name in list:
        print 'That name has already been used.'
        return False
    else:
        return True

def validate_coords(coords):

    ''' coords must be integers '''

    # can the coordinates properly converted to integers?
    if len(coords) != 3:  #  Must be length of 3
        print '\nCoordinates must be 3 integers (for example 12 4 1).'
        return False
    for coord in coords:
        try:
            coord = int(coord)
        except:
            print "\nCoordinates must be integers (whole numbers)."
            return False

    return True