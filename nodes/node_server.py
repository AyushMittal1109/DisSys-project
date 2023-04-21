import node_start

from flask import Flask, redirect, url_for, request
import requests
from _thread import *
import threading
import random
import socket
import pickle
import time
import json
import sys 
import socket, errno
from threading import Lock
from colored import fg
# import logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# global f
f=None
pp = 8000
port1 = str(pp)
port2 = str(pp+1)
port3 = str(pp+2)
port4 = str(pp+3)

color = fg('white')

# logging.basicConfig(filename="log.txt")
# logging.info("Ayush")
# sess = requests.Session()

# Unhadled case is  Node goes down and then comes back
# for all global variable add locks

app = Flask(__name__)

'''
   Keeping some global data here
'''

'''
    Executing_CS tells whether you are Executing CS 
'''

# node and their addresses
alive_node_address = {}
responsibility_of = []

# for containg nodes failed in one iteration
failed_nodes = set()

# for new nodes, to add them in next iteration
new_responsibility = set()

# got permission from set
got_permission_from = set()

global my_ip
global my_port
global my_process_id
global finished
finished = False

my_process_id = 11


global Executing_CS 
Executing_CS=0
Executing_CS_lock = Lock() # create a lock
def get_Executing_CS():
    # lock
    Executing_CS_lock.acquire()
    global Executing_CS
    temp=Executing_CS
    Executing_CS_lock.release()
    #unlock
    return temp

def set_Executing_CS(input):
    # lock
    Executing_CS_lock.acquire()
    global Executing_CS
    Executing_CS=input
    Executing_CS_lock.release()
    #unlock

'''
    Requesting_CS tells whether you are Requesting CS 
'''
global Requesting_CS 
Requesting_CS=0
Requesting_CS_lock = Lock() # create a lock
def get_Requesting_CS():
    # lock
    Requesting_CS_lock.acquire()
    global Requesting_CS
    temp=Requesting_CS
    Requesting_CS_lock.release()
    #unlock
    return temp

def set_Requesting_CS(input):
    # lock
    Requesting_CS_lock.acquire()
    global Requesting_CS
    Requesting_CS=input
    Requesting_CS_lock.release()
    #unlock




'''
    my_local_clock tells my event count 
'''
global my_local_clock
my_local_clock=0
my_local_clock_lock = Lock() # create a lock for it
def get_my_local_clock():
    #lock
    my_local_clock_lock.acquire()
    global my_local_clock
    temp=my_local_clock
    #unlock
    my_local_clock_lock.release()
    return temp

def update_my_local_clock():
    #lock
    my_local_clock_lock.acquire()
    global my_local_clock
    my_local_clock=my_local_clock+1
    my_local_clock_lock.release()
    #unlock

'''
    can_enter_CS tells whwther you can enter CS or not (i.e. waiting_for_reply_from list is empty [you are waiting for no alive process to get reply message])
'''
global can_enter_CS  #can be updated by 2 threads RW dependency, add lock. and add setter getter function
can_enter_CS=0
can_enter_CS_lock = Lock() # create a lock for it
def get_can_enter_CS():
    # lock
    can_enter_CS_lock.acquire()
    global can_enter_CS
    temp=can_enter_CS
    can_enter_CS_lock.release()
    #unlock
    return temp

def set_can_enter_CS(input):
    # lock
    can_enter_CS_lock.acquire()
    global can_enter_CS
    can_enter_CS=input
    can_enter_CS_lock.release()
    #unlock



'''
    tells to whom you have not sent any reply (you will use it after your CS is done and send reply to those, whom you have not sent reply previously)
    reply_defered_to tells to whom i have deferred reply to (which process is waiting for my reply)
    it contains a list with following elements
        [
            requesting_process_ip,
            requesting_process_port,
            requesting_process_id,
            requesting_process_event_count
        ]

'''

reply_defered_to=[]
reply_defered_to_lock = Lock() # create a lock for it
def get_reply_defered_to():
    # lock
    reply_defered_to_lock.acquire()
    global reply_defered_to
    temp=reply_defered_to
    reply_defered_to_lock.release()
    #unlock
    return temp

def append_reply_defered_to(input):
    # lock
    reply_defered_to_lock.acquire()
    global reply_defered_to
    reply_defered_to.append(input)
    reply_defered_to_lock.release()
    #unlock

