# Importamos Librerías necesarias
import cv2                                                          # Procesamiento de imagenes
import customtkinter as ctk                                         # Intefaz
from PIL import Image, ImageTk                                      # Manejo de imagenes con la interfaz
from customtkinter import CTkImage                                  # Manejo de imagenes con la interfaz
from pyzbar.pyzbar import decode                                    # Decodificación de codigo QR
import requests                                                     # Uso de internet
from Data_Extract import requestData                                # Extraer datos del HTML
import face_recognition                                             # Reconocimiento de rostros
from UserFace_Recognition import UserFaceRecognition                # Reconocimientio  del rostro de usuario
import os
import time
import threading
import mediapipe as mp
import pygame

# Cargamos archivos de inicio
## Imagen de inicio (la cargamos con cv2 debido a como recuperamos la imagen con el QR) 
user_example = r"ProyectoSAVA\user_login.jpg"
img_user_example = cv2.imread(user_example)
## Imagenes de acceso
path_acces_look = "ProyectoSAVA/lock.png"
path_acces_unlook = "ProyectoSAVA/unlock.png"
## Escudo del IPN
escudo_ipn = "ProyectoSAVA/ipn_escudo.png"

# Nuestra base de datos (a futro podria usarse un sql)
data_base = r"ProyectoSAVA\Data_BaseUsers"


