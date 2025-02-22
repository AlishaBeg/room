
# -----------------
# - client script -
# -----------------

import socket

# function handling server connection or request and response

def handle_server(client_socket):

	while True :

		# send server request

		message = input("\n# request : ")

		client_socket.send(message.encode())

		if message.lower() == 'exit':

			print("\n server connection closed!")

			break

		# received server response

		response = client_socket.recv(1024).decode()

		print(f"\n _(server) : {response}")


	# close connection

	client_socket.close();



# ---

# create a socket object

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# connect to the server on localhost and port

client_socket.connect(("localhost", 12345))


# server

handle_server(client_socket)

