import os
import sys
import tkinter as tk
from tkinter import messagebox
import GPUtil
import requests
import subprocess
import platform
import ctypes
from tkinter.ttk import Progressbar
import threading

def is_admin():
    """Verifica si el script se está ejecutando como administrador en Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

class DriverUpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Actualizador de Drivers de GPU")
        self.root.geometry("400x280")  # Tamaño aún más pequeño
        self.root.resizable(False, False)  # Deshabilitar redimensionamiento
        self.root.attributes('-toolwindow', True)  # Quitar botón de maximizar
        self.root.configure(bg="#f0f0f0")  # Fondo claro

        # Título principal
        self.title_label = tk.Label(root, text="Actualizador de Drivers de GPU", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)

        # Etiqueta de estado
        self.status_label = tk.Label(root, text="Iniciando...", font=("Arial", 10), bg="#f0f0f0")
        self.status_label.pack(pady=5)

        # Barra de progreso
        self.progress = Progressbar(root, orient=tk.HORIZONTAL, length=350, mode='determinate')
        self.progress.pack(pady=10)

        # Botón de reinicio (inicialmente oculto)
        self.restart_button = tk.Button(root, text="Reiniciar Windows", command=self.restart_windows, state=tk.DISABLED, bg="#4CAF50", fg="white", font=("Arial", 10))
        self.restart_button.pack(pady=10)

        # Programar la detección de GPU después de que la ventana se muestre
        self.root.after(100, self.start_detection)

    def update_progress(self, value, message):
        """Actualiza la barra de progreso y el mensaje de estado."""
        self.progress['value'] = value
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def start_detection(self):
        """Inicia la detección de GPU en un hilo secundario."""
        threading.Thread(target=self.detect_gpu, daemon=True).start()

    def detect_gpu(self):
        try:
            self.update_progress(10, "Detectando GPU...")
            gpus = GPUtil.getGPUs()
            if not gpus:
                raise Exception("No se detectó ninguna GPU.")

            gpu = gpus[0]
            self.gpu_name = gpu.name.lower()
            self.update_progress(20, f"GPU Detectada: {gpu.name}")

            # Determinar el fabricante de la GPU
            if "nvidia" in self.gpu_name:
                self.vendor = "nvidia"
            elif "amd" in self.gpu_name or "radeon" in self.gpu_name:
                self.vendor = "amd"
            elif "intel" in self.gpu_name:
                self.vendor = "intel"
            else:
                raise Exception("Fabricante de GPU no compatible.")

            self.update_progress(30, f"Fabricante detectado: {self.vendor.capitalize()}")
            self.download_and_install_drivers()
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def download_and_install_drivers(self):
        self.update_progress(40, f"Iniciando descarga e instalación de drivers para {self.vendor.capitalize()}...")

        try:
            if self.vendor == "nvidia":
                self.install_nvidia_drivers()
            elif self.vendor == "amd":
                self.install_amd_drivers()
            elif self.vendor == "intel":
                self.install_intel_drivers()
        except Exception as e:
            self.update_progress(0, f"Fallo al instalar los drivers: {str(e)}")
            messagebox.showerror("Error", f"Fallo al instalar los drivers: {str(e)}")

    def install_nvidia_drivers(self):
        driver_url = "https://us8-dl.techpowerup.com/files/rONndIIWJL4NNq2nQNoikw/1738380642/572.16-desktop-win10-win11-64bit-international-dch-whql.exe"
        driver_path = os.path.join(os.getcwd(), "nvidia_driver.exe")

        self.update_progress(50, "Descargando controladores de NVIDIA...")
        response = requests.get(driver_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open(driver_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded += len(chunk)
                progress_value = 50 + (downloaded / total_size) * 30  # 50% a 80%
                self.update_progress(progress_value, f"Descargando: {downloaded / 1024 / 1024:.2f} MB")

        self.update_progress(80, "Instalando controladores de NVIDIA...")
        subprocess.run([driver_path, "/s", "/noreboot"], check=True)

        os.remove(driver_path)
        self.finish_installation()

    def install_amd_drivers(self):
        driver_url = "https://us1-dl.techpowerup.com/files/8_T90HM-leWw5KzLkv_0OA/1738380713/whql-amd-software-adrenalin-edition-24.12.1-win10-win11-dec-rdna.exe"
        driver_path = os.path.join(os.getcwd(), "amd_driver.exe")

        self.update_progress(50, "Descargando controladores de AMD...")
        response = requests.get(driver_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open(driver_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded += len(chunk)
                progress_value = 50 + (downloaded / total_size) * 30  # 50% a 80%
                self.update_progress(progress_value, f"Descargando: {downloaded / 1024 / 1024:.2f} MB")

        self.update_progress(80, "Instalando controladores de AMD...")
        subprocess.run([driver_path, "/S"], check=True)

        os.remove(driver_path)
        self.finish_installation()

    def install_intel_drivers(self):
        driver_url = "https://us8-dl.techpowerup.com/files/QA_8mUFsJ0jhvTpYqaIBUg/1738380757/gfx_win_101.6458_101.6257.exe"
        driver_path = os.path.join(os.getcwd(), "intel_driver.exe")

        self.update_progress(50, "Descargando controladores de Intel...")
        response = requests.get(driver_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open(driver_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded += len(chunk)
                progress_value = 50 + (downloaded / total_size) * 30  # 50% a 80%
                self.update_progress(progress_value, f"Descargando: {downloaded / 1024 / 1024:.2f} MB")

        self.update_progress(80, "Instalando controladores de Intel...")
        subprocess.run([driver_path, "/silent"], check=True)

        os.remove(driver_path)
        self.finish_installation()

    def finish_installation(self):
        self.update_progress(100, "Instalación completada.")
        self.restart_button.config(state=tk.NORMAL)

    def restart_windows(self):
        result = messagebox.askyesno("Reiniciar", "¿Deseas reiniciar Windows ahora?")
        if result:
            subprocess.run(["shutdown", "/r", "/t", "0"])

if __name__ == "__main__":
    # Verificar si el script se ejecuta como administrador
    if not is_admin():
        messagebox.showerror("Error", "Este programa debe ejecutarse como administrador.")
        sys.exit(1)

    root = tk.Tk()
    app = DriverUpdaterApp(root)
    root.mainloop()