def remove_reply_defered_to(input):
    # lock
    reply_defered_to_lock.acquire()
    # status=False
    global reply_defered_to
    ele_to_delete=[]
    for x in reply_defered_to:
        if x[0]==input[0] and x[1]==input[1]:
            ele_to_delete.append(x)
    for y in ele_to_delete:
        reply_defered_to.remove(y)
        # reply_defered_to.erase(y)
    # if input in reply_defered_to:
    #     reply_defered_to.remove(input)
    #     status=True
    # else:
    #  1+1
    # print(color, "Function: 'remove_reply_defered_to'")
    #  1+1
    # print(color, "Want to delete:",input)
    #  1+1
    # print(color, "But I contain:",reply_defered_to)
    reply_defered_to_lock.release()
    #unlock
    # return status

def erase_reply_defered_to():
    # lock
    reply_defered_to_lock.acquire()
    global reply_defered_to
    reply_defered_to=[]
    reply_defered_to_lock.release()
    #unlock


'''
    'request_sent_to' tells to which process you have sent request (used to handle addition of new node)
    it contains a list with following elements
        [
            Dest_process_ip, #To whom I have sent request
            Dest_process_port, #To whom I have sent request
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
    will be needed when a new node is added, so that you don't send a request to it again, a node will recieve request only if it is not 
    in this list i.e. it is new node. 
    Ex: request_sent_to.append([Dest_process_ip,Dest_process_port,My_process_id,My_process_event_count])
    
# alive_process['host']==requested_process[0] and alive_process['port']==requested_process[1] and my_process_id==requested_process[3]:
'''
# continue from here
request_sent_to=[] #tells to which process you have sent request (used to handle addition of new node)
request_sent_to_lock = Lock() # create a lock for it

def get_request_sent_to():
    # lock
    request_sent_to_lock.acquire()
    global request_sent_to
    temp=request_sent_to
    request_sent_to_lock.release()
    #unlock
    return temp

def append_request_sent_to(input):
    # lock
    request_sent_to_lock.acquire()
    global request_sent_to
    request_sent_to.append(input)
    request_sent_to_lock.release()
    #unlock

def remove_request_sent_to(input):
    # lock
    request_sent_to_lock.acquire()
    status=False
    global request_sent_to
    ele_to_delete=[]
    for x in request_sent_to:
        if x[0]==input[0] and x[1]==input[1]:
            ele_to_delete.append(x)
    for y in ele_to_delete:
        # request_sent_to.erase(y)
        request_sent_to.remove(y)
    # if input in request_sent_to:
    #     request_sent_to.remove(input)
    #     status=True
    # else:
    #  1+1
    # print(color, "Function: 'remove_request_sent_to'")
    #  1+1
    # print(color, "Want to delete:",input)
    #  1+1
    # print(color, "But I contain:",request_sent_to)
    request_sent_to_lock.release()
    #unlock
    return status



'''
    tells to which process you have sent request but have not recieved reply yet.

        [
            Dest_process_ip, #On whom I am waiting/who has not sent me reply
            Dest_process_port, #On whom I am waiting/who has not sent me reply
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
    Has 4 info his IP, his Port, my process id and my event count
    so when reply comes (if it does) get replying proess's IP and port and get your process id and event count and get these info to remove it from list
    waiting_for_reply_from.append([Dest_process_ip,Dest_process_port,My_process_id,My_process_event_count])#
'''
waiting_for_reply_from=[] # 
waiting_for_reply_from_lock = Lock() # create a lock for it


def get_waiting_for_reply_from():
    # lock
    waiting_for_reply_from_lock.acquire()
    global waiting_for_reply_from
    temp=waiting_for_reply_from
    waiting_for_reply_from_lock.release()
    #unlock
    return temp

def append_waiting_for_reply_from(input):
    # lock
    waiting_for_reply_from_lock.acquire()
    global waiting_for_reply_from
    waiting_for_reply_from.append(input)
    waiting_for_reply_from_lock.release()
    #unlock

