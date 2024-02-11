import socket
from threading import Thread, Lock
from queue import Queue


THREADS = 100
p_lock = Lock()
thread_queue = Queue()
OPEN = []
CLOSED = []

def ipCheck(ip):
    ip = str.strip(ip)
    ip_split = ip.split('.')
    ip_split = [int(numeric_string) for numeric_string in ip_split]
    if(all(x > 255 for x in ip_split) or ip_split[-1] > 254 or len(ip_split) != 4):
        raise ValueError("Invalid IP-address") 
    else:
        return ip

def rangeCheck(ports):
    ports = str.strip(ports)
    start, end = ports.split("-")
    if(str.isnumeric(start) and str.isnumeric(end)):
        start, end = int(start), int(end)
        if(end > 65535):
            raise ValueError("Port "+str(end)+" is out of range")
        else: 
            return [start, end]
    else:
        raise ValueError("Chars are not ports")

def ping(ip, ports):
    global thread_queue

    try:
        st = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        st.settimeout(10) # Change this to whatever you like
        st.connect((ip, ports))
    except:
        with p_lock:
            CLOSED.append(ports) 
    else:
        with p_lock:
            print("[+] Port " + str(ports) + " is open")
            OPEN.append(ports)
    finally:
        st.close()

def thread(target):
    global thread_queue
    while True:
        thread_worker = thread_queue.get()
        ping(target, thread_worker)
        thread_queue.task_done()

def timedOut(ports):
    if((len(OPEN)+len(CLOSED)) == len(ports)):
        return False
    else:
        return True



def main():
    global thread_queue
    while True:
        try:
            iptarget = input("Target: ")
            ipCheck(iptarget)
            break
        except ValueError as e:
            print(e)
    while True:
        try:
            ports = input("Port range (e.g 1-100): ")
            ports = rangeCheck(ports)
            ports = [p for p in range(ports[0], ports[1]+1)]
            break
        except ValueError as e:
            print(e)
    
    global thread_queue
    for t in range(THREADS):
        t = Thread(target=thread, args = (iptarget, ))
        t.daemon = True
        t.start()
    for worker in ports:
        thread_queue.put(worker)
    thread_queue.join()
    print("---SUMMARY---")
    OPEN.sort()
    CLOSED.sort()
    open = ", ".join(str(num) for num in OPEN)
    closed = ", ".join(str(num) for num in CLOSED)
    print("Open ports: " + open)
    print("Closed ports: " + closed)
    
    
    if(timedOut(ports)):
        scan_result = set(OPEN) | set(CLOSED)
        all_ports = set(ports)
        missing_ports = all_ports-scan_result
        missing_ports = ", ".join(str(num) for num in missing_ports)
        print("WARNING: Following ports where neither considered open or closed: "+ missing_ports)


main()
