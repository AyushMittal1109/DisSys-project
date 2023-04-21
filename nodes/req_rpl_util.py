from threading import Lock

reply_defered_to=[]
reply_defered_to_lock = Lock() 

def get_reply_defered_to():
    reply_defered_to_lock.acquire()
    global reply_defered_to
    temp=reply_defered_to
    reply_defered_to_lock.release()
    return temp

def append_reply_defered_to(input):
    reply_defered_to_lock.acquire()
    global reply_defered_to
    reply_defered_to.append(input)
    reply_defered_to_lock.release()

def remove_reply_defered_to(input):
    reply_defered_to_lock.acquire()
    global reply_defered_to
    ele_to_delete=[]
    for x in reply_defered_to:
        if x[0]==input[0] and x[1]==input[1]:
            ele_to_delete.append(x)
    for y in ele_to_delete:
        reply_defered_to.remove(y)
    reply_defered_to_lock.release()

def erase_reply_defered_to():
    reply_defered_to_lock.acquire()
    global reply_defered_to
    reply_defered_to=[]
    reply_defered_to_lock.release()


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
    
'''

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

    
    waiting_for_reply_from_lock.release()
    #unlock
    return status
