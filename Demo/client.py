import socket
import threading
import random

addr = ('192.168.1.168', random.randint(8000, 8999))
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(addr)

server = ("192.168.1.168", 9999)

name = input("Nickname: ")
client.sendto(f"SIGNUP_TAG:{name}".encode(), server)
while True:
    message, addr1 = client.recvfrom(1024)
    if addr1[0] == '192.168.1.168':
        server = eval(message)
        print(server)
        break

client.sendto(f"SIGNUP_TAG:{name}".encode(), server)