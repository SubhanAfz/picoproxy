import threading
from flask import Flask, request
import socket

# Flask app
app = Flask(__name__)

# List to keep track of connected socket clients
clients = []

# Function to handle the Flask server
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Broadcast message to all connected socket clients
def send_wake(username):
    for client in clients:
        if client["username"] == username:
            try:
                client["socket"].send("wake".encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to client: {e}")
                clients.remove(client)

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

        client_dic = {
            "username": username,
            "socket": client_socket
        }

        clients.append(client_dic)

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
