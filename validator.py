# global list of names across all named objects to validate originality will need to appended and removed as onjects are added removed
names = ['door', 'sword', 'key', 'piano', 'chest']

# lists of item types Append remove similar to names above.  Required to make sure someone does not specify a portal name as an item in a room this
# would break our loader xml etc becuase they do not have similar attributes.  Am I correct?
# need to add additional layer of validation in all (make**.py) against these lists still.
portal_list = []
item_list = []

def validate_name(name, list):  #  function to validate if name is in a given list
    if name in list:  # Name in List True
        return True
    elif name not in list:  # Name not in list False
        return False
    
    
def original_name(name, list):  #  Function to validate a given name against a given list/dictionary for originality.
    '''Names of things must be unique this will take a given name and validate it against a given list/dictionary '''
    if len(name) <= 0:
        print '\nNames must contain at least 1 character to be valid.'
        return False
    if name in list:  
        #print 'That name has already been used.'
        return True
    else:
        return False

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

def validYesNo():  # Validates an answer is a simple Yes or No returns answer Yes or no
    while True:
        ans = raw_input('\n>').strip().lower()
        if ans == 'yes' or ans == 'y':
            ans = 'yes'
            return ans 
        elif ans == 'no' or ans == 'n':
            ans = 'no'
            return ans
        else:
            print "\nAnswer must be yes or no.  Try again."