def remove_waiting_for_reply_from(input):
    # lock
    waiting_for_reply_from_lock.acquire()
    status=False
    global waiting_for_reply_from
    ele_to_delete=[]
    for x in waiting_for_reply_from:
        if x[0]==input[0] and x[1]==input[1]:
            ele_to_delete.append(x)
            status=True
    for y in ele_to_delete:
        waiting_for_reply_from.remove(y)

        # waiting_for_reply_from.erase(y)
    # if input in waiting_for_reply_from:
    #     waiting_for_reply_from.remove(input)
    #     status=True
    # else:
    #  1+1
    # print(color, "Function: 'remove_waiting_for_reply_from'")
    #  1+1
    # print(color, "Want to delete:",input)
    #  1+1
    # print(color, "But I contain:",waiting_for_reply_from)
    waiting_for_reply_from_lock.release()
    #unlock
    return status


##########################################################################################

def enter_CS():
    '''
        Your CS task here
    '''
    f=open('logs.txt','a')
    f.write("["+str(my_process_id)+","+str(get_my_local_clock())+","+str(get_Requesting_CS())+","+str(get_Executing_CS())+"] :entering CS"+str(get_my_local_clock())+'\n')
    f.close()

    set_Executing_CS(1)
    global color
    color = fg('green')
    
    print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :entering CS",get_my_local_clock())
    # randomtime=random.randint(0,3)
    # time.sleep(randomtime)
    time.sleep(10)
    
    print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :exiting CS",get_my_local_clock())
    # f.write("[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :exiting CS",get_my_local_clock())
    f=open('logs.txt','a')
    f.write("["+str(my_process_id)+","+str(get_my_local_clock())+","+str(get_Requesting_CS())+","+str(get_Executing_CS())+"] :exiting CS"+str(get_my_local_clock())+'\n')
    color = fg('white')
    set_Executing_CS(0)
    f.close()
     #will it give deadlock
    # set_can_enter_CS(0)

def can_send_reply(his_local_event,his_process_id):
    '''
        Check Ricard Agarwala Condition,
        Return True if you agree to send Reply message to Requesting Process 
        Else Return False

        Executing_CS=1
            Defer Reply
        Executing_CS=0
            Requesting_CS=0
                Send Reply
            Requesting_CS=1
                (my_priority < his_priority) ((my_local_clock > his_local_event) or ((my_local_clock == his_local_event) and (my_process_id > his_process_id)))
                    Send Reply
                else 
                    Defer Reply
    '''
    if get_Executing_CS()==1: 
        '''I won't send reply if i am in CS'''
        return False
    if get_Requesting_CS()==0: 
        '''I will send reply since i am not interested in CS(as of now)'''
        return True
    '''
        I am here means I am requesting CS and not in CS
    '''
    My_event_count=get_my_local_clock()
    
    if (My_event_count > his_local_event) or ((My_event_count == his_local_event) and (my_process_id > his_process_id)):
        '''
            My priority is less so send Reply
        '''
        return True
    return False
    

@app.route('/RecieveRequest', methods=['POST', 'GET'])
def handle_recieved_Request():
    '''
        I recieve request from other processes.
    '''
    data = request.get_json()
    requesting_process_ip=data["requesting_process_ip"]
    requesting_process_id=data["requesting_process_id"]
    requesting_process_port=data["requesting_process_port"]
    requesting_process_event_count=data["requesting_process_event_count"]
    
    print(color, "Recieved Request from :",requesting_process_ip ,requesting_process_port)
    
    # global request_recieved_from# use later don't let a process who got a reply get a reply again

    Ricard_status=can_send_reply(requesting_process_event_count,requesting_process_id)

    # TODO
    if requesting_process_id in got_permission_from:
        Ricard_status = False

    if Ricard_status==True:
        print(color, "reply send to", requesting_process_ip ,requesting_process_port)
        return "Continue Execution"
    
    else:
        print(color, "deferred send to", requesting_process_ip ,requesting_process_port)
        temp=[requesting_process_ip,requesting_process_port,requesting_process_id,requesting_process_event_count]
        append_reply_defered_to(temp)
        '''
            you must append following DS
            [
            requesting_process_ip,
            requesting_process_port,
            requesting_process_id,
            requesting_process_event_count
        ]
        '''
        return "Reply Deffered" #abhi mai ack bhej rha hu, baad me timout se handle krna hai (bhejna to padega , flask ki dikkat hai)



