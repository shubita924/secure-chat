import socket
import threading

from crypto_utils import (
    generate_rsa_keys,
    serialize_public_key,
    load_public_key,
    generate_aes_key,
    encrypt_message,
    decrypt_message,
    encrypt_aes_key_with_rsa,
    decrypt_aes_key_with_rsa
)


session_keys = {}



def send_key_exchange(client, recipient):
    aes_key = generate_aes_key()

    recipient_pub_pem = request_public_key(client, recipient)
    if not recipient_pub_pem:
        return None

    recipient_pub = load_public_key(recipient_pub_pem)
    encrypted_key_b64 = encrypt_aes_key_with_rsa(aes_key, recipient_pub)

    client.send(
        b"KEY_EXCHANGE|" + recipient.encode() + b"|" + encrypted_key_b64 + b"\n"
    )

    return aes_key
  
    
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

            if command == 'MSG':
                sender = cmds[1]
                encrypted_msg = cmds[2].encode()
                print(
                    '\n' + sender + ' -> ' +
                    decrypt_message(session_keys[sender], encrypted_msg) + '\n'
                )

            elif command == 'KEY_EXCHANGE':
                sender = cmds[1]
                encrypted_key_b64 = cmds[2]

                aes_key = decrypt_aes_key_with_rsa(
                    encrypted_key_b64,
                    rsa_private_key
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
            
            encrypted_message = encrypt_message(
                session_keys[recipient],
                message
            )
            client.send(b'MSG|' + recipient.encode() + b'|' + encrypted_message + b'\n')

        except:
            break

    client.close()


if __name__=="__main__":
    main()