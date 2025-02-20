import socket
import json
import os
import sys
import threading
import tkinter as tk
import tkinter.scrolledtext as st


def load_client_config(config_path='client_config_sample.json'):
    """
    Carga la configuración de conexión (host y puerto) desde un archivo JSON.
    """
    if not os.path.exists(config_path):
        print(f"[ERROR] Client configuration file '{config_path}' not found.")
        sys.exit(1)
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            # Validar campos requeridos
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


class ChatClientGUI:
    def __init__(self, master):
        """
        Inicializa la ventana principal y configura los widgets.
        """
        self.master = master
        self.master.title("Cliente Chat (Ejemplo)")

        # Configurar la sección de mensajes
        self.txt_display = st.ScrolledText(master, wrap=tk.WORD, width=50, height=15, state='disabled')
        self.txt_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Campo de entrada de texto
        self.entry_message = tk.Entry(master, width=40)
        self.entry_message.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Botón para enviar
        self.btn_send = tk.Button(master, text="Enviar", command=self.send_message)
        self.btn_send.grid(row=1, column=1, padx=10, pady=5, sticky="e")

        # Opcional: Botón para conectar (puedes conectar automáticamente en __init__ si prefieres)
        self.btn_connect = tk.Button(master, text="Conectar al servidor", command=self.connect_to_server)
        self.btn_connect.grid(row=2, column=0, columnspan=2, pady=5)

        # Variables de socket y thread
        self.client_socket = None
        self.receive_thread = None
        self.is_connected = False

    def connect_to_server(self):
        """
        Conecta con el servidor usando la configuración cargada.
        """
        if self.is_connected:
            self.append_message("[INFO] Ya estás conectado al servidor.")
            return

        config = load_client_config()  # Cargar la config (server_host, server_port)
        SERVER_HOST = config['server_host']
        SERVER_PORT = config['server_port']

        self.append_message(f"[CONECTANDO] Intentando conectar a {SERVER_HOST}:{SERVER_PORT}...")

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            self.is_connected = True
            self.append_message(f"[CONECTADO] Conectado al servidor en {SERVER_HOST}:{SERVER_PORT}")

            # Iniciar hilo para recibir mensajes
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()

        except ConnectionRefusedError:
            self.append_message(f"[ERROR] No se pudo conectar con el servidor en {SERVER_HOST}:{SERVER_PORT}.")
        except socket.gaierror:
            self.append_message(f"[ERROR] Dirección de servidor inválida: {SERVER_HOST}.")
        except Exception as e:
            self.append_message(f"[ERROR] Ocurrió un error inesperado al conectar: {e}")

    def receive_messages(self):
        """
        Hilo que recibe mensajes del servidor y los muestra en el área de texto.
        """
        while self.is_connected:
            try:
                response = self.client_socket.recv(1024)
                if not response:
                    self.append_message("[DESCONECTADO] El servidor cerró la conexión.")
                    self.is_connected = False
                    break
                decoded_msg = response.decode('utf-8')
                self.append_message(f"[SERVIDOR] {decoded_msg}")
            except OSError:
                # Esto ocurre cuando el socket se cierra desde el lado del cliente.
                break
            except Exception as e:
                self.append_message(f"[ERROR] Error recibiendo mensaje: {e}")
                break

    def send_message(self):
        """
        Envía el mensaje ingresado en el Entry al servidor.
        """
        if not self.is_connected:
            self.append_message("[INFO] No estás conectado. Conéctate antes de enviar mensajes.")
            return

        message = self.entry_message.get()
        if message.strip() == '':
            return  # Ignorar mensajes vacíos

        # Enviar mensaje al servidor
        try:
            self.client_socket.sendall(message.encode('utf-8'))
            # Mostrar tu propio mensaje en la ventana (opcional)
            self.append_message(f"[TÚ] {message}")
        except Exception as e:
            self.append_message(f"[ERROR] No se pudo enviar el mensaje: {e}")

        self.entry_message.delete(0, tk.END)  # Limpiar el campo de entrada

    def append_message(self, msg):
        """
        Inserta un mensaje en la ventana de texto de forma segura.
        """
        self.txt_display.config(state='normal')
        self.txt_display.insert(tk.END, msg + "\n")
        self.txt_display.config(state='disabled')
        self.txt_display.see(tk.END)  # Auto-scroll hacia el final

    def close_connection(self):
        """
        Cierra la conexión y la ventana.
        """
        self.is_connected = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.master.destroy()


def main():
    root = tk.Tk()
    app = ChatClientGUI(root)
    # Hook para capturar el cierre de la ventana
    root.protocol("WM_DELETE_WINDOW", app.close_connection)
    root.mainloop()


if __name__ == "__main__":
    main()
