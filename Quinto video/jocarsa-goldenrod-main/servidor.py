import socket
import threading
import json
import os
import sys

def load_server_config(config_path='server_config_sample.json'):
    if not os.path.exists(config_path):
        print(f"[ERROR] Server configuration file '{config_path}' not found.")
        sys.exit(1)
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            # Validate required fields
            required_fields = ['host', 'port', 'message_file']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing '{field}' in server configuration.")
            return config
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse '{config_path}': {e}")
        sys.exit(1)
    except ValueError as ve:
        print(f"[ERROR] {ve}")
        sys.exit(1)

def handle_client(conn, addr, message_file):
    print(f"[NEW CONNECTION] {addr} connected.")
    with conn:
        try:
            while True:
                data = conn.recv(1024)  # Receive data from client
                if not data:
                    break  # No more data, client has closed the connection
                message = data.decode('utf-8')
                print(f"[RECEIVED] {addr}: {message}")

                # Save the message to a text file
                with open(message_file, 'a') as file:
                    file.write(f"{addr}: {message}\n")

                # Prepare and send a response back to the client
                response = f"Server received your message: {message}"
                conn.sendall(response.encode('utf-8'))
        except ConnectionResetError:
            print(f"[DISCONNECTED] {addr} connection was reset.")
    print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    # Load server configuration
    config = load_server_config()

    HOST = config['host']
    PORT = config['port']
    MESSAGE_FILE = config['message_file']

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # Allow reuse of the address
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the address and port
        try:
            server.bind((HOST, PORT))
        except socket.error as e:
            print(f"[ERROR] Failed to bind to {HOST}:{PORT}: {e}")
            sys.exit(1)
        server.listen()
        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        while True:
            # Wait for a new client connection
            conn, addr = server.accept()
            # Handle the client connection in a new thread
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, MESSAGE_FILE))
            client_thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start_server()
