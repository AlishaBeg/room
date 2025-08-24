# server.py
# Chat Room Server with Admin Controls
# ------------------------------------
# - Multiple rooms (public/private)
# - Admin can block, fire, reset, close server
# - Users join "public" by default
# - Blocked users can only send messages to server (not to rooms)

import socket
import threading

class Server:

    __HOST = "127.0.0.1"                   # ip address
    __PORT = 5000                          # port number
    __SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket as (IPv4 and TCP)


    # clients is private set of unique client like {connect: {"username": user_name, "room": room_name}, ... } 
    __clients = {}
    
    # rooms is private set of unique room like {room_name : { connect1, connect2, ... }, ... }
    __rooms = {"public": set()}

    # set of block username
    __blocklist = set()

    # ----------------------
    # is admin or not
    # ----------------------
    def isAdmin(username):
        if username in ("ADMIN", "root"):
            return True
        else:
            return False


    # -------------------------------------------------------
    # Send a message to all clients in a given room.
    # - sender (optional): don't send back to the same user
    # -------------------------------------------------------
    @staticmethod
    def broadcast(room, message, sender=None):
        if room not in Server.__rooms:
            return
        for connect in list(Server.__rooms[room]):
            try:
                # if connection is sender than not send
                if sender and connect == sender:
                    continue
                connect.sendall(message.encode())
            except:
                Server.remove_client(connect)


    # ---------------------------------
    # Send message to a single client
    # ---------------------------------
    @staticmethod
    def send_to(connect, message):
        try:
            connect.sendall(message.encode())
        except:
            Server.remove_client(connect)


    # -------------------------------------------------------
    # Disconnect client, remove from rooms and list
    # -------------------------------------------------------
    @staticmethod
    def remove_client(connect):
        # if connection exist in server.clients set
        if connect in Server.__clients:
            user = Server.__clients[connect]["username"]
            room = Server.__clients[connect]["room"]

            # remove from current room
            if room in Server.__rooms and connect in Server.__rooms[room]:
                Server.__rooms[room].remove(connect)

            # remove from clients dictionary
            del Server.__clients[connect]
            connect.close()
            print(f"- {user} is (disconnect)")


    # -------------------------------------------------------
    # Handle all commands that start with '/'
    # -------------------------------------------------------
    @staticmethod
    def handle_command(command, connect):
        
        args = command.strip().split()
        user = Server.__clients.get(connect, {}).get("username")

        # if command /join room_name
        if command.startswith("/join "):
            room = args[1]
            # Blocked user cannot join
            if user in Server.__blocklist:
                Server.send_to(connect, f"! only request to (server)")
                return

            # if room not exist create new
            if room not in Server.__rooms:
                Server.__rooms[room] = set()
            Server.__rooms[room].add(connect)

            # update client room
            Server.__clients[connect]["room"] = room
            response = f"+ {user} is joined in {room}"
            print(response)

            Server.broadcast(room, response)

        # if command /out (leave private, go back to public)
        elif command.startswith("/out "):
            room = Server.__clients[connect]["room"]
            if room != "public":
                Server.__rooms[room].remove(connect)
                Server.__clients[connect]["room"] = "public"
                Server.__rooms["public"].add(connect)
                response = f"- {user} is out from {room}"
                print(response)
                Server.broadcast("public", response)

        # if command /blocklist
        elif command == "/blocklist":
            if not Server.__blocklist:
                respnose = "~ blocklist is empty"
                print(respnose)
                Server.send_to(user, respnose)

            else:
                response = f"~ blocklist : \n {list(Server.__blocklist)}"
                print(respnose)
                Server.send_to(user, respnose)
                

        # if command /close (shut down server)
        elif command == "/close":
            for c in list(Server.__clients.keys()):
                Server.send_to(c, "! Server closed by admin")
                Server.remove_client(c)
            Server.__SOCKET.close()
            print('~ server is (closed)')
            exit(0)

        # if command /reset (clear all rooms, users, blocklist)
        elif command == "/reset":
            Server.__clients.clear()
            Server.__rooms = {"public": set()}
            Server.__blocklist.clear()
            print("~ server is (reset)")

        # if command /clients
        elif command == "/clients":
            if not Server.__clients:
                respnose = "~ no active client found"
                print(respnose)
                Server.send_to(user, respnose)
            else:
                respnose = "~ clients :"
                print(respnose)
                Server.send_to(user, respnose)
                for c, data in Server.__clients.items():
                    respnose = f"\n > {data['username']} {data['room']}"
                    print(respnose)
                    Server.send_to(user, respnose)

        # if command /rooms
        elif command == "/rooms":
            respnose = "~ rooms :"
            print(respnose)
            Server.send_to(user, respnose)
            for room, conns in Server.__rooms.items():
                users = [Server.__clients[c]["username"] for c in conns]
                respnose = f"\n > [{room}] : {users}"
                print(respnose)
                Server.send_to(user, respnose)            

        # if command /block username
        elif command.startswith("/block "):
            target = args[1]
            Server.__blocklist.add(target)
            respnose = f"~ {target} is (blocked)"
            print(respnose)
            Server.send_to(connect, respnose)
            Server.broadcast(connect, respnose)

        # if command /unblock username 
        elif command.startswith("/unblock "):
            target = args[1]
            Server.__blocklist.discard(target)
            respnose = f"~ {target} is (unblocked)"
            print(respnose)
            Server.send_to(connect, respnose)
            Server.broadcast(connect, respnose)

        # if command /fire username (disconnectect target)
        elif command.startswith("/fire "):
            target = args[1]
            for c, info in list(Server.__clients.items()):
                if info["username"] == target:
                    Server.send_to(c, "! [server] you are (disconnectected)")
                    Server.remove_client(c)
                    print(f"- {target} is (disconnected)")
                    return


    # -----------------------------------------
    # Handle each client in a separate thread
    # -----------------------------------------
    @staticmethod
    def client_thread(connect, addr):

        # before request to user enter name
        Server.send_to(connect, "server is reqired unique username :")
        username = connect.recv(1024).decode().strip()

        Server.isAdmin(username):
            respnose = f"~ welcome admin"
            print("~ admin checkin")
            Server.send_to(username, respnose)

        # add client to public room
        Server.__clients[connect] = {"username": username, "room": "public"}
        Server.__rooms["public"].add(connect)

        response = f"+ {username} is joined in public"
        print(response)
        Server.broadcast("public", response)

        try:
            while True:

                request = connect.recv(1024).decode()
                if not request:
                    break

                # if request is command like (/) than 
                if request.startswith("/"):
                    Server.handle_command(request, connect)
                else:
                    # if user blocked → only show to server
                    if username in Server.__blocklist:
                        print(f"[BLOCKED] ({username}): {request}")
                        continue

                    room = Server.__clients[connect]["room"]
                    response = f"[{room}] ({username}): {request}"
                    print(response)

                    # send message to proper room
                    if room == "public":
                        Server.broadcast("public", response, sender=connect)
                    else:
                        Server.broadcast(room, response, sender=connect)
        finally:
            Server.remove_client(connect)

    # ---------------------------------------
    # Start the server and wait for clients
    # ---------------------------------------
    @staticmethod
    def active():

        Server.__SOCKET.bind((Server.__HOST, Server.__PORT))
        
        # limit = num(input('~ enter number of client : '))

        Server.__SOCKET.listen()

        print(f"~ server is (active) listen on [http://{Server.__HOST}:{Server.__PORT}]")

        try:
            while True:
                connect, address = Server.__SOCKET.accept()
                print(f"~ new connection {address}")
                threading.Thread(target=Server.client_thread, args=(connect, address), daemon=True).start()
        except KeyboardInterrupt:
            print("\n~ server is (stop) by user")
        finally:
            Server.__SOCKET.close()
            print("\n~ server is (close)")


if __name__ == "__main__":
    Server.active()