import socket
import threading
from datetime import datetime

clients = {}
clients_lock = threading.Lock()
public_keys = {}


def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1024)
        if not chunk:
            return None
        data += chunk
    return data.decode().strip()

# this is left here : validating that cmds[0] is USER_NAME!! I will do this later
def username_validation(client_socket):
    client_socket.sendall(b'SYS|ENTER_USERNAME\n')

    while True:
        username = recv_line(client_socket)
        cmds = username.split('|')
        
        if not cmds[1]:
            client_socket.close()
            return

        with clients_lock:
            if cmds[1] not in clients:
                clients[cmds[1]] = client_socket
                client_socket.sendall(b'SYS|USERNAME_OK\n')
                break
            else:
                client_socket.sendall(b'SYS|USERNAME_TAKEN\n')
    
    return cmds[1]
    


def handle_connection(client_socket, addr):
    
    print(f"New connection from {addr}")
    
    #enter username
    username = username_validation(client_socket)
    

    #forward messages
    try:
        while True:
            msg = recv_line(client_socket)
            if not msg:
                break
            
            cmds = msg.split('|')
            command = cmds[0]
            
            if command == 'MSG':
                recepient = cmds[1]
                message = cmds[2]
                
                if recepient in clients:
                    clients[recepient].sendall(
                        f"{command}|{username}|{message}\n".encode()
                    )
                    now = datetime.now()
                    print('[\033[32m'+ str(now.hour) + ':' + str(now.minute) + '\033[0m]', username, '->', recepient + ':', message)
                else:
                    client_socket.sendall(
                        f"ERROR|User {recepient} not online.\n".encode()
                    )
            elif command == 'SYS':
                if cmds[1] == 'PUBLIC_KEY':
                    public_keys[username] = cmds[2]
                elif cmds[1] == 'KEY_REQUEST':
                    requested_user = cmds[2]
                    if requested_user in public_keys:
                        key = public_keys[requested_user]
                        client_socket.sendall(
                            f"SYS|PUBLIC_KEY|{requested_user}|{key}\n".encode()
                        )
                    else:
                        client_socket.sendall(
                            f"ERROR|User {requested_user} not online.\n".encode()
                        )
            elif command == 'KEY_EXCHANGE':
                recepient = cmds[1]
                encrypted_key = cmds[2]

                if recepient in clients:
                    clients[recepient].sendall(f"KEY_EXCHANGE|{username}|{encrypted_key}\n".encode())
                else:
                    client_socket.sendall(f"ERROR|User {recepient} not online.\n".encode())

    except:
        pass
    finally:
        print(public_keys)
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

