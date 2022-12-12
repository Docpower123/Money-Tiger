import socket
import threading
import random

addr = ('192.168.174.95', random.randint(8000, 9000))
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(addr)

name = input("Nickname: ")

"""
a function that listen to responses from the server and print them
"""


def receive():
    while True:
        message, addr1 = client.recvfrom(1024)
        print(message.decode())


# create a thread that uses the receive function
exit_flag = False
t1 = threading.Thread(target=receive)
t1.start()
# send the name of the user to the server
client.sendto(f"SIGNUP_TAG:{name}".encode(), ("192.168.174.95", 9999))

# main loop
while True:
    message = input("")
    # check if the user wants to quit: if he does kil the thread and break the loop
    if message == "!q":
        exit_flag = True
        break
    # send the server the message
    else:
        client.sendto(f"{name}: {message}".encode(), ("192.168.174.95", 9999))