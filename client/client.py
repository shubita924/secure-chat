import socket
import threading


def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1024)
        if not chunk:
            return None
        data += chunk
    return data.decode().strip()


def enter_username(client):

    msg = recv_line(client)

    if msg == 'ENTER_USERNAME':
        username = input('Enter your username:')
        client.send((username + '\n').encode())

    while True:
        msg = recv_line(client)
        
        if msg == 'USERNAME_OK':
            print('username accepted')
            break
        elif msg == 'USERNAME_TAKEN':
            print('username is taken, try another one.')
            username = input('Enter your username:')
            client.send((username + '\n').encode())
    
        


def receive_messages(client):
    
    while True:
        try:
            msg = recv_line(client)
            if not msg:
                break
            print('\n' + msg + '\n')
        except:
            break        
    
   
def main():   
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = 8899

    client.connect(('127.0.0.1', port))
    
    enter_username(client)
      
    thread = threading.Thread(target=receive_messages, args=[client])
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
            client.send((text + '\n').encode())
        except:
            break

    client.close()


if __name__=="__main__":
    main()