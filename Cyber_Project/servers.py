import threading
import subprocess

def run_script1():
    subprocess.run(["python3", "LoadBalancer.py"])

def run_script2():
    subprocess.run(["python3", "slave1.py", "192.168.68.111", "192.168.68.111"])

thread1 = threading.Thread(target=run_script1)
thread2 = threading.Thread(target=run_script2)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
