# client.py
# A simple IPv4 and TCP chat client script

import socket
import threading
import sys

class Client:
    __HOST = "127.0.0.1"   # ip address
    __PORT = 5000          # port number
    __SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Continuously listen for server messages
    @staticmethod
    def listen():
        try:
            while True:
                response = Client.__SOCKET.recv(1024).decode()
                if not response:
                    break
                # keep input prompt on same line
                sys.stdout.write("\r" + response + "\n> ")
                sys.stdout.flush()
        except:
            pass

    # Continuously read user input and send to server
    @staticmethod
    def send():
        try:
            while True:
                request = input("> ")

                if request.strip().upper() == "EXIT":
                    Client.__SOCKET.sendall(b"/exit")
                    break

                Client.__SOCKET.sendall(request.encode())
        except KeyboardInterrupt:
            print("\n! client stopped by user")
        finally:
            Client.__SOCKET.close()
            print("~ client is (disconnected)")

    # Start client connection
    @staticmethod
    def active():
        try:
            Client.__SOCKET.connect((Client.__HOST, Client.__PORT))
            print(f"~ connected to server [http://{Client.__HOST}:{Client.__PORT}]")

            # background listener thread
            threading.Thread(target=Client.listen, daemon=True).start()

            # main thread handles user input
            Client.send()

        except ConnectionRefusedError:
            print("! connection failed: server not running?")

# Run client script
if __name__ == "__main__":
    Client.active()