def send_request(Dest_id, Dest_ip,Dest_port,my_clock):
    '''
        send request to process with corresponding IP and Port,when requesting for CS
    '''
    Dest_Process = "http://"+Dest_ip+":"+str(Dest_port)+"/" #extra / needed? may cause error
    send_info = {
        "requesting_process_id": my_process_id,
        "requesting_process_ip": my_ip,
        "requesting_process_port": my_port,
        "requesting_process_event_count": my_clock
    }

    response_holder = "Ayush"
    try:
        response_holder = requests.post(Dest_Process + "RecieveRequest", json=send_info).content.decode('ascii')
    except:
        # TODO
        1+1
    '''Sending Request at the /RecieveRequest api of Destn and recieved response(may not be reply) in response_holder
    '''
    Dest_process_ip=Dest_ip
    Dest_process_port=Dest_port
    My_process_id=my_process_id
    My_process_event_count=my_clock
    temp=[Dest_process_ip,Dest_process_port,My_process_id,My_process_event_count]
    append_request_sent_to(temp)
    append_waiting_for_reply_from(temp)

    '''
        temp must have following DS
        [
            Dest_process_ip, #To whom I have sent request
            Dest_process_port, #To whom I have sent request
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
        
    '''
    # 
    # print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :Request sent to IP:",Dest_ip,"and Port:",Dest_port)
    if response_holder=="Continue Execution":
        '''Request send to the process and recieved reply as well.'''
        # TODO
        got_permission_from.add(Dest_id)
        # pass
        
        print(color, "Received:Continue Execution from",Dest_process_ip,Dest_process_port)
        remove_waiting_for_reply_from(temp)
        # 
        # print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :Recieved Reply from IP:",Dest_ip,"and Port:",Dest_port)
    elif response_holder=="Reply Deferred": 
        '''
            you don't send this ack in ricart agarwala, if you don't get reply it means other process is either not willing to let you enter CS
            or the other process is not alive, so handle this with timeout
        '''
        
        print(color, "Received:Reply Deferred from",Dest_process_ip,Dest_process_port)

        # 
        # print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :Reply Deffered from IP:",Dest_ip,"and Port:",Dest_port)
        temp2=[Dest_process_ip,Dest_process_port,My_process_id,My_process_event_count]
        # append_waiting_for_reply_from(temp2)
        '''
            temp2 must have DS
            [
            Dest_process_ip, #On whom I am waiting/who has not sent me reply
            Dest_process_port, #On whom I am waiting/who has not sent me reply
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
        '''
    # else:
        
        # print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :Error Occured in sending request or (Recieved Neither 'Continue Execution' nor 'Reply Deffered')")


def get_alive_process_info():
    '''
        Dummy data of Alive process (Replace with function which finds currently alived processes)
    '''
    processes = []
    for node_id in alive_node_address.keys():
        processes.append({"process_id": node_id, "host": alive_node_address[node_id]['ip'], "port": alive_node_address[node_id]['port']})
    
    # processes = [
        # { "process_id": "1", "host": "127.0.0.1", "port": port1},
    #     { "process_id": "2", "host": "127.0.0.1", "port": port2},
    #     { "process_id": "3", "host": "127.0.0.1", "port": port3},
    #     { "process_id": "4", "host": "127.0.0.1", "port": port4}
    # ]
    return processes

def handle_nodes_failue(alive_processes):
    '''
        Gets list of Alive processes and then looks for that process information upon whom it is waiting for reply
        if that process upon whom this process is not alive, then Remove it from 'waiting_for_reply_from' array
        i.e. iterate over the processes upon whom you are waitng and check if it is in list of alive processes

        Note: (Untested hypotesis) if ypu also remove that process info from 'request_sent_to' it will handle 
        node coming back online as a new node after failure.
    '''
    # global waiting_for_reply_from
    Process_down_list=[]
    I_am_waiting_on=get_waiting_for_reply_from()
    '''
        DS of I_am_waiting_on
        [
            Dest_process_ip, #On whom I am waiting/who has not sent me reply
            Dest_process_port, #On whom I am waiting/who has not sent me reply
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
    '''
    for process in I_am_waiting_on:
        found=False
        # WHY??????
        for alive_process in alive_processes:
            if alive_process['host']==process[0] and alive_process['port']==process[1] and my_process_id==process[2]:
                '''
                    his IP matched with one of alive process ip
                    his port matched with one of alive process port
                    # my process id matched to 
                    # port matched
                    # my clock
                '''
                found=True #process is alive
                break
        if found==False: #process upon whom i am waiting is not in alive list means it is deleted.
            Process_down_list.append(process)
            # waiting_for_reply_from.remove(process)
            # if process in request_sent_to:
            #     request_sent_to.remove(process)
        else:
            
            # print(color, "process is alive and i am waiting on it so no need to remmove from 'waiting_for_reply_from' and 'request_sent_to' list")
            # pass #add 1+1
            # #print color, stmt
            pass
    for process in Process_down_list:
        remove_waiting_for_reply_from(process)
        '''
            process must have DS
            [
            Dest_process_ip, #On whom I am waiting/who has not sent me reply
            Dest_process_port, #On whom I am waiting/who has not sent me reply
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
        
        '''
        # waiting_for_reply_from.remove(process)
        remove_request_sent_to(process)
        '''
        Process must have DS as follows
            [
            Dest_process_ip, #To whom I have sent request
            Dest_process_port, #To whom I have sent request
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
        '''
        #since the process is down you will behave as if you never sent him request 
        #(so that when it comes up you will send a fresh request to it)

