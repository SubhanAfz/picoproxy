import threading
from flask import Flask, request
import socket

# Flask app
app = Flask(__name__)

# List to keep track of connected socket clients
clients = {}

# Function to handle the Flask server
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Broadcast message to all connected socket clients
def send_wake(username):
    for client in clients:
            try:
                client[username].send("wake".encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to client: {e}")
                clients.remove(client)

def handle_client(client_socket, username):
    """
    Handles a single client connection by listening for messages and responding
    if needed.

    Parameters:
    client_socket (socket.socket): The socket object for the client connection
    username (str): The username of the client

    Returns:
    None
    """
    
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print(f"Client {username} disconnected")
                break
            # Handle 'keep_alive' or other messages if needed
            message = data.decode('utf-8')
            if message == 'keep_alive':
                print(f"Received keep_alive from {username}")
        except Exception as e:
            print(f"Error with client {username}: {e}")
            break
    client_socket.close()
    del clients[username]


# Flask route to receive POST request
@app.route('/wake/<username>', methods=['POST'])
def wake_clients(username):
    if request.method == 'POST':
        print("Received wake request from Flask!")
        send_wake(username)
        return "Message broadcasted to all clients", 200

# Function to handle the socket server
def socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 6000))
    server_socket.listen(5)

    print("Socket server started and listening on port 6000...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Client {client_address} connected")
        username = client_socket.recv(1024).decode('utf-8')
        print(f"got clients username {username}")

        clients[username] = client_socket
        #start a new thread for each client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.daemon = True
        client_thread.start()

# Main execution starts here
if __name__ == '__main__':
    # Create and start threads for both Flask and socket servers
    flask_thread = threading.Thread(target=run_flask)
    socket_thread = threading.Thread(target=socket_server)

    # Start both threads
    flask_thread.start()
    socket_thread.start()

    # Join threads to keep the main program alive
    flask_thread.join()
    socket_thread.join()
