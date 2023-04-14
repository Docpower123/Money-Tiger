from socket import *
from settings import *
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import mysql.connector

clients = []
slaves = []

# parameters for the server to use
PORT = LB_PORT
ADDR = ('0.0.0.0', PORT)


def load_private_key(filename):
    with open(filename, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return private_key


def load_public_key(filename):
    with open(filename, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key


def receive_message(server_socket, private_key, public_key):
    data, client_address = server_socket.recvfrom(RECV_SIZE)
    signature, encrypted_message = data[:256], data[256:]
    try:
        public_key.verify(
            signature,
            encrypted_message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except:
        print("Invalid signature")
        server_socket.close()
        exit()
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message, client_address


def send_response(server_socket, response, public_key, private_key, client_address):
    encrypted_response = public_key.encrypt(
        response,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    signature = private_key.sign(
        encrypted_response,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    server_socket.sendto(signature + encrypted_response, client_address)


def handle_new_user(addr):
    """
    code to find out the best server
    """
    print('new client!', addr)
    server = slaves[0]
    send_response(loadbalancer, f'{server}'.encode(), public_key, private_key, addr)


def lb_main():
    loadbalancer.bind(ADDR)
    print('load balancer is up and running!')

    # connecting to the database
    db = mysql.connector.connect(host="mysql-serve", port="3306", user="client", passwd="P123321p", database="dblogin",
                                 auth_plugin='mysql_native_password')
    mycur = db.cursor()

    # set up connection with slaves
    count = 0
    while True:
        data, addr = receive_message(loadbalancer, private_key, public_key)
        if str(addr[1]).startswith('9'):
            slaves.append((data, addr[1]))
            send_response(loadbalancer, f'done'.encode(), public_key, private_key, addr)
            count += 1
        if count == 1:
            break

    while True:
        # begin work with clients:
        data, addr = receive_message(loadbalancer, private_key, public_key)
        if addr not in clients and addr not in slaves:
            clients.append(addr)
            handle_new_user(addr)

        # save info in database
        message = data
        if message.decode().find(';') != -1 and message.decode().split(';')[1] == "DBS":
            messag = message.decode().split(';')
            info_name = messag[2]
            for i in range(3):
                messag.pop(0)
            t = tuple(messag)
            sql = f"update dblogin set {info_name} = %s where Username = %s"
            mycur.execute(sql, t)
            db.commit()

        # get info from database
        elif message.decode().find(',') != -1 and message.decode().split(',')[1] == "DBG":
            messag = message.decode().split(',')
            info_name = messag[2]
            user_password = messag[3]
            user_name = messag[0]
            # get info from database
            sql = f"select {info_name} from dblogin where Username = %s and Password = %s"
            mycur.execute(sql, [(user_name), (user_password)])
            info = mycur.fetchall()
            # send info to client
            send_response(loadbalancer, f"SERVER,DBG,{info[0][0]}".encode(), public_key, private_key, addr)

        # log varify
        elif message.decode().find(',') != -1 and message.decode().split(',')[1] == "LV":
            user_varify = message.decode().split(',')[2]
            pass_varify = message.decode().split(',')[3]
            sql = "select * from dblogin where Username = %s and Password = %s"
            mycur.execute(sql, [(user_varify), (pass_varify)])
            results = mycur.fetchall()
            if results:
                send_response(loadbalancer, "SERVER,LV,T".encode(), public_key, private_key, addr)
            else:
                send_response(loadbalancer, "SERVER,LV,F".encode(), public_key, private_key, addr)

        # register new clients
        elif message.decode().find(',') != -1 and message.decode().split(',')[1] == "REG":
            username = message.decode().split(',')[2]
            password = message.decode().split(',')[3]
            sql = "insert into dblogin (Username, Password) values(%s,%s)"
            t = (username, password)
            mycur.execute(sql, t)
            db.commit()

        if data.decode()[0:4] == "KILL":
            clients.remove(addr)

# Load the private key from the PEM encoded file
private_key = load_private_key("private_key.pem")
# Load the public key from the PEM encoded file
public_key = load_public_key("public_key.pem")
# setting up the server
loadbalancer = socket(AF_INET, SOCK_DGRAM)


if __name__ == "__main__":
    lb_main()



# Structure: (USERNAME,TYPE,DATA)
# Types:
    # PSS - POSITION STATUS STATS - DATA=player(x,y,status,health)+enemies(x,y,status,health,index)
    # MDROP - make drops - DATA=(drop_name,x,y, drop_status)
    # PDROP - pick drops - DATA=(drop_name,x,y)
    # WAT - weapon attack - DATA=(player_x,player_y,status,name)
    # MAT - magic attack - DATA=(magic_x,magic_y,status,name)
    # HURT - enemies hurt - DATA=(enemy_index,player_damage)
    # KILL - client is no more in game - DATA=(username)
    # LOG - client logged in - DATA=(username)
    # MSG - client sent message - DATA=(message)
    # REG - client register - DATA=(username,password)
    # LV (from client) - client login varify - DATA=(username,password)
    # LV (from server) - server response if login succeed or failed - DATA=(T/F)
    # DBS - set info in database - DATA=(info_name,t)
    # DBG (from client) - ask for info which in database - DATA=(info_name,user_password)
    # DBG (from server) - return info which in database - DATA=(info)
    # MSG - client sent message - DATA(message)
