from threading import Lock

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

