import socket
import threading

clients = {}


def handle_connection(client_socket, addr):
    
    print(f"New connection from {addr}")
    
    
    username = client_socket.recv(1024).decode()
    
    clients[username] = client_socket
    
    print(clients)
    
    try:
        while True:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            print(f'{addr}: {msg}')
            
            split = msg.split('|')
            recepient = split[0]
            message = split[1]
            
            if recepient in clients:
                clients[recepient].send(f"{username}--> {message}".encode())
            else:
                client_socket.send(f"User {recepient} not online.".encode())
            
    except:
        pass
    finally:
        client_socket.close()
        if username in clients:
            del clients[username]
        print(f'connection closed: {addr}')


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket successfully created!")

port = 7887

server_socket.bind(('', port))
print('socket binded to', port)

server_socket.listen(5)
print('socket is listening..')


while True:
    
    client, addr = server_socket.accept()
    
    thread = threading.Thread(target=handle_connection, args=(client, addr))
    
    thread.start()
    



