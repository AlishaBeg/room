# import socket
# import threading
# import sys

# class Server:

#     __HOST = '127.0.0.1'       # server IP
#     __PORT = 5000              # server port

#     SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#     clients = {}               # {username: (connection, address, room)}
#     rooms = {"Hell": set()}    # chat rooms with members

#     isActive = True            # server control flag

#     # ----------------- MAIN -----------------
#     @staticmethod
#     def active():
#         """Start server and admin control"""
#         Server.enable()
#         print(f"~ Server is (active)")

#         # Start admin console in background thread
#         threading.Thread(target=Server.admin_console, daemon=True).start()

#         try:
#             Server.handle_clients()
#         except Exception as err:
#             print(f"! Server error: {err}")
#         finally:
#             Server.disable()

#     # ----------------- SERVER -----------------
#     @staticmethod
#     def enable(limit=20):
#         """Bind and listen for new connections"""
#         Server.SOCKET.bind((Server.__HOST, Server.__PORT))
#         Server.SOCKET.listen(limit)
#         print(f"~ Listening on http://{Server.__HOST}:{Server.__PORT}/ (max {limit} clients)")

#     @staticmethod
#     def disable():
#         """Shutdown server and disconnect clients"""
#         Server.isActive = False

#         # disconnect all clients
#         for username, (connection, address, room) in list(Server.clients.items()):
#             try:
#                 connection.sendall("! Server is (closed)\n".encode())
#                 connection.close()
#             except:
#                 pass

#         # close socket
#         try:
#             Server.SOCKET.close()
#         except:
#             pass

#         print("~ Server disabled")
#         sys.exit(0)

#     # ----------------- CLIENT -----------------
#     @staticmethod
#     def new_client(connection, address):
#         """Handle a new client connection"""
#         try:
#             connection.sendall("Enter your username: ".encode())
#             username = connection.recv(1024).decode().strip()

#             if not username:
#                 username = f"guest_{address[1]}"

#             if username in Server.clients:
#                 connection.sendall("! Username already exists\n".encode())
#                 connection.close()
#                 return

#             # Register client in default room
#             Server.clients[username] = (connection, address, "Hell")
#             Server.rooms["Hell"].add(username)

#             print(f"+ {username} joined from {address}")
#             Server.broadcast(f"~ {username} joined Hell", "Hell")

#             connection.sendall("~ You are in room: Hell (use /join <room> to switch)\n".encode())

#             # Start client session in new thread
#             threading.Thread(target=Server.client_session, args=(username,), daemon=True).start()

#         except Exception as e:
#             print(f"! Error adding client {address}: {e}")
#             connection.close()

#     @staticmethod
#     def client_session(username):
#         """Handle client messages"""
#         connection, address, room = Server.clients[username]
#         try:
#             while True:
#                 msg = connection.recv(1024)
#                 if not msg:
#                     break

#                 message = msg.decode().strip()

#                 if message.startswith("/"):
#                     Server.handle_command(username, message)
#                 else:
#                     Server.broadcast(f"[{username}] {message}", room)

#         except:
#             pass
#         finally:
#             Server.remove_client(username)

#     @staticmethod
#     def handle_command(username, command):
#         """Handle slash commands from clients"""
#         connection, address, room = Server.clients[username]
#         parts = command.split()
#         cmd = parts[0].lower()

#         if cmd == "/quit":
#             connection.sendall("~ Bye!\n".encode())
#             Server.remove_client(username)

#         elif cmd == "/rooms":
#             rooms_list = ", ".join(Server.rooms.keys())
#             connection.sendall(f"~ Rooms: {rooms_list}\n".encode())

#         elif cmd == "/join":
#             if len(parts) < 2:
#                 connection.sendall("! Usage: /join <room>\n".encode())
#                 return
#             new_room = parts[1]
#             Server.change_room(username, new_room)

#         else:
#             connection.sendall(f"! Unknown command: {command}\n".encode())

#     @staticmethod
#     def change_room(username, new_room):
#         """Switch client to another room"""
#         connection, address, old_room = Server.clients[username]

#         if old_room in Server.rooms:
#             Server.rooms[old_room].discard(username)
#             Server.broadcast(f"- {username} left {old_room}", old_room)

#         if new_room not in Server.rooms:
#             Server.rooms[new_room] = set()
#         Server.rooms[new_room].add(username)

#         Server.clients[username] = (connection, address, new_room)

#         connection.sendall(f"~ You joined room: {new_room}\n".encode())
#         Server.broadcast(f"+ {username} joined {new_room}", new_room)

