import os
import csv
import socket
import threading
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set the path to the data folder
data_folder = os.path.join(os.path.dirname(__file__), 'data')

# Set the path to the dataset.csv file
dataset_file = os.path.join(data_folder, 'dataset.csv')

# Define the TCP/IP server configuration
SERVER_HOST = '127.0.0.1'  # Replace with your desired server IP
SERVER_PORT = 9011  # Replace with your desired server port

# Create a lock to synchronize access to the dataset
data_lock = threading.Lock()

# Create a list to store the latest dataset
latest_data = []


def load_dataset():
    """Load data from the dataset.csv file."""
    global latest_data

    with open(dataset_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        latest_data = list(csv_reader)


def handle_client(client_socket):
    """Handle a client connection."""
    while True:
        # Receive a single byte packet from the client
        packet = client_socket.recv(1)

        if packet:
            # Acquire the data lock to access the dataset
            with data_lock:
                # Send the latest dataset to the client
                response = jsonify(latest_data)
                client_socket.sendall(response.encode())

    client_socket.close()


def start_server():
    """Start the TCP/IP server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()

    print(f'Server listening on {SERVER_HOST}:{SERVER_PORT}')

    while True:
        client_socket, client_address = server_socket.accept()
        print(f'Client connected: {client_address}')

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


# Route to fetch the latest dataset
@app.route('/', methods=['GET'])
def get_data():
    return jsonify(latest_data)


if __name__ == '__main__':
    # Load the dataset from the CSV file
    load_dataset()

    # Start the TCP/IP server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Run the Flask application
    app.run(debug=True)
