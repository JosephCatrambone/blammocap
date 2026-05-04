import asyncio
import json
import socket  # I guess we could make a dependency on an HTTP library.
import websockets

backlog_capacity = 100
shutdown = False

#fname.split("/")[-1]: open(fname, 'rt').read() for fname in []
served_files = {
	"index.html": ("text/html", open("../client/index.html", 'rt').read()),
	"ml5.1.3.1.min.js": ("application/javascript", open("../client/ml5.1.3.1.min.js", 'rt').read()),
	"p5.1.11.13.min.js": ("application/javascript", open("../client/p5.1.11.13.min.js", 'rt').read()),
	"sketch.js": ("application/javascript", open("../client/sketch.js", 'rt').read()),
}

async def handle_websocket_data(part_callback):
	uri = "ws://0.0.0.0:34567"

	async with websockets.connect(uri) as websocket:
		while True:
			try:
				# Receive data from websocket
				data = await websocket.recv()
				data = json.loads(data)

			except websockets.exceptions.ConnectionClosed:
				print("Connection closed")
				break


# Mostly taken from https://wangkuiyi.github.io/asyncio_serving.html
async def start_server(client_handler_fn, host="127.0.0.1", port: int=8080):
	"""Given a client_handler_fn, awaits an infinite loop which does client accepts and dispatches requests to the
	client_handler_fn.  client_handler_fn should take the client socket and client address."""
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((host, port))
	server_socket.listen(backlog_capacity)
	server_socket.setblocking(False)
	await accept_clients(server_socket, client_handler_fn)


async def accept_clients(server_socket, client_handler_fn):
	"""Loops infinitely accepting inbound requests from clients and making tasks."""
	# client_handler_fn should take a client_socket and client_address.
	loop = asyncio.get_event_loop()
	while not shutdown:
		client_socket, client_address = await loop.sock_accept(server_socket)
		client_socket.setblocking(False)
		asyncio.create_task(client_handler_fn(client_socket, client_address))


async def serve_http_pages(client_socket, client_address):
	try:
		loop = asyncio.get_running_loop()  # Get the event loop created by asyncio.run
		while not shutdown:
			data = await loop.sock_recv(client_socket, 1024)
			if not data:
				break  # Client disconnected
			req_data = data.decode()
			# print(f"Received from {client_address}: {data.decode()}")
			request_lines = req_data.split("\r\n")
			method_resource_protocol_triple = request_lines[0].split(" ")
			# TODO: Bunch of error checking here.
			resource = method_resource_protocol_triple[1]  # GET /whatever.html HTTP/1.1
			filename = resource.split("/")[-1]
			if filename in served_files:
				content_type, filedata = served_files[filename]
				http_response = (
					"HTTP/1.0 200 OK\r\n"
					f"Content-Type: {content_type}; charset=utf-8\r\n"
					f"Content-Length: {len(filedata)}\r\n"
					"\r\n"
					f"{filedata}"
				)
			else:
				print(f"Couldn't find {filename}")
				http_response = (
					"HTTP/1.0 404 OK\r\n"
					"Content-Type: text/plain; charset=utf-8\r\n"
					"Content-Length: 9\r\n"
					"\r\n"
					"Not found"
				)
			await loop.sock_sendall(client_socket, http_response.encode())
	except Exception as e:
		print(f"Error with client {client_address}: {e}")
	finally:
		print(f"Closing connection to {client_address}")
		client_socket.close()


if __name__ == "__main__":
	try:  # Run the server
		asyncio.run(start_server(serve_http_pages, "127.0.0.1", 8080))
	except KeyboardInterrupt:
		print("Server shut down")