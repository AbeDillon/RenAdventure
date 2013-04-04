#!/usr/bin/env python
import sys
import time
import datetime

class out_file_instance(object):
    def __init__(self, file_name):
        self.field_separator = ''
        self.current_day = self.get_current_day()
        self.file_name = file_name
        self.open_target_file(self.file_name)
        self.current_debug_level = 0

    def open_target_file(self, file_name):
        #file_name = file_name+'.'+self.current_day+'.log'
        #self.handle = open(file_name, 'a')
        try:
            file_name = file_name + '.' + self.current_day + '.log'
            self.handle = open(file_name, 'a')
        except IOError:
            print "Could not open", file_name, ", exiting..."; sys.exit(-1)
    
    def write_line(self, data, debug_level = 0):         # this is now a wrapper for the actual writing to check the 
        # check for new day
        self.is_new_day()
        self.perform_write(data, debug_level)
    
    def perform_write(self, data, debug_level):
        if debug_level <= self.current_debug_level:
            new_row = [str(x) for x in data]
            #self.handle.write(time.strftime('%m/%d/%Y %H:%M:%S')+' '+self.field_separator.join(new_row)+'\n')
            self.stamp = datetime.datetime.now()
            self.handle.write(self.stamp.strftime('%m/%d/%Y %H:%M:%S')+'.'+str(self.stamp.microsecond)[:-3]+'   '+self.field_separator.join(new_row)+'\n')
            # flush here - is this a bad idea?
            self.handle.flush()

    def set_current_debug_level(self, new_debug_level):
        self.current_debug_level = new_debug_level
        self.write_line(['Debug Level Changed to', new_debug_level])
        
    def get_current_day(self):              # fetch the current day mm-dd-yyyy (this is ugly)
        return time.strftime('%m-%d-%Y')

    def shutdown(self):
        self.handle.close()
        
    def is_new_day(self):                   # determine if this is a new day and cycle the log if it is...
        if time.strftime('%m-%d-%Y') == self.current_day:
            return
        else:
            # update self.current_day
            self.current_day = self.get_current_day()
            self.handle.close()
            self.open_target_file(self.file_name)





