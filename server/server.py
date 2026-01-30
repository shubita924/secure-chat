import socket
import threading
from datetime import datetime

clients = {}
clients_lock = threading.Lock()


def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1024)
        if not chunk:
            return None
        data += chunk
    return data.decode().strip()


def handle_connection(client_socket, addr):
    
    print(f"New connection from {addr}")
    
    #enter username
    client_socket.sendall(b'ENTER_USERNAME\n')

    while True:
        username = recv_line(client_socket)
        if not username:
            client_socket.close()
            return

        with clients_lock:
            if username not in clients:
                clients[username] = client_socket
                client_socket.sendall(b'USERNAME_OK\n')
                break
            else:
                client_socket.sendall(b'USERNAME_TAKEN\n')


    #forward messages
    try:
        while True:
            msg = recv_line(client_socket)
            if not msg:
                break
            
            split = msg.split('|', 1)
            recepient = split[0]
            message = split[1]
            
            if recepient in clients:
                clients[recepient].sendall(
                    f"{username}|{message}\n".encode()
                )
                now = datetime.now()
                print('[\033[32m'+ str(now.hour) + ':' + str(now.minute) + '\033[0m]', username, '->', recepient + ':', message)
            else:
                client_socket.sendall(
                    f"User {recepient} not online.\n".encode()
                )
    except:
        pass
    finally:
        client_socket.close()
        with clients_lock:
            if username in clients:
                del clients[username]
        print(f'[' + '\033[31mserver\033[0m' + '] ' + username + ' went offline')


def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created!")

    port = 8899

    server_socket.bind(('', port))
    print('socket binded to', port)

    server_socket.listen(5)
    print('socket is listening..')

    while True:
        
        client, addr = server_socket.accept()
        
        thread = threading.Thread(target=handle_connection, args=(client, addr))
        
        thread.start()
    

if __name__=="__main__":
    main()

