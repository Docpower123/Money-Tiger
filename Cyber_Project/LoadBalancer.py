from socket import *
from settings import *

clients = []
slaves = []

# parameters for the server to use
HOST = LB_IP
PORT = LB_PORT
ADDR = (HOST, PORT)


def handle_new_user(addr):
    """
    code to find out the best server
    """
    print('new client!', addr)
    server = slaves[0]
    loadbalancer.sendto(f'{server}'.encode(), addr)
    loadbalancer.sendto(f'IP{addr}'.encode(), server)


# setting up the server
loadbalancer = socket(AF_INET, SOCK_DGRAM)
loadbalancer.bind(ADDR)
print('load balancer is up and running!')

# set up connection with slaves
count = 0
while True:
    data, addr = loadbalancer.recvfrom(1024)
    if str(addr[1]).startswith('9'):
        slaves.append(addr)
        loadbalancer.sendto(f'done'.encode(), addr)
        count += 1
    if count == 1:
        break

while True:
    # begin work with clients:
    data, addr = loadbalancer.recvfrom(1024)
    if addr not in clients and addr not in slaves:
        clients.append(addr)
        handle_new_user(addr)


# ------------------- to fix / to add -------------------
# synchronized enemies - movement and health are shit
# chat!
# synchronized pickup of drop sometimes does not work :(
# synchronized weapons & magic
# one squid can collide EVERYTHING
# auto movement do problems
# players join during game

# ------------------- what we have -------------------
# synchronized movement
# synchronized animation
# synchronized health
# synchronized drops

# Structure: (USERNAME,TYPE,DATA)
# Types:
    # PSS - POSITION (movement) STATUS (animation) STATS (health) - DATA=player(x,y,status,health)+enemies(x,y,status,health)
    # TDROP - take drops - DATA=(drop_name,x,y, drop_status)
    # PDROP - pick drops - DATA=(drop_name,x,y)
