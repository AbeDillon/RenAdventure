import threading
import Queue
import engine_classes
import Q2logging


class shopthread(threading.Thread):
    def __init__(self, player, cmd_queue, engine, inventory):
        threading.Thread.__init__(self)
        self.inventory = {} #Item and cost in likes.
        for item in inventory:
            self.inventory[item] = inventory[item]
        self.cmd_queue = cmd_queue
        self.msg_queue = engine._MessageQueue
        self.name = player.name
        self.logger = Q2logging.out_file_instance('logs/shops/'+player.name)
        self.engine = engine
        
    
    def run(self):
        entry_msg = "Welcome to my store!\r\nI have the following items available for purchase: \r\n"
        for item in self.inventory.keys(): 
            entry_msg = entry_msg + "\t"+item+" for: "+ str(self.inventory[item])+" likes"+"\r\n"
            
        entry_msg = entry_msg + "To buy an item, type 'buy -itemname-', 'sell -itemname-', or type 'done' to exit\r\n"
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
                
            elif resp[0] == 'sell':
                self.do_buy(item) #Buy the item from them.

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
        
    def do_buy(self, item): #For when we buy back items from them
        if item in self.inventory: #We sell it, so we will buy it.
            self.engine._Characters_In_Shop_Lock.acquire()
            if item in self.engine._Characters_In_Shop[self.name].items: #The player has this item in their inventory, so they can sell it to us.
                self.send_output("How many %s would you like to sell?" % item)
                self.engine._Characters_In_Shop_Lock.release()
                while 1:
                    qty = self.get_input()
                    if qty != '': #Non empty string
                        break
                try:
                    qty = int(qty)
                    if qty > self.engine._Characters_In_Shop[self.name].items[item]: # They are trying to sell more than they have, only accept what they have.
                        qty = self.engine._Characters_In_Shop[self.name].items[item]
                except:
                    qty = 0 #If we can't make a number out of it, don't buy it.
                self.engine._Characters_In_Shop_Lock.acquire()
                self.engine._Characters_In_Shop[self.name].items[item] = self.engine._Characters_In_Shop[self.name].items[item] - qty
                if self.engine._Characters_In_Shop[self.name].items[item] == 0: #We took all of this item from them, delete it?
                    del self.engine._Characters_In_Shop[self.name].items[item]
                if item == 'mutagen': #Give them 20 likes * qty
                    self.engine._Characters_In_Shop[self.name].items['like'] = self.engine._Characters_In_Shop[self.name].items.get('like', 0) + (20*qty)
                    self.send_output("You sold %d mutagen, and in return you received %d likes" % (qty, (qty*20)))
                elif item == 'flat pack furniture': #Give them 10 likes * qty
                    self.engine._Characters_In_Shop[self.name].items['like'] = self.engine._Characters_In_Shop[self.name].items.get('like', 0)+ (10*qty)
                    self.send_output("You sold %d flat pack furniture, and in return you received %d likes" % (qty, qty*10))
                self.engine._Characters_In_Shop_Lock.release()
                    
            else: #Item not in character items, they can't sell it
                self.engine._Characters_In_Shop_Lock.release()
                self.send_output("You do not have any %s to sell." % item)
        else:
            self.send_output("Sorry, I do not buy %s" % item)

    def get_input(self):
        response = self.cmd_queue.get()
        self.logger.write_line('Got command from %s: %s' % (self.name, response))
        return response
        
    def send_output(self, message):
        ret_tuple = (self.name, message, [])
        self.msg_queue.put(ret_tuple)
        self.logger.write_line("Sending message to %s:  %s" % (self.name, message))