def handle_nodes_addition(alive_processes):
    '''
        Iterate over alive process list and check if you have sent request to that process or not, if you have not 
        sent request to a process then it means that process is new, so send request to this process.  add the case where
        there is a new process in alive_processes and you have not sent request to that process earlier, it means you have to send 
        request to it process as well as this is a new node in the system
    '''
    already_requested_processes=get_request_sent_to()
    '''
        already_requested_processes gets following ds
        [
            Dest_process_ip, #To whom I have sent request
            Dest_process_port, #To whom I have sent request
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
    '''

    to_add = []
    for alive_process in alive_processes:
        # iterate over the processes upon whom you are waitng and check if it is in list of alive processes
        found=False
        for requested_process in already_requested_processes:
            if alive_process['host']==requested_process[0] and alive_process['port']==requested_process[1] and my_process_id==requested_process[2]:#it was 3 earlier
                found=True # you have already sent request to this (alive)process, it is not new process
                break
            '''else:
                Dest_ip=alive_process['host']
                Dest_port=alive_process['port']
                my_clock=get_my_local_clock()
                if Dest_ip==my_ip and Dest_port==my_port:
                    continue #don't send request to self
                else:
                    send_request(Dest_id,Dest_ip,Dest_port,my_clock)
                    
                    print(color, "i have not sent request to this process so have to send now")'''
        if found==False: # you have not sent request to this (alive)process, it is new process so send request to this process
            Dest_ip=alive_process['host']
            Dest_port=alive_process['port']
            Dest_id=alive_process['process_id']
            my_clock=get_my_local_clock()
            if Dest_ip==my_ip and Dest_port==my_port:
                continue #don't send request to self
            else:
                # 
                # print(color, "mene esko request ab beji he, request id bhi")
                # 
                # print(color, f"sending to {Dest_port} ------------- ----------===============")
                send_request(Dest_id,Dest_ip,Dest_port,my_clock)
                process = [Dest_ip,Dest_port,my_process_id,my_clock]
                to_add.append(process)
                
                # print(color, process)
                # process = [Dest_ip,Dest_port,alive_process['process_id'],my_clock]
    for process in to_add:
        append_request_sent_to(process)

def update_node_alive_list():
    '''
        Function to check if the process upon which i am waiting for reply is alive or not
        remove that process(from request_sent_to) whose information is in request_sent_to but is not in alive_processes

        also handles the case of node addtion
    '''
    alive_processes = get_alive_process_info()
    handle_nodes_failue(alive_processes)
    handle_nodes_addition(alive_processes)


def check_recieved_reply_from_everyone():
    '''
        Check if I have recieved reply from all the alive process whom I sent request or not
    '''
    # set_can_enter_CS(0) 
    #initialiseing the flas as 0, meaning you cannot enter, 
    #first you have to check then only you can enter
    if len(get_waiting_for_reply_from())==0:
        set_can_enter_CS(1)
        set_Executing_CS(1)
        return
    while get_can_enter_CS()==0:
        
        print(color, "Stuck here",get_waiting_for_reply_from())
        time.sleep(1)
        update_node_alive_list()
        if len(get_waiting_for_reply_from())==0:
            ''' it is a list of list'''
            set_can_enter_CS(1)
            break
        else:
            set_can_enter_CS(0)
    #Optimise above apporach(replace with no Busy wait/ Spin Lock free Appraoch)

