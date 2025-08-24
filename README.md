# Room  

**Room** is a simple real-time chat room application built in **Python** using sockets.  
It allows multiple clients to connect to a server, join rooms, send messages, and interact in real time.  
The server has full control over user management and room access.  


          ┌────────────┐
          │   Server   │
          └─────┬──────┘
                │
 ┌──────────────┼──────────────┐
 │              │              │
 ▼              ▼              ▼
Client A      Client B      Client C
(Alice)       (Bob)         (Admin="")
(public)      (public)      (admin)


---

### Server  
- Manages all client connections.  
- Assigns users to the **public room** by default.  
- Supports **private rooms** (users can join/exit freely).  
- Prints messages in format:  

- Blocklist support → blocked users can send messages only to the server, not to rooms.  
- Admin-only commands:  
- `/reset` → reset all rooms and clients.  
- `/close` → shut down the server.  
- `/block <username>` → block a user.  
- `/unblock <username>` → remove user from blocklist.  
- `/fire <username>` → disconnect a user.  
- `/out <username>` → force a user to leave a room.  

### Client  
- Connects to the server and chooses a username.  
- Sends messages to rooms or requests to join private rooms.  
- Listens for real-time updates (all messages appear instantly).  
- Can exit with `/exit`.  

---

---

## execute

_if server once is active then number of client active_

```bash

room/
│
├── server.py    # server script
├── client.py    # client script
└── README.md    # documentation

cd room

pyhton server.py

# else

python client.py

```


###### SERVER SCRIPT

```py

import socket

__HOST = '127.0.0.1'    # ip address

__PORT = 5000           # port number

# socket as (IPv4 and TCP)

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind socket with ip address and port

SOCKET.bind((Server.__HOST, Server.__PORT))

# Active server and listen connection with number or client (limit)

SOCKET.listen(5)

# This function run server loop or handle client    

connect, address = SOCKET.accept()

# Get request of client

response = input(' server response : ').encode()

connect.sendall(response)

# Send response to connected client 

request = connect.recv(1024).decode()

print(f'- client request : {request}')

# close client connection

connect.close()

# Close server SOCKET

SOCKET.close()

```
###### CLIENT SCRIPT

```py

import socket

__HOST = '127.0.0.1'    # ip address

__PORT = 5000           # port number

# socket as (IPv4 and TCP)

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect with (server) use ip and and port number 

SOCKET.connect((Server.__HOST, Server.__PORT))

# Listen server response  

request = SOCKET.recv(1024).decode()

print(f'- server response : {request}')

# Send client request

response = input(' client request : ').encode()

SOCKET.sendall(response)

# close client connection

SOCKET.close()

# Close server SOCKET

SOCKET.close()

```