#     @staticmethod
#     def broadcast(message, room, exclude=None):
#         """Send message to all users in a room"""
#         if room not in Server.rooms:
#             return

#         for user in list(Server.rooms[room]):
#             if user in Server.clients and user != exclude:
#                 connection, _, _ = Server.clients[user]
#                 try:
#                     connection.sendall((message + "\n").encode())
#                 except:
#                     pass

#     @staticmethod
#     def remove_client(username):
#         """Remove client from server"""
#         if username not in Server.clients:
#             return

#         connection, address, room = Server.clients[username]

#         try:
#             connection.close()
#         except:
#             pass

#         del Server.clients[username]
#         if room in Server.rooms:
#             Server.rooms[room].discard(username)
#             Server.broadcast(f"- {username} disconnected", room)

#         print(f"- {username} disconnected from {address}")

#     @staticmethod
#     def handle_clients():
#         """Accept new clients continuously"""
#         while Server.isActive:
#             try:
#                 connection, address = Server.SOCKET.accept()
#                 threading.Thread(target=Server.new_client, args=(connection, address), daemon=True).start()
#             except OSError:
#                 break  # socket closed

#     # ----------------- ADMIN CONSOLE -----------------
#     @staticmethod
#     def admin_console():
#         """Server admin commands"""
#         while Server.isActive:
#             cmd = input("server> ").strip().lower()

#             if cmd == "stop":
#                 print("~ Stopping server...")
#                 Server.disable()

#             elif cmd == "clients":
#                 print("~ Connected clients:")
#                 for username, (c, address, room) in Server.clients.items():
#                     print(f"  - {username} ({address}) in {room}")

#             elif cmd == "rooms":
#                 print("~ Rooms:")
#                 for room, users in Server.rooms.items():
#                     print(f"  {room}: {', '.join(users) if users else '(empty)'}")

#             elif cmd.startswith("kick "):
#                 user = cmd.split(" ", 1)[1]
#                 if user in Server.clients:
#                     connection, _, _ = Server.clients[user]
#                     connection.sendall("! You were kicked by admin\n".encode())
#                     Server.remove_client(user)
#                     print(f"~ Kicked {user}")
#                 else:
#                     print(f"! No such client: {user}")

#             elif cmd.startswith("announce "):
#                 announcement = cmd.split(" ", 1)[1]
#                 for room in Server.rooms:
#                     Server.broadcast(f"[ADMIN] {announcement}", room)
#                 print("~ Announcement sent")

#             elif cmd:
#                 print(f"! Unknown admin command: {cmd}")


# if __name__ == "__main__":
#     Server.active()

# --------------------------------------------------------------------------------

import socket
import threading

# Server config
HOST = "127.0.0.1"
PORT = 5000

# {group_name: {client_socket: username}}

groups = {"general": {}}
lock = threading.Lock()

def broadcast(group, message, sender=None):
    with lock:
        for client, _ in groups[group].items():
            if client != sender:  # don’t send to sender
                try:
                    client.sendall(message.encode("utf-8"))
                except:
                    client.close()
                    groups[group].pop(client, None)

def handle_client(client, addr):

    client.sendall("Enter your username: ".encode("utf-8"))
    username = client.recv(1024).decode("utf-8").strip()

    # default group = general
    groups["general"][client] = username
    broadcast("general", f"\n[SERVER] {username} joined general\n")

    try:
        while True:
            msg = client.recv(1024).decode("utf-8")

            if not msg:
                break

            if msg.startswith("/join "):
                group = msg.split(" ", 1)[1].strip()
                with lock:
                    if group not in groups:
                        groups[group] = {}
                    groups[group][client] = username
                client.sendall(f"[SERVER] Joined group {group}\n".encode("utf-8"))
                continue

            elif msg.startswith("/exit"):
                client.sendall("[SERVER] Bye!\n".encode("utf-8"))
                break

            elif msg.startswith("/kick "):
                user_to_kick = msg.split(" ", 1)[1].strip()
                with lock:
                    for g in groups:
                        for c, uname in list(groups[g].items()):
                            if uname == user_to_kick:
                                c.sendall("[SERVER] You were kicked!\n".encode("utf-8"))
                                c.close()
                                del groups[g][c]
                                broadcast(g, f"[SERVER] {uname} was kicked!\n")
                                break
            else:
                # send to all in same group
                for g, members in groups.items():
                    if client in members:
                        broadcast(g, f"{username}: {msg}\n", sender=client)
                        break

    except:
        pass
    finally:
        with lock:
            for g in groups:
                if client in groups[g]:
                    del groups[g][client]
                    broadcast(g, f"\n[SERVER] {username} left {g}\n")
        client.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
