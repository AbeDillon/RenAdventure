import winsound, sys

def play_sound(sound):
    filepath = 'c:/Python27/Sounds/%s.wav' % sound
    winsound.PlaySound(filepath, winsound.SND_FILENAME)
    return True
    
if __name__ == '__main__':
    while 1:
        ans = raw_input('Please enter the name of the sound, or type "done":\r\n')
        if ans == 'done':
            break
        else:
            try:
                play_sound(ans.upper())
            except:
                print 'ERROR PLAYING SOUND FILE'
    raw_input('Program finished, hit enter to exit.')