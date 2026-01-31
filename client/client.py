import socket
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import base64

session_keys = {}



def send_key_exchange(client, recipient):
    
    aes_key = Fernet.generate_key()  
    recipient_pub_pem = request_public_key(client, recipient)
    if not recipient_pub_pem:
        return None

    
    recipient_pub = serialization.load_pem_public_key(
        recipient_pub_pem.encode()
    )

    
    encrypted_key = recipient_pub.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    
    client.send(
        b"KEY_EXCHANGE|" + recipient.encode() + b"|" + base64.b64encode(encrypted_key) + b"\n"
    )
    
    return aes_key  




def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
def request_public_key(client, recipient):
    
    client.send(f"SYS|KEY_REQUEST|{recipient}\n".encode())
    
    while True:
        msg = recv_line(client)
        cmds = msg.split('|')
        if cmds[0] == 'SYS' and cmds[1] == 'PUBLIC_KEY' and cmds[2] == recipient:
            pub_key_pem = cmds[3]
            return pub_key_pem
        elif cmds[0] == 'ERROR':
            print(cmds[1])
            return None





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
    cmds = msg.split('|')

    if cmds[0] == 'SYS' and cmds[1] == 'ENTER_USERNAME':
        username = input('Enter your username:')
        client.send(('USERNAME|' + username + '\n').encode())

    while True:
        msg = recv_line(client)
        cmds = msg.split('|')
        
        if cmds[0] == 'SYS' and cmds[1] == 'USERNAME_OK':
            print('username accepted')
            break
        elif cmds[0] == 'SYS' and cmds[1] == 'USERNAME_TAKEN':
            print('username is taken, try another one.')
            username = input('Enter your username:')
            client.send(('USERNAME|' + username + '\n').encode())
    
        


def receive_messages(client, rsa_private_key):
    
    while True:
        try:
            msg = recv_line(client)
            if not msg:
                break
            cmds = msg.split('|')
            command = cmds[0]
            sender = cmds[1]
            message = cmds[2]
            if command == 'MSG':
                cipher = Fernet(session_keys[sender])
                print('\n' + sender + ' -> ' + cipher.decrypt(message.encode()).decode() + '\n')
            elif command == 'KEY_EXCHANGE':
                
                sender = cmds[1]  
                encrypted_key_b64 = cmds[2]
                
                encrypted_key = base64.b64decode(encrypted_key_b64)
                
                aes_key = rsa_private_key.decrypt(
                    encrypted_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                session_keys[sender] = aes_key
                print(f"[INFO] Received AES session key from {sender}")

        except:
            print("errorrrrr")
            break        
    
   
def main():   
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = 8899

    client.connect(('127.0.0.1', port))
    
    enter_username(client)
    
    rsa_private_key, rsa_public_key = generate_rsa_keys()
    
    serialized_public_key = serialize_public_key(rsa_public_key)
    
    client.send(b'SYS|PUBLIC_KEY|' + serialized_public_key + b'\n')
      
    thread = threading.Thread(target=receive_messages, args=[client, rsa_private_key])
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
            recipient = text.split('|', 1)[0]
            message = text.split('|', 1)[1]
            
            if recipient not in session_keys:
                session_key = send_key_exchange(client, recipient)
                session_keys[recipient] = session_key
            
            encrypted_message = Fernet(session_keys[recipient]).encrypt(message.encode())
            client.send(b'MSG|' + recipient.encode() + b'|' + encrypted_message + b'\n')
        except:
            break

    client.close()


if __name__=="__main__":
    main()