import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 7077

client.connect(('127.0.0.1', port))

client.send('hellloooo'.encode())

print(client.recv(1024).decode())

client.close()


