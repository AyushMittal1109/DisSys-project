import os
import time

# available nodes
alive_nodes = set()

# new process id always increasing
new_node_id = 0

# node and their addresses
node_address = {}

# input for new node
def new_node_initializer():
    STOP = False
    while STOP == False:
        print("1 - initlise node | 2 - show database | 3 - stop bootstraper")
        i = int(input())
        
        if i == 1:
            ip = input("ip : ")
            port = input("port : ")
            print("i = 1 tested")
        elif i == 2:
            print("i = 2 tested")
            # show whole graph 
            pass
        elif i == 3:
            s = input("Sure?\nenter Y/y to exit(stop), else press any other key : ")
            if s == 'y' or s == 'Y':
                STOP = True
        else:
            print("invalid input")

        time.sleep(1)
        os.system('clear')


new_node_initializer()
    