# SecureChat

SecureChat is a simple end-to-end encrypted chat application built with Python sockets.
The server never sees plaintext messages.

## Features

- One-to-one messaging
- RSA public key exchange
- AES (Fernet) session keys per peer
- Encrypted messages end-to-end
- Multi-client server using threads

## Architecture

- Client generates RSA key pair on startup
- Public keys are exchanged via the server
- AES session keys are encrypted with RSA and sent peer-to-peer
- Messages are encrypted with AES before being sent

Server acts only as a relay and cannot decrypt messages.

## How to Run

1. Start the server:

```bash
python server/server.py

```

2. Start clients in separate terminals:

```bash
python client/client.py

```

3. Send messages using:

```bash
recipient|message

```
