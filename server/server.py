import socket
import threading


def handle_connection(client_socket, addr):
    
    print(f"New connection from {addr}")
    
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            print(f'{addr}: {msg}')
            client_socket.send(f'Echo:{msg}'.encode())
        except:
            break
        
    client_socket.close()
    print(f'connection closed: {addr}')


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket successfully created!")

port = 7077

server_socket.bind(('', port))
print('socket binded to', port)

server_socket.listen(5)
print('socket is listening..')


while True:
    
    client, addr = server_socket.accept()
    print('Incoming Connection from', addr)
    
    thread = threading.Thread(target=handle_connection, args=(client, addr))
    
    thread.start()
    



