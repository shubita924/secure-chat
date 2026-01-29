import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 7887

client.connect(('127.0.0.1', port))

username = input('Enter your username:')

client.send(username.encode())

def receive_messages():
    
    while True:
        try:
            msg = client.recv(1024).decode()
            if not msg:
                break
            print('\n' + msg + '\n')
        except:
            break        
    
        
thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()


while True:
    try:
        text = input('\nType message:')
        text = text.strip()
        
        if text.lower() == 'quit':
            break
        
        if '|' not in text:
            print("Use format recipient|message")
            continue
        client.send(text.encode())
    except:
        break

client.close()


