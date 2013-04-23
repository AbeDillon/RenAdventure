import threading
import Queue
import engine_classes
import Q2logging



class shopthread(threading.thread):
    def __init__(self, inventory, player, cmd_queue, engine):
        self.inventory = {}
        self.cmd_queue = cmd_queue
        
        for item in inventory:
            self.inventory[item] = inventory[item] #Transfer item and cost.
            
        self.msg_queue = engine._MessageQueue
        self.name = player
        self.logger = Q2logging.out_file_instance('logs/shops/'+player)
        self.engine = engine
        
    
    def run(self):
        entry_msg = "Welcome to my store!\r\nI have the following items available for purchase: \r\n"
        for item in self.inventory.keys(): 
            entry_msg = entry_msg + "\t"+item+" for: "+ str(self.inventory[item])+" likes"+"\r\n"
            
        send_output(entry_msg)
        while 1:
            response = get_input()
            resp = response.split() #Get user response as list of words
            item = ''
            for i in range(1, len(resp)):
                item += resp[i]+' '
                
            item = item.strip()
            if resp[0] == 'buy':
                do_sell(item) #Sell them the item.

            elif resp[0] == 'done':
                break
                #End getting responses
            else:
                #That was not an accepted command, ignore.
                send_output("Sorry, I do not recognize the command '%s'" % response)
                
                
        leave_msg = "Thank you, please come again!"
        send_output(leave_msg)
        
        
    def do_sell(self, item): #For when we sell them things.
        self.engine._Characters_Lock.acquire() 
        player_money = self.engine._Characters[self.name].items.get('likes', 0) #The quantity of monies they currently have. "money_name" is placeholder for actual currency name. Returns 0 if none.
        if item in self.inventory: #This is something they can buy from us
            if self.inventory[item] > player_money: #If they do not have enough money, tell them such.
                send_output("Sorry, you do not have enough likes to buy %s" % item)
            else: #They have at least as much as they nead if not more.
                self.engine._Characters[self.name].items[item] = self.engine._Characters[self.name].items.get(item, 0) + 1 #If item is in inventory, increment count, else add with count 1
                self.engine._Characters[self.name].items['likes'] -= self.inventory[item]
                send_output("You purchased %s" % item)
        else: #This is not something they can buy from us?
            send_output("Sorry, I do not have any %s" % item)
            
        self.engine._Characters_Lock.release()
        

    def get_input(self):
        response = self.cmd_queue.get()
        cmd = response[1] #Get the message portion
        self.logger.write_line('Got command from %s: %s' % (self.name, cmd))
        return cmd
        
    def send_output(self, message):
        ret_tuple = (self.name, message, [])
        self.msg_queue.put(ret_tuple)
        self.logger.write_line("Sending message to %s:  %s" % (self.name, msg))
    