import threading
import cv2
from UserFace_Recognition import UserFaceRecognition  # Importa la clase externa

class MyApp:
    def __init__(self):
        self.processing = False  # Controla si hay un hilo en ejecución
        self.result = None  # Resultado del reconocimiento
        self.face_location = None  # Ubicación del rostro
        self.identicator = UserFaceRecognition()  # Instancia de la clase externa

    def user_recognition_task(self, frame):
        """
        Función ejecutada en un hilo separado para realizar el reconocimiento facial.
        """
        self.processing = True  # Indica que el proceso está en curso
        try:
            id_user_temp = self.search_data_base()  # Ruta a la imagen del usuario
            self.identicator.array_recognition(id_user_temp, frame)  # Procesar imagen del usuario
            self.result, self.face_location = self.identicator.fly_recognition(frame)  # Realizar reconocimiento en el frame actual
        except Exception as e:
            print(f"Error en el reconocimiento facial: {e}")
            self.result, self.face_location = None, None
        finally:
            self.processing = False  # Finaliza el proceso

    def user_recognition(self, frame):
        """
        Inicia el hilo del reconocimiento facial si no está en curso.
        """
        if not self.processing:  # Solo inicia si no hay un proceso activo
            threading.Thread(target=self.user_recognition_task, args=(frame,)).start()

    def update_ui(self, frame):
        """
        Actualiza la interfaz gráfica con los resultados del reconocimiento.
        """
        if self.result is not None:
            if self.result:
                text = "Usuario reconocido"
                color = (125, 220, 0)
            else:
                text = "Desconocido"
                color = (50, 50, 255)

            if self.face_location:
                top, right, bottom, left = self.face_location
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, text, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Reconocimiento Facial", frame)

    def search_data_base(self):
        """
        Método simulado para buscar la ruta a la imagen del usuario.
        """
        return r"ProyectoSAVA\Data_BaseUsers\2020680111.jpeg"

    def run(self):
        """
        Bucle principal de la aplicación.
        """
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            # Llama al reconocimiento en segundo plano
            self.user_recognition(frame)

            # Actualiza la interfaz con los resultados
            self.update_ui(frame)

            if cv2.waitKey(1) & 0xFF == 27:  # Salir con la tecla ESC
                break

        cap.release()
        cv2.destroyAllWindows()