@app.route('/RecieveReply', methods=['POST', 'GET'])
def handle_recieved_Rfeply():
    '''
        Api Exposed so that i can recieve Reply from Others
    '''
    data = request.get_json()
    reply_from_ip=data["replying_ip"]
    reply_from_process_id=data["replying_process_id"] # not needed
    reply_from_port=data["replying_port"]
    reply_from_event_count=data["replying_process_event_count"] # not needed
    reply_message=data["message"]
    if reply_message=="I am done with my CS, you have my permission":

        # TODO
        got_permission_from.add(reply_from_process_id)
        # my_
        global my_process_id
        My_process_id=my_process_id
        My_process_event_count=get_my_local_clock()
        temp=[reply_from_ip,reply_from_port,My_process_id,My_process_event_count]
        '''
            temp must have DS
            [
            Dest_process_ip, #On whom I am waiting/who has not sent me reply
            Dest_process_port, #On whom I am waiting/who has not sent me reply
            My_process_id, #What Info about me I have sent him
            My_process_event_count #What Info about me I have sent him
        ]
        '''
        
        
        #1        # #print(color, get_waiting_for_reply_from())
        # print(color, data)
        
        # print(color, "He is done with my CS, I have my permission from: ",reply_from_ip,reply_from_port)
        if remove_waiting_for_reply_from(temp)==False:
            
            print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :eeerror",temp,get_waiting_for_reply_from())
        else:
            print("Received reply from",reply_from_ip,reply_from_port)
            # print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :No longer waiting on:",reply_from_ip,reply_from_port)
        # 
        # print(color, get_waiting_for_reply_from())
        
        # print(color, )
        # pass
        if len(get_waiting_for_reply_from())==0:#new
            set_Executing_CS(1)
    return "OK! I recieved your ack"


def post_CS_send_reply():
    '''
        You are done with you CS, so you send reply to everyone who requested Permission for CS access from you
    '''
    # pass
    to_be_deleted=[]
    whose_reply_i_have_deferred=get_reply_defered_to()
    '''
        whose_reply_i_have_deferred has 
        [
            requesting_process_ip,
            requesting_process_port,
            requesting_process_id,
            requesting_process_event_count
        ]
    '''
    
    print(color, "\nwhose_reply_i_have_deferred:",whose_reply_i_have_deferred,"\n")
    # [requesting_process_id,requesting_process_ip,requesting_process_port,requesting_process_event_count]
    for process in whose_reply_i_have_deferred:
        his_ip=process[0]
        his_port=process[1]
        # his_proceess_id=process[2]
        # his_event_count=process[3]
        my_clock=get_my_local_clock()
        send_info = {
            "replying_ip": my_ip,
            "replying_port": my_port,
            "replying_process_id": my_process_id, #he won't need it
            "replying_process_event_count": my_clock, #he won't need it
            "message":"I am done with my CS, you have my permission"
        }
        Dest_Process = "http://"+his_ip+":"+his_port+"/"
        '''
            Send Reply to his Exposed API "/RecieveReply"
        '''
        
        # print(color, "sending deffered reply to:",Dest_Process)
        try:
            response_holder = requests.post(Dest_Process + "RecieveReply", json=send_info).content.decode('ascii')
        
            # if response_holder =="OK! I recieved your ack":
            #     to_be_deleted.append(process)
            #     # remove_reply_defered_to(process)
            #     '''
            #         You must remove 
            #         [
            #             requesting_process_ip,
            #             requesting_process_port,
            #             requesting_process_id,
            #             requesting_process_event_count
            #         ]
            #     '''
            #     # reply_defered_to.remove(process)
            #     # continue
            # else:
                
            #     print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :Error Occured")
            #     break
        except:
            # TODO
            1+1
    got_permission_from.clear()
    erase_reply_defered_to()#I have sent reply to all so clear this
    # reply_defered_to=[]#I have sent reply to all so clear this


def CS():
    '''
        CS Part of the code
    '''
    update_my_local_clock()
    processes=get_alive_process_info()
    # 
    # print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] : I got list of alive Processes as Follows :=> ",processes)
    # 
    # print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] : I Want to Enter CS")
    set_Requesting_CS(1)
    '''
        Send request to everyone(except self)
    '''
    for process in processes: 
        if process["process_id"]==my_process_id:
            '''Don't sends request to self'''
            continue 
        else:
            
            print(color, process)
            send_request(process["process_id"], process['host'],process['port'],my_local_clock)
    # if len(get_waiting_for_reply_from())==0:#new
    #         set_Executing_CS(1)
            # 
            # print(color, my_process_id, "sending re to ",process['host'],process['port'],)
    '''Wait for Reply from everyone'''
    check_recieved_reply_from_everyone()
    '''Code to actually enter CS'''
    enter_CS()
    set_can_enter_CS(0)#can give deadlock
    set_Requesting_CS(0)
    '''send reply to all'''
    
    post_CS_send_reply()

    # 
    # print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"]")
   