class App:
    def __init__(self, root):
        """_summary_
        Inicializa la interfaz, creando todos los componentes necesarios, configurar el
        frame para la camara y las banderas de estado para el proceso de acceso
        Args:
            root (obj): Raiz de la interfaz grafica
        """
        self.root = root
        self.root.title("Acceso con Reconocimiento Facial y QR")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        #Credenciales
        self.Face_check = False
        self.Credential_check = False
        self.flag_credential = False
        self.flag_face = False
        self.processing = False  
        self.id_user = ""
        self.face_in_camara = False
        self.result = None
        self.face_location = None
        self.face_in_camara = False
        self.try_angain = 0
        self.instru_audio = True
        # Configuración de la ventana
        self.root.geometry("1250x500")
        #Audios
        self.audio_acceso_correcto = r"ProyectoSAVA\Audio_Out\acceso_correcto.mp3"
        self.audio_acceso_incorrecto = r"ProyectoSAVA\Audio_Out\usuario_noindef.mp3"
        self.audio_init = r"ProyectoSAVA\Audio_Out\init.mp3"
        # Frame para la cámara
        camframe_dim = [640, 480] 
        self.camframe = ctk.CTkFrame(self.root, width=camframe_dim[0], height=camframe_dim[1])
        self.camframe.grid(row=0, column=0, padx=10, pady=10)
        
        # Label para mostrar el feed de la cámara
        self.camera_label = ctk.CTkLabel(self.camframe, text="")
        self.camera_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Frame para los datos recuperados por el QR
        #Imagen Usuario
        self.data_frame = ctk.CTkFrame(self.root)
        self.data_frame.grid(row=0, column=1, columnspan=2, pady=1)
        
        self.data_imagen = ctk.CTkLabel(self.data_frame, text="")
        self.data_imagen.pack(padx = 10, pady = 10)
        
        #Informacion de usuario
        self.data_user = ctk.CTkFrame(self.data_frame)
        self.data_user.pack(fill = "both", expand = True, padx = 10, pady =10)
        ## Nombre
        self.label_nombre = ctk.CTkLabel(self.data_user, text="Nombre: Desconocido", font=("Arial", 14))
        self.label_nombre.pack(anchor="w", pady=5)
        ## ID - Boleta
        self.label_id = ctk.CTkLabel(self.data_user, text="ID: No registrado", font=("Arial", 14))
        self.label_id.pack(anchor="w", pady=5)
        ## Carrera
        self.label_status = ctk.CTkLabel(self.data_user, text="Carrera: Desconocido", font=("Arial", 14))
        self.label_status.pack(anchor="w", pady=5)
        ##  Unidad
        self.label_unidad = ctk.CTkLabel(self.data_user, text="Unidad: Desconocido", font=("Arial", 14))
        self.label_unidad.pack(anchor="w", pady=5)
        
        #Imagen de acceso
        self.acces_img = ctk.CTkFrame(self.root)  # Ajusta las dimensiones si es necesario
        self.acces_img.place(x = 1000, y = 10 )
        #Añadimos como atributo las direcciones
        self.img_access_unlook = path_acces_unlook
        self.img_access_look = path_acces_look
        #Cargamos imagen
        acces_unlook = Image.open(self.img_access_look)
        unlook_img = CTkImage(light_image=acces_unlook, size=(100, 120))
        self.acces_img_label = ctk.CTkLabel(self.acces_img, text="", image= unlook_img)
        self.acces_img_label.place(relx=0.5, rely=0.5, anchor="center")
        self.update_img_access(self.img_access_look)
        
        # No puede faltar nuestro glorioso escudo
        self.logo_ipn = ctk.CTkFrame(self.root)  
        self.logo_ipn.place(x = 1000, y = 250 )
        path_img_escudo_ipn = Image.open(escudo_ipn)
        img_escudo_ipn = ctk.CTkImage(light_image=path_img_escudo_ipn, size=(100, 120))
        self.logo_ipn_label = ctk.CTkLabel(self.logo_ipn, text="", image=img_escudo_ipn)
        self.logo_ipn_label.place(relx=0.5, rely=0.5, anchor="center")
        self.logo_ipn_label.image = img_escudo_ipn
        
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_holistic = mp.solutions.holistic.Holistic(static_image_mode=False, model_complexity=1)
        
        
        # Inicia la captura de video
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: No se pudo abrir la cámara.")
            return
        self.update_frame()
        self.update_img_credential(img_user_example)
        self.audio_wait()

    def update_frame(self):
        """
        Recupera la imagen obtenida por la camara, pre procesa y pasa por el proceso de acceso
        mediante las banderas de estado, dependiendo del proceso la salida a la interfaz se vera modificada
        dependiendo si el proceso lo requiere
        """
        # Leer un frame de la cámara
        self.chek_flags()
        ret, frame = self.cap.read()
        if ret:
            # Hacemos una copia del frame
            frame = cv2.flip(frame, 1)
            copy_frame = frame.copy()
            temp_frame = self.face_camdetection(frame)
            frame = temp_frame.copy()
            height, width, _ = frame.shape
            
            # Verificamos las banderas
            #Primer condicion, primero la credencial
            if (self.flag_credential and not self.flag_face):
                # Dibujar cuadrado para el QR
                bottom_right_x, bottom_right_y, top_left_x, top_left_y = self.draw_qr_Square(height, width, 200)
                color = (0, 255, 0)  # Color del cuadrado
                thickness = 2  # Grosor de la línea del cuadrado
                cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), color, thickness)
                cv2.putText(frame, "Coloca el QR aqui", (top_left_x, top_left_y - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                self.ReadQr(copy_frame)
                self.audio_wait()
            
            #Segunda condicion, el rostro            
            if(self.flag_face and not self.flag_credential):
                if self.try_angain < 25:
                    if self.face_in_camara:
                        self.user_recognition(copy_frame)
                        self.try_angain +=1
                        if self.result:
                            self.Face_check = True
                            self.flag_face = False
                else:
                    self.restart_all()
                    self.play_audio(self.audio_acceso_incorrecto)
                
            
            # Ultima condicion si ambas banderas se cumplen
            if(self.Face_check and self.Credential_check):
                self.update_img_access(self.img_access_unlook)
                # Reiniciar las banderas
                #print("Flags reiniciadas")
                self.play_audio(self.audio_acceso_correcto)
                self.Credential_check = False
                self.Face_check = False
                self.restart_all()
            # Convertimos el frame a RGB y lo adaptamos a Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        #Refrescamos la camara cada 10ms
        self.root.after(10, self.update_frame)
        
        #self.root.after(180000, )
     
    def update_img_credential(self, img):
        """
        Modifica la imagen de usuario indetificado de la interfaz
        Args:
            img (obj): Imagen de usuario
        """
        # Ajustamos tamaño de la imagen
        resized_img = cv2.resize(img, (250, 275))
        rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        cv2ckt = Image.fromarray(rgb_img)
        img_ckt = ImageTk.PhotoImage(image=cv2ckt)
        # Actualiza la imagen
        self.data_imagen.configure(image=img_ckt)
        self.data_imagen.image = img_ckt  
           
    def update_img_access(self, path):
        """
        Modifica el indicador visual de que el acceso es otorgado o declinado
        Args:
            path (str): direccion de la imagen
        """
        path_image = Image.open(path)
        img = CTkImage(light_image=path_image, size=(100, 120))
        self.acces_img_label.configure(image = img)
        self.acces_img_label.image = img
        
    def update_data_labels(self, data):
        """
        Refrezfa los datos de usuario, sea el caso de que sea reconocido o su defecto reinicie el proceso
        *Ojo : El orden de los datos sera  Nombre, Boleta, Carrera, Unidad
        Args:
            data (str): Datos obtenidos del usuario
        """
   
        self.label_nombre.configure(text=f"Nombre: {data[0]}")
        self.label_id.configure(text= f"ID: {data[1]}")
        self.label_status.configure(text = f"Carrera: {data[2]}")    
        self.label_unidad.configure(text = f"Unidad: {data[3]}")
        
    def draw_qr_Square(self, height, width, size):
        """
        Genera las cordenadas del cuadrao a dibujar sobre el streamin de la camara
        para colocar el QR, mediante sus dimenciones y el tamaño ingrtesado
        Args:
            height (uint8): Altura del frame (camara)
            width (uint8): Ancho del frame (camara)
            size (uint8): Tamaño del cuadrado 

        Returns:
            _type_: _description_
        """
        # Calcula las coordenadas del cuadrado centrado
        center_x, center_y = width // 2, height // 2
        half_size = size // 2
        
        top_left_x = max(0, center_x - half_size)
        top_left_y = max(0, center_y - half_size)
        bottom_right_x = min(width, center_x + half_size)
        bottom_right_y = min(height, center_y + half_size)
        
        return bottom_right_x, bottom_right_y, top_left_x, top_left_y
        
    def ReadQr(self, frame):
        """
        Recupera la imagen de la camara para procesar si existe un codigo QR legible, en caso que lo
        indentifique realiza la decodificacion del mismo, una vez pasa por la extracion de datos
        refresca las credenciales para terminar el proceso del QR, validando el primer filtro
        Args:
            frame (objt): Imagen de la camara
        """
        try:
            # Decodificar QR usando pyzbar
            qr_codes = decode(frame)
            for qr in qr_codes:
                qr_data = qr.data.decode("utf-8")
                response = requests.get(qr_data)
            if response.status_code == 200:
                print(f"QR detectado: {qr_data}")
                qr_data = requestData(qr_data)
                img_user, metadata = qr_data.requestURL()
                #Terminamos el proceso de lectura de QR
                self.flag_credential = False
                #Hacemos check a la validaciond ela credencial
                self.Credential_check = True
                print(metadata)
                #Actualizamos la informacion en la GUI
                self.update_img_credential(img_user)
                self.update_data_labels(metadata)                
                self.id_user = metadata[1]

                
        except:
            #print("Try Again !!!")
            pass
        
    def chek_flags(self):
        """
        Verifica el estado del proceso mediante las banderas de estado
        """
        if(self.Credential_check is not  True):
            self.flag_credential = True
        
        if self.Credential_check and not self.Face_check:
            self.flag_face = True

    def search_data_base(self):
        """
        Busca en la "base de datos" si existe algún usuario registrado, regresando la dirección
        de la imagen coincidente
        Returns:
        img_user (str): Dirección de la imagen del usuario
        """
        # Dirección del usuario identificado
        img_user = None  # Empezamos con None, indicando que no hemos encontrado ninguna imagen
        
        for archivo in os.listdir(data_base):
            if self.id_user in archivo:
                img_user = os.path.join(data_base, archivo)
                break  # Salimos del bucle después de encontrar la primera coincidencia
        
        return img_user

    def user_recognition(self, frame):
        if not self.processing:  # Solo inicia si no hay un proceso activo
            time.sleep(5)
            threading.Thread(target=self.user_recognition_task, args=(frame,)).start()
    
    def user_recognition_task(self, frame):
        self.processing = True  # Marca como en proceso
        id_user_temp = self.search_data_base()  # Ruta a la imagen del usuario
        if(id_user_temp):
            identicator = UserFaceRecognition()  # Crear instancia de la clase
            identicator.array_recognition(id_user_temp)  # Procesar imagen del usuario
            self.result, self.face_location = identicator.fly_recognition(frame)  # Realizar reconocimiento en el frame actual
        else:
            self.play_audio(self.audio_acceso_incorrecto)
            self.restart_all()
    def face_camdetection(self, frame):
        # Convertimos a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Procesamos el frame con MediaPipe
        results = self.mp_holistic.process(frame_rgb)
        # Dibujamos landmarks del rostro si están disponibles
        if results.face_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, results.face_landmarks, mp.solutions.face_mesh.FACEMESH_TESSELATION,
                self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1),
                self.mp_drawing.DrawingSpec(color=(50, 50, 50), thickness=1))
        # Indicador para saber si se detectaron landmarks
        self.face_in_camara = results.face_landmarks is not None
        return frame  # Devuelve el frame actualizado
        
    def play_audio(self, path_file):
        pygame.mixer.init()  # Inicializar el mezclador de pygame
        pygame.mixer.music.load(path_file)  # Cargar el archivo de audio
        pygame.mixer.music.play()  # Reproducir el archivo de audio
            
    def restart_flags(self):
        self.Face_check = False
        self.Credential_check = False
        self.flag_credential = False
        self.flag_face = False
        self.processing = False  
        self.id_user = ""
        self.face_in_camara = False
        self.result = None
        self.face_location = None
        self.face_in_camara = False
        self.try_angain = 0
        self.instru_audio = True
    
    def restart_all(self):
        data_restart = ["Desconocido", "Desconocido", "Desconocido", "Desconocido"]
        # Iniciar las tareas de manera asíncrona
        threading.Timer(1, self.update_img_credential, args=[img_user_example]).start()
        threading.Timer(1, self.update_data_labels, args=[data_restart]).start()
        threading.Timer(3, self.restart_flags).start()
        threading.Timer(1, self.update_img_access, args=[self.img_access_look]).start()

    def audio_wait(self):
        if self.instru_audio is True:
            threading.Timer(5, self.play_audio, args=[self.audio_init]).start()
            self.instru_audio = False

        
        
# Iniciamos aplicación
if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
