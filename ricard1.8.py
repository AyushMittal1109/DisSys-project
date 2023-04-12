#!/usr/bin/python3
from _thread import *
import threading
import random
import socket
import pickle
import time
import sys 
'''
Two types of msg REQUEST and REPLY

pi that is waiting for CS and gets REQUEST pj , 
if priority(pj)s REQUEST < pi then pi defers REPLY to pj and sends a REPLY message to pj after CS of pending request.

Processes use Lamport-style logical clocks to assign a timestamp to critical section requests and timestamps are used to decide the priority of requests.
Each process pi maintains the Request-Deferred array, RDi , the size of which is the same as the number of processes in the system.
Initially, ∀i ∀j: RDi [j]=0. Whenever pi defer the request sent by pj , it sets RDi [j]=1 and after it has sent a REPLY message to pj , it sets RDi [j]=0.

request is of form 
[local event, process id]

Process A has high priority if  
    (local event A < local event B) or ((local event A = local event B) and (process id A < process id B))


process id is unique



Explanation:
	Sj gets request from Si send reply when
    Not in CS
    Not requesting CS
    Sj is requesting and TS(Sj) > TS(Si)
        Else defer reply.



Enter Cs when Reply from every site.

After CS send reply to every defered message

'''


'''
Global Declaration
'''
print_lock = threading.Lock()
# max_process_num=100
Executing_CS=0 #surround this variable by locks
Requesting_CS=0 #surround this variable by locks
My_current_CS_req=-1
my_cs_acess_time=[]
my_ip
base_port
my_port
my_process_id
my_name
node_mgr_ip
node_mgr_port
my_cs_acess_time

def get_Executing_CS():
    # lock
    global Executing_CS
    temp=Executing_CS
    #unlock
    return temp

def set_Executing_CS(input):
    # lock
    global Executing_CS
    Executing_CS=input
    #unlock

def get_Requesting_CS():
    # lock
    global Requesting_CS
    temp=Requesting_CS
    #unlock
    return temp

def set_Requesting_CS(input):
    # lock
    global Requesting_CS
    Requesting_CS=input
    #unlock

def get_My_current_CS_req():
    # lock
    temp=My_current_CS_req
    #unlock
    return temp

def update_My_current_CS_req():
    global my_cs_acess_time
    if my_cs_acess_time.size() <= 0:
        set_Requesting_CS(0)
    else:
        # lock--needed?
        global My_current_CS_req
        My_current_CS_req=my_cs_acess_time[0]
        my_cs_acess_time.pop(0)
        #unlock

RequestDefered=[]


def my_request_receiving_thread_helper(c):
    '''
        helper function for my_request_receiving_thread  
        this function recieves request msg from processes
        and if it can send reply immediately,then it sends reply msg immedidately
        otherwise it defers the reply and reply is collectely sent for the deffered request
        after cs execution. 
    '''
    data = c.recv(1024)# received request from client
    data=pickle.loads(data)
    # [requestor's local event, requestor's process id]
    his_local_event=data[0]
    his_process_id=data[1]
    # add lock
    if get_Executing_CS()==0:
        data=pickle.dumps("ok!")
        c.sendall(data) #reply msg sent immediately
        c.close()
    elif get_Requesting_CS()==0:
        data=pickle.dumps("ok!")
        c.sendall(data) #reply msg sent immediately
        c.close()
    elif (get_My_current_CS_req() > his_local_event) or ((get_My_current_CS_req() == his_local_event) and (my_process_id > his_process_id)): # if i am here then i am requesting CS
        data=pickle.dumps("ok!")
        c.sendall(data) #reply msg sent immediately
        c.close()
    else:
        global RequestDefered
        RequestDefered.append([c]) #reply msg delayed immediately
    

def my_request_receiving_thread(my_name,my_number,my_host,my_port):
    '''
        Function starts a server where other process can send me request
    '''
    host = my_host
    port = my_port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print(my_name, ": My Socket binded to port", port)
    s.listen(1024)    # Max number of process supported 1024
    print(my_name, ": Started Listening")
    while True:
        c, addr = s.accept()
        print(my_name, ': Connected to :', addr[0], ':', addr[1])
        start_new_thread(my_request_receiving_thread_helper, (c,))
    s.close()


