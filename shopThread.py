import threading
import Queue
import engine_classes
import Q2logging



class shopthread(threading.Thread):
    def __init__(self, player, cmd_queue, engine):
        threading.Thread.__init__(self)
        self.inventory = {"flat pack furniture":10, "mutagen":20} #Item and cost in likes.
        self.cmd_queue = cmd_queue
        self.msg_queue = engine._MessageQueue
        self.name = player.name
        self.logger = Q2logging.out_file_instance('logs/shops/'+player.name)
        self.engine = engine
        
    
    def run(self):
        entry_msg = "Welcome to my store!\r\nI have the following items available for purchase: \r\n"
        for item in self.inventory.keys(): 
            entry_msg = entry_msg + "\t"+item+" for: "+ str(self.inventory[item])+" likes"+"\r\n"
            
        entry_msg = entry_msg + "To buy an item, type 'buy -itemname-', or type 'done' to exit\r\n"
        self.send_output(entry_msg)
        while 1:
            response = self.get_input()
            resp = response.split() #Get user response as list of words
            item = ''
            for i in range(1, len(resp)):
                item += resp[i]+' '
                
            item = item.strip()
            if resp[0] == 'buy':
                self.do_sell(item) #Sell them the item.

            elif resp[0] == 'done':
                break
                #End getting responses
            else:
                #That was not an accepted command, ignore.
                self.send_output("Sorry, I do not recognize the command '%s', try 'buy -item-' or 'done' to leave" % response)
                
                
        leave_msg = "Thank you, please come again!"
        self.send_output(leave_msg)
        self.engine._CommandQueue.put((self.name, 'done_shopping', []))
        self.logger.write_line("Command sent to the game queue to exit shop")
        
        
    def do_sell(self, item): #For when we sell them things.
        self.engine._Characters_In_Shop_Lock.acquire() 
        player_money = self.engine._Characters_In_Shop[self.name].items.get('like', 0) #The quantity of likes they currently have.  Returns 0 if none.
        if item in self.inventory: #This is something they can buy from us
            if self.inventory[item] > player_money: #If they do not have enough money, tell them such.
                self.send_output("Sorry, you do not have enough likes to buy %s" % item)
            else: #They have at least as much as they need if not more.
                self.engine._Characters_In_Shop[self.name].items[item] = self.engine._Characters_In_Shop[self.name].items.get(item, 0) + 1 #If item is in inventory, increment count, else add with count 1
                self.engine._Characters_In_Shop[self.name].items['like'] -= self.inventory[item]
                if self.engine._Characters_In_Shop[self.name].items['like'] == 0: #There are no more likes
                    del self.engine._Characters_In_Shop[self.name].items['like'] #So we delete likes from the inventory.
                self.send_output("You purchased %s" % item)
        else: #This is not something they can buy from us?
            self.send_output("Sorry, I do not have any %s" % item)
            
        self.engine._Characters_In_Shop_Lock.release()
        

    def get_input(self):
        response = self.cmd_queue.get()
        self.logger.write_line('Got command from %s: %s' % (self.name, response))
        return response
        
    def send_output(self, message):
        ret_tuple = (self.name, message, [])
        self.msg_queue.put(ret_tuple)
        self.logger.write_line("Sending message to %s:  %s" % (self.name, message))