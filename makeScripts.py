import textwrap
import engine_helper
import validator

scripts = {}
verb_list = engine_helper.valid_verbs

def makeScripts():
    
    script = {} # dictionary for this script  format is {verb:( (action1), (action2), (...) )}
    actions_list = [] # list to hold tuples until finalized
    
    # GET VERB TO OVERIDE
    print ""
    print textwrap.fill('Enter the action word (verb) you would like to override. This is the first word a player types in their command.  '
                        'Currently scripts are limited to the %s commands.', width=100) % str(verb_list).strip('[]').replace("'", '')
    
    valid_verb = False
    while valid_verb == False:
        ans = raw_input('\n>').strip().lower()
        if ans in verb_list:
            ovr_verb = ans
            valid_verb = True
        else:
            print '\nThat is not a valid verb for scripts, try again.'
            
    # GET ACTION
    # introductory explanation text Only display on first pass through.
    if len(scripts) == 0:  
        print ""
        print textwrap.fill('In this segment you will enter the action or actions you want to happen when a player uses the verb you just entered '
                        'on this portal or item.  Any invalid commands will be passed over and not processed.  Proper Action format is 3 parts, '
                        '(verb, object, delay) verb is the action taken, object is the subject of that action, and delay is the time (in whole seconds) '
                        'waited before the action happens. For example take apple 5 will wait 5 seconds and take the object named apple.' , width=100).strip()
        print ""
        print textwrap.fill('A few other things to note are that multiple actions will happen in the order they are entered as long as they are valid, '
                        'if multiple actions have delays the delays do not run simultaneously, when the previous action has ran the delay of the '
                        'following action will begin.  For Example take apple 2, open door 5, close door 5 would take 12 seconds for the door to close.  '
                        'And Finally, if you want the original action entered to happen (the one the script is written to override) you will have to '
                        'include it with the actions you enter for the script.',width=100).strip()
    
    # begin work of getting actions    
    actions_done = False
    while actions_done == False:
        print ""
        print textwrap.fill('Enter the action seperated by a space.  Example take apple 5', width=100).strip()
        
        action_done = False
        while action_done == False:
            ans = raw_input('\n>').strip().lower()
            ans = ans.split(' ')
            if len(ans) < 3:  # ans must be 3 or more words items
                print ''
                print textwrap.fill('Your action needs to be at least 3 parts seperated with a space.  (verb object delay) Try again.',width=100)
            
            elif len(ans) >= 3:   # has enough words create parts
                verb = ans[0]
                # validate verb
                if verb not in verb_list:
                    print ""
                    print textwrap.fill('The first word should be one of the verbs %s.  Try again', width=100) % str(verb_list).strip('[]').replace("'", '')      
                else:
                    delay = ans[-1]
                    # make object string for multiword objects (Remove first and last, middle word(s) is/are object) 
                    ans.remove(ans[0]) 
                    ans.remove(ans[-1])
                    object = str(ans).strip('[]').replace(', ', ' ').replace("'", "")
            
            # validate delay is an int and in range        
            tryFlag = False
            try:
                delay = int(delay)
            except:
                print ""
                print textwrap.fill('The last portion of your action, the delay (in seconds) must be a whole number between 0 and 1200.  Try again.', width=100).strip()
                tryFlag = True
            #validate in range allowed
            if tryFlag == False:
                if delay < 0 or delay > 1200:
                    print ""
                    print textwrap.fill('Your delay must be a whole number between 0 and 1200.  Try Again.')    
                else:
                    # make this action tuple
                    action = (verb, object, delay)
                    # append to list
                    actions_list.append(action)
                    print actions_list
                    action_done = True
        
        print ""
        print textwrap.fill('You have completed that action do you want to add another action to this script?  (Yes or No)', width=100).strip()
        ans = validator.validYesNo()
        if ans == 'no':
            # write to script dict
            scripts[ovr_verb] = tuple(actions_list)
            print scripts
            actions_done = True
    
    #MAKE ANOTHER SCRIPT?
    print ""
    print textwrap.fill('Do you want to make a script for another verb?  (Yes or No)', width=100).strip()
    ans = validator.validYesNo()
    if ans == 'yes':
        makeScripts()
    if ans == 'no':
        return scripts
    

if __name__ == '__main__':
    makeScripts()   