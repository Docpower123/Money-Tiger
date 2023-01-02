from socket import *

clients = []
slaves = []

# parameters for the server to use
HOST = '192.168.175.248'
PORT = 9999
ADDR = (HOST, PORT)


def handle_new_user(addr):
    """
    code to find out the best server
    """
    server = slaves[0]
    loadbalancer.sendto(f'{server}'.encode(), addr)
    loadbalancer.sendto(f'{addr}'.encode(), server)


# setting up the server
loadbalancer = socket(AF_INET, SOCK_DGRAM)
loadbalancer.bind(ADDR)
print('load balancer is up and running!')

# set up connection with slaves
count = 0
while True:
    data, addr = loadbalancer.recvfrom(1024)
    print(addr)
    if str(addr[1]).startswith('9'):
        slaves.append(addr)
        loadbalancer.sendto(f'done'.encode(), addr)
        count += 1
    if count == 1:
        break

# begin work with clients:
if addr not in clients and addr not in slaves:
    clients.append(addr)
    handle_new_user(addr)
