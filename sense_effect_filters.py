import engine
import re
import random

_Sense_Effect_Map = {'blind': 'sight',
                     'hallucinating': 'sight',
                     'deaf': 'sound'}

_Stack_Probability = {1: .50,
                      2: .65,
                      3: .77,
                      4: .87,
                      5: .95}

def filter_messages(messages):
    # Runs all of the messages through the appropriate filters
    filtered_messages = []

    for player_name, message in messages:
        engine._Characters_Lock.acquire()
        player = engine._Characters[player_name]
        engine._Characters_Lock.release()

        if isinstance(player, engine.Player):   # Make sure that we are not looking at an NPC
            filtered_message = ''

            while len(message) > 0:
                if message[0] == '<':   # Message starts with a tag
                    tags = re.findall('<.*?>', message) # Find the tags in the message
                    tag_string = re.findall(tags[0]+'(.*)'+tags[1], message)    # Get the string between the tags
                    message = message.replace(tags[0] + tag_string[0] + tags[1], '') # Cut the filtered sub string out of the message

                    tag_string = filter_message_segment(player, tag_string[0], tags[0])
                    filtered_message += tag_string
                else:   # Message does not start with a tag
                    tag_index = message.find('<')
                    if tag_index == -1: # Did not find another tag
                        filtered_message += message
                    else:
                        tag_string = message[:tag_index] # Get the segment that is before the next tag
                        message.replace(tag_string, '')
                        filtered_message += tag_string

            filtered_messages.append((player.name, filtered_message))

    return filtered_messages

def filter_message_segment(player, message, tag):
    # Runs the segment through the appropriate filters
    tag = tag.replace('<', '')
    tag = tag.replace('>', '')

    for effect in player.sense_effects:
        sense = _Sense_Effect_Map.get(effect, None) # Get the affected sense
        if sense == tag:
            stacks = player.sense_effects[effect]
            script = effect + '(message, stacks)'
            message = eval(script) # Apply the filter to the message

    return message

def blind(message, stacks):
    # Replaces a percentage of words in the message with ellipses
    words = message.split()
    num_replace = int(len(words) * _Stack_Probability[stacks])  # Number of words to replace

    for i in range(num_replace):
        while 1:
            rand_index = random.randint(0, len(words)-1)
            if words[rand_index] != '...':
                words[rand_index] = '...'
                break

    return ' '.join(words)

def deaf(message, stacks):
    return blind(message, stacks)