def NonCS():
    '''
        Non Cs Part of the code
    '''
    set_Requesting_CS(0)
    set_Executing_CS(0)
    # update_my_local_clock()
    
    print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :entering NCS",get_my_local_clock())
    randomtime=random.randint(0,3)
    time.sleep(randomtime)
    set_Executing_CS(0)
    set_Requesting_CS(0)
    

def my_task_Process1():
    time.sleep(2) #sleep added to make sure by that time all 4 process's server become alive
    CS()
    NonCS()
    CS()
    CS()
    NonCS()
    CS()
    NonCS()
    CS()
    global finished
    finished = True

def my_task_Process2():
    time.sleep(2) #sleep added to make sure by that time all 4 process's server become alive
    CS()
    CS()
    NonCS()
    NonCS()
    CS()
    CS()
    CS()
    NonCS()
    NonCS()
    CS()
    NonCS()
    CS()
    global finished
    finished = True

def my_task_Process3():
    time.sleep(2) #sleep added to make sure by that time all 4 process's server become alive
    CS()
    NonCS()
    CS()
    CS()
    CS()
    NonCS()
    NonCS()
    CS()
    NonCS()
    CS()
    NonCS()
    CS()
    NonCS()
    CS()
    global finished
    finished = True

def my_task_Process4():
    time.sleep(2) #sleep added to make sure by that time all 4 process's server become alive
    CS()
    NonCS()
    NonCS()
    CS()
    CS()
    CS()
    NonCS()
    NonCS()
    CS()
    CS()
    NonCS()
    CS()
    NonCS()
    CS()
    global finished
    finished = True

def get_free_port(my_ip,my_port):
    '''
        Function checks if port is available or not, If not avialbale then tries to find a available port
    '''
    base_port=1024
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((my_ip, int(my_port)))
            
            print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :Port:",my_port,"is avaliable,using it.")
            s.close()
            return my_port 
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                
                print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :Port:",my_port,"is already in use",e)
            else:
                
                print(color, "[",my_process_id,",",get_my_local_clock(),",",get_Requesting_CS(),",",get_Executing_CS(),"] :Unknown Error",e) # something else raised the socket.error exception
            my_port=base_port+random.randint(0,4000)
        s.close()
    return my_port


@app.route('/takeResponsibility',methods = ['POST','GET'])
def takeResponsibility():
    
    # print(color, request.json)
    # return 'ok'
    new_node = request.json
    new_responsibility.add(new_node['id'])

    return 'ok'

@app.route('/newNode',methods = ['POST','GET'])
def newNode():
    data = request.json
    newNode_id = data['id']
    newNode_ip = data['ip']
    newNode_port = data['port']
    alive_node_address[newNode_id] = {
        'ip':newNode_ip,
        'port':newNode_port
    }
    
    print(color, 'new node added, and now all nodes are:', )
    
    print(color, alive_node_address)
    return 'ok'

@app.route('/healthCheck',methods = ['POST','GET'])
def healthCheck():
    return 'ok'

@app.route('/node_x_failed',methods = ['POST','GET'])
def node_x_failed():
    data = request.json
    id = data['node_id']

    print("node",id,"failed")
    try:
        # 
        # print(f"-------------------------------node {failed_node} deleted -------------------------")
        del alive_node_address[id]
        # use locking here TODO
    except:
        2+2

    return 'ok'
    

def tell_node_x_failed(target_ip, target_port, x):
    # node_x_ip = alive_node_address[tell_to]["ip"]
    # node_x_port = alive_node_address[tell_to]["port"]
    data = {
        "node_id":x
    }
    try:
        requests.post(f"http://{target_ip}:{target_port}/node_x_failed", json = data )
    except:
        # TODO
        1+1
    return