def my_request_sending_thread(my_name,my_host,my_port,my_process_id,my_cs_acess_time,processes):
    '''
        Function sends request message to everyone (broadcast)
        Afterwards wait for reply from everyone(If other end is alive).
        If Recieved reply from everyone then
        Execute CSs

    '''
    for local_envent_time in my_cs_acess_time:
        get_reply_from=[]
        # get processes from node manager (currently using hardcoded value)
        for process in processes: # sends request msg to all.
            if process.process_id==my_process_id:
                continue 
            his_number=process.process_id
            his_name="Process"+his_number
            his_host=process.host
            his_port=process.ricard_listening_port
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((his_host,his_port))
            message = [local_envent_time,my_process_id]
            data=pickle.dumps(message)
            s.sendall(data) 
            print(my_name,":Sent request to",his_name)
            get_reply_from.append([his_number,his_name,his_host,his_port,s])

        #request sent to all, now get reply from all.
        for process_info in get_reply_from:
            s=process_info[4]
            data = s.recv(1024)
            '''
                convert this recv so that it does not wait indefinately,
                it waits for few seconds then asks node manager if this process is alive or not
                if alive then keep waiting, if not alive then close connection and continue to next iteration 
            '''
            
            data=pickle.loads(data) # if i get a reply then it means the other process has no issue if i enter CS
            if data=="ok!":
                s.close()
            else:
                print(my_name,":Unexpected error")

        # in terminal the following two output should be together to ensure that no one else entered cs in non-mutually exclusive manner
        print(my_name,": CS execution started:", local_envent_time)
        randomtime=random.randint(0,10)
        time.sleep(randomtime)
        print(my_name,": CS execution completed:", local_envent_time)
        update_My_current_CS_req()
        # send reply to all other processes.
        for request in RequestDefered:
            data=pickle.dumps("ok!")
            request.sendall(data)
            request.close()



def Main():
    '''
    Command line argument:
        My IP
        My Ricard_listening_port
        My Process_id
        Node_mgr's ip 
        Node_mgr's port 
        Number of times you want to access CS and your local event when you want to acess CS 
    '''
    global my_ip
    global base_port
    global my_port
    global my_process_id
    global my_name
    global node_mgr_ip
    global node_mgr_port
    global my_cs_acess_time
    my_ip=sys.argv[1]
    base_port=1024
    my_port=base_port+sys.argv[2] #add code to check if this address is availbale or not, if not available then dynamically pick a available port
    my_process_id=sys.argv[3]
    my_name="Process"+my_process_id
    node_mgr_ip=sys.argv[4]
    node_mgr_port=sys.argv[5]
    count_cs_access=sys.argv[6]
    
    for i in range(count_cs_access):
        my_cs_acess_time.append(sys.argv[7+i])
    my_cs_acess_time.sort()
    #dynamically assign a port for listening to heartbeat signal
    # send_my_address_to_node_mgr at node_mgr_ip node_mgr_port
    # recieve the following information from node mgr
    processes = [
        { "process_id": "1", "host": "localhost", "ricard_listening_port": 8000},
        { "process_id": "2", "host": "localhost", "ricard_listening_port": 8001},
        { "process_id": "3", "host": "localhost", "ricard_listening_port": 8002},
        { "process_id": "4", "host": "localhost", "ricard_listening_port": 8003}
    ] 
    start_new_thread(my_request_receiving_thread, (my_name,my_ip,my_port,my_process_id,))
    global Requesting_CS
    if my_cs_acess_time.length()!=0:
        Requesting_CS=0
    else:
        Requesting_CS=1
    start_new_thread(my_request_sending_thread, (my_name,my_ip,my_port,my_process_id,my_cs_acess_time,processes, ))
    #wait for all thread to complete
    # threads.join()


if __name__ == '__main__':
	Main()



'''
write test case to check the case when i am executing CS and I am the next process to enter CS next as well.

'''