


def validate_name(name, dictionary):  #  Function to validate a given name against a given dictionary for originality.
    '''Names of things must be unique this will take a given name and validate it against a given list/dictionary '''
    if name == '':
        print 'Names must contain at least 1 character to be valid.'
        return False
    if name in dictionary:
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