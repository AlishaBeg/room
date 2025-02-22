
# -----------------
# - server script -
# -----------------

import socket


# function handling client connection or request and response

def handle_client(client_socket, client_address):

    print(f"\n client [{client_address}] connected")

    while True:

    	# received client request

        message = client_socket.recv(1024).decode()

        if message.lower() == 'exit':

            print(f"\n client {client_address} closed")

            break

        print(f"\n _(client [{client_address}]) : {message}")


        # send server response

        response = input("\n# response : ")

        client_socket.send(response.encode())


    # close connection

    client_socket.close()

# ---



# create server socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# bind socket ( ip address || port )

server_socket.bind(("localhost", 12345))


# listen connection

server_socket.listen(3)

print("\n server listening ... \n")



# accept client connection

client_socket, client_address = server_socket.accept()


# client

handle_client(client_socket, client_address)


# close server : after client interaction is done

server_socket.close()
