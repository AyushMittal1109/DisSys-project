from threading import Lock

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
