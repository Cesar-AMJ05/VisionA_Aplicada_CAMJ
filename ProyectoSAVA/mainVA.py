import cv2
import customtkinter as ctk
from PIL import Image, ImageTk

# Configuración de la ventana principal
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Acceso con Reconocimiento Facial y QR")
        ctk.set_appearance_mode("Dark")  # Modo oscuro
        ctk.set_default_color_theme("blue")  # Tema de color
        
        # Configuración de la ventana
        self.root.geometry("800x600")
        
        # Frame para la cámara
        self.camera_frame = ctk.CTkFrame(self.root, width=640, height=480)
        self.camera_frame.grid(row=0, column=0, padx=10, pady=10)
        
        # Label para mostrar el feed de la cámara
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="")
        self.camera_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Frame para los datos recuperados
        self.data_frame = ctk.CTkFrame(self.root, width=200, height=400)
        self.data_frame.grid(row=0, column=1, padx=10, pady=10)
        
        self.data_label = ctk.CTkLabel(self.data_frame, text="Datos de la credencial", justify="left", wraplength=180)
        self.data_label.pack(padx=10, pady=10)
        
        # Botones para acciones adicionales
        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.start_button = ctk.CTkButton(self.button_frame, text="Iniciar", command=self.start_camera)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ctk.CTkButton(self.button_frame, text="Detener", command=self.stop_camera)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Inicializa la captura de video
        self.cap = None

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.update_frame()

    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.camera_label.configure(image="")

    def update_frame(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Convierte el frame a RGB y lo adapta a Tkinter
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
            
            # Llama a esta función nuevamente después de 10 ms
            self.root.after(10, self.update_frame)

# Inicializa la aplicación
if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