def check_node(x):
    # node_x_ip = 0
    # node_x_port = 0
    try:
        node_x_ip = alive_node_address[x]['ip']
        node_x_port = alive_node_address[x]['port'] 
    except:
        failed_nodes.add(x)
        print("node",x,"is deleted")
        return

    
    url = f'http://{node_x_ip}:{node_x_port}/healthCheck'

    try:
        res = requests.post(url)#, timeout = 5)
        if res.ok:
            return 
    except:
        # print(f"failed to contact {node_x_port} first time")
        pass
    time.sleep(2)
    try:
        res = requests.get(f'http://{node_x_ip}:{node_x_port}/healthCheck')#, timeout = 5)
        if res.ok:            
            return
    except:
        # print(f"failed to contact {node_x_port} second time")
        pass    
    
    print(f"\nnode {node_x_port} is failed")
    
    # node x is failed
    failed_nodes.add(x)
    # broadcast to all(including bootstraper) that node is failed
    threads = []
    for node_id in list(alive_node_address.keys()):
        if node_id == my_process_id or node_id == x: 
            continue
        t = threading.Thread(target=tell_node_x_failed, args = (alive_node_address[node_id]["ip"],alive_node_address[node_id]["port"], x))
        threads.append(t)
        t.start()
    
    t = threading.Thread(target=tell_node_x_failed, args = (sys.argv[3],sys.argv[4], x))
    threads.append(t)
    t.start()

    for t in threads:
        t.join()

def start_health_check():

    while finished==False:
        time.sleep(3)
        
        # health check for res. nodes
        # only i can remove node from set when detected failed


        # adding new responsibility
        for new_node in new_responsibility:
            responsibility_of.append(new_node)
        new_responsibility.clear()

        threads = []
        for node in responsibility_of:
            t = threading.Thread(target=check_node(node), args=(node))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        
        # 
        # print('-------------------------',failed_nodes,'--------------------')
        # continue
        # removing the failed nodes 
        for failed_node in failed_nodes:
            try:
                responsibility_of.remove(failed_node)
            except:
                1+1
            try:
                # 
                # print(f"-------------------------------node {failed_node} deleted -------------------------")
                del alive_node_address[failed_node]
                # use locking here TODO
            except:
                2+2
        failed_nodes.clear()

        

        time.sleep(2)

def broadcast_helper(ip,port):
    url = f'http://{ip}:{port}/newNode'
    data = {
        'id':my_process_id,
        'ip':my_ip,
        'port':my_port
    }
    try:
        requests.post(url, json = data)
    except:
        # TODO
        1+1
    return

        

def broadcast():

    threads = []
    for node_id in alive_node_address.keys():
        if node_id == my_process_id:
            continue
        t = threading.Thread(target=broadcast_helper, args = (alive_node_address[node_id]["ip"],alive_node_address[node_id]["port"]))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()




if __name__ == '__main__':
    
    '''
    Command line argument:
        My IP
        My Port
        Bootstrapper IP
        Bootstrapper Port
    '''

    my_ip=sys.argv[1]
    my_port=sys.argv[2]
    my_port=str(get_free_port(my_ip,my_port))
    '''
        Code to send information to bootstrapper,here
    '''
    bootstrapper_ip = sys.argv[3]
    bootstrapper_port = sys.argv[4]

    data = {
        'ip':my_ip,
        "port":my_port
    }
    
    res = requests.post(f'http://{bootstrapper_ip}:{bootstrapper_port}/initializeMe', json = data)
    print(color, "Ayush",res.text)
    res = json.loads(res.text)
    
    # check if json worked well?
    my_process_id = res['node_id']
    responsibility_of = res['responsibility']
    alive_node_address = res['database']


    
    '''
        Code to take responsibility here
    '''

    # broadcast own to all
    broadcast()

    finished = False

    
    print("now calling health check")
    start_new_thread(start_health_check, ())
   
    

    if (int(my_process_id))%4 + 1 == 1:
        start_new_thread(my_task_Process1, ())
    elif (int(my_process_id))%4 + 1 == 2:
        start_new_thread(my_task_Process2, ())
    elif (int(my_process_id))%4 + 1 == 3:
        start_new_thread(my_task_Process3, ())
    elif (int(my_process_id))%4 + 1 == 4:
        start_new_thread(my_task_Process4, ())
    else:
        # start_new_thread(my_task_Process4, ())
        
        print(color, "Error process id not mathced to any existing code")
    
    

    '''
        Perprocess server starts below
    '''
    # app.debug = True
    app.run(my_ip,my_port, debug=False)
    # f.close()