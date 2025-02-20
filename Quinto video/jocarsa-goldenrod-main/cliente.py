import socket
import json
import os
import sys

def load_client_config(config_path='client_config_sample.json'):
    if not os.path.exists(config_path):
        print(f"[ERROR] Client configuration file '{config_path}' not found.")
        sys.exit(1)
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            # Validate required fields
            required_fields = ['server_host', 'server_port']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing '{field}' in client configuration.")
            return config
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse '{config_path}': {e}")
        sys.exit(1)
    except ValueError as ve:
        print(f"[ERROR] {ve}")
        sys.exit(1)

def start_client():
    # Load client configuration
    config = load_client_config()

    SERVER_HOST = config['server_host']
    SERVER_PORT = config['server_port']

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            # Connect to the server
            client.connect((SERVER_HOST, SERVER_PORT))
            print(f"[CONNECTED] Connected to server at {SERVER_HOST}:{SERVER_PORT}")

            while True:
                # Get user input
                message = input("Enter message to send (type 'exit' to quit): ")
                if message.lower() == 'exit':
                    print("[DISCONNECTING] Disconnecting from the server.")
                    break

                # Send the message to the server
                client.sendall(message.encode('utf-8'))

                # Wait for the server's response
                response = client.recv(1024)
                if not response:
                    print("[DISCONNECTED] Server closed the connection.")
                    break

                # Decode and print the response
                print(f"Server response: {response.decode('utf-8')}")

        except ConnectionRefusedError:
            print(f"[ERROR] Could not connect to server at {SERVER_HOST}:{SERVER_PORT}. Is the server running?")
        except socket.gaierror:
            print(f"[ERROR] Invalid server address: {SERVER_HOST}")
        except KeyboardInterrupt:
            print("\n[EXIT] Client terminated by user.")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    start_client()
