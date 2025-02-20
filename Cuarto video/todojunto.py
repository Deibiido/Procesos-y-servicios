import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import psutil
import time
import os

# ========================
# Función para detener Apache
# ========================
def stop_apache():
    try:
        # Ajusta la ruta al ejecutable de Apache según tu instalación
        apache_bin_path = r"C:\Apache24\bin\httpd.exe"
        subprocess.run([apache_bin_path, "-k", "stop"], check=True)
        messagebox.showinfo("Éxito", "Apache se ha detenido correctamente.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "No se pudo detener Apache. Verifica la ruta o los permisos.")

# ========================
# Función para apagar la máquina
# ========================
def shutdown_machine():
    respuesta = messagebox.askyesno("Apagar equipo", "¿Estás seguro de que deseas apagar el equipo?")
    if respuesta:
        try:
            # En Windows, /s apaga el sistema y /t 0 lo hace inmediatamente
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"No se pudo apagar la máquina: {e}")

# ========================
# Función para mostrar puertos abiertos (Resultado en consola)
# ========================
def get_open_ports():
    open_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN':
            open_ports.append((conn.laddr.ip, conn.laddr.port))
    if open_ports:
        ports_str = "Puertos abiertos:\n" + "\n".join(f"{ip}:{port}" for ip, port in open_ports)
    else:
        ports_str = "No se encontraron puertos abiertos o no se tienen permisos suficientes."
    
    # En lugar de mostrar en ventana emergente, lo imprimimos en la consola
    print(ports_str)

# ========================
# Función para bloquear un puerto
# (requiere sudo/permisos de admin en Linux)
# ========================
def block_port():
    # Pedir al usuario el puerto e IP
    port = simpledialog.askstring("Bloquear puerto", "Ingresa el puerto que deseas bloquear:")
    if not port:
        return  # Usuario canceló
    ip = simpledialog.askstring("Bloquear puerto", "Ingresa la IP a bloquear (deja vacío para todas):")
    if ip is None:
        ip = ""  # Usuario canceló o dejó vacío
    
    # Validar que sea numérico
    if not port.isdigit():
        messagebox.showerror("Error", "Número de puerto no válido. Debes ingresar un número.")
        return

    # Construir comando de iptables
    if ip:
        command = f"sudo iptables -A INPUT -p tcp --dport {port} -s {ip} -j DROP"
    else:
        command = f"sudo iptables -A INPUT -p tcp --dport {port} -j DROP"

    # Ejecutar iptables
    try:
        subprocess.run(command, shell=True, check=True)
        messagebox.showinfo("Éxito", f"Puerto {port} bloqueado correctamente{' para IP ' + ip if ip else ''}.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se pudo bloquear el puerto: {e}\n¿Tienes privilegios de sudo/admin?")

# ========================
# Función para monitorear el uso de red (Resultado en consola)
# ========================
def monitor_network_usage():
    """
    - Si no existe el archivo 'red.txt', calcula valores promedio de subida/descarga por 10 segundos
      y los guarda en el archivo.
    - Si existe, compara el uso actual con los valores almacenados para detectar anomalías.
    - Imprime la información en la consola en lugar de mostrar una ventana emergente.
    """
    interval = 1
    archivo_ruta = "red.txt"

    def get_network_usage(intervalo):
        """Calcula bytes subidos y descargados en 'intervalo' segundos."""
        initial_net_io = psutil.net_io_counters()
        time.sleep(intervalo)
        net_io = psutil.net_io_counters()
        subida_calc = (net_io.bytes_sent - initial_net_io.bytes_sent) / intervalo
        descarga_calc = (net_io.bytes_recv - initial_net_io.bytes_recv) / intervalo
        return subida_calc, descarga_calc

    if not os.path.exists(archivo_ruta):
        # Calcular valores promedio de 10 segundos
        total_subida = 0
        total_descarga = 0

        for _ in range(10):
            s, d = get_network_usage(interval)
            total_subida += s
            total_descarga += d

        subida = total_subida / 10
        descarga = total_descarga / 10

        with open(archivo_ruta, 'w') as f:
            f.write(f"{subida},{descarga}")

        print(
            f"[Monitor de red] Se calcularon valores de referencia:\n"
            f"   - Subida promedio: {subida:.2f} bytes/s\n"
            f"   - Descarga promedio: {descarga:.2f} bytes/s\n"
            f"Se guardaron en {archivo_ruta}."
        )
    else:
        with open(archivo_ruta, 'r') as f:
            linea = f.readline()

        partido = linea.split(",")
        try:
            subida_ref = float(partido[0])
            descarga_ref = float(partido[1])
        except (IndexError, ValueError):
            print(f"[Monitor de red] Error: El archivo {archivo_ruta} está dañado o es inválido.")
            return

        previous_net_io = psutil.net_io_counters()
        time.sleep(interval)
        current_net_io = psutil.net_io_counters()

        nuevasubida = (current_net_io.bytes_sent - previous_net_io.bytes_sent) / interval
        nuevadescarga = (current_net_io.bytes_recv - previous_net_io.bytes_recv) / interval

        # Verificar anomalías (umbral x15 en este ejemplo)
        if nuevasubida > subida_ref * 15 or nuevadescarga > descarga_ref * 15:
            print(
                f"[Monitor de red] ¡Anomalía detectada!\n"
                f"   - Subida actual: {nuevasubida:.2f} bytes/s (Referencia: {subida_ref:.2f})\n"
                f"   - Descarga actual: {nuevadescarga:.2f} bytes/s (Referencia: {descarga_ref:.2f})"
            )
        else:
            print(
                f"[Monitor de red] Uso normal.\n"
                f"   - Subida actual: {nuevasubida:.2f} bytes/s (Referencia: {subida_ref:.2f})\n"
                f"   - Descarga actual: {nuevadescarga:.2f} bytes/s (Referencia: {descarga_ref:.2f})"
            )

# ========================
# Creación de la ventana principal
# ========================
def main():
    ventana = tk.Tk()
    ventana.title("Aplicación de Utilidades")
    ventana.minsize(400, 300)

    # Botón para detener Apache
    btn_stop_apache = tk.Button(ventana, text="Detener Apache", command=stop_apache)
    btn_stop_apache.pack(pady=10)

    # Botón para apagar el equipo
    btn_shutdown = tk.Button(ventana, text="Apagar equipo", command=shutdown_machine)
    btn_shutdown.pack(pady=10)

    # Botón para mostrar puertos abiertos (imprime resultado en consola)
    btn_open_ports = tk.Button(ventana, text="Mostrar puertos abiertos", command=get_open_ports)
    btn_open_ports.pack(pady=10)

    # Botón para bloquear un puerto
    btn_block_port = tk.Button(ventana, text="Bloquear un puerto", command=block_port)
    btn_block_port.pack(pady=10)

    # Botón para monitorizar uso de red (imprime resultado en consola)
    btn_monitor_network = tk.Button(ventana, text="Monitorear uso de red", command=monitor_network_usage)
    btn_monitor_network.pack(pady=10)

    ventana.mainloop()

if __name__ == "__main__":
    main()
