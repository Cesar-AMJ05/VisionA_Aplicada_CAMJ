import cv2
import face_recognition

class UserFaceRecognition:
    def __init__(self):
        pass
    
    def array_recognition(self, img_user_id):
        try:
            # Cargamos la imagen del usuario a identificar
            img = cv2.imread(img_user_id)
            # Detectamos la ubicación del rostro
            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                raise ValueError("No se detectaron rostros en la imagen del usuario.")
            
            face_loc = face_locations[0]
            # Obtenemos las codificaciones del rostro
            self.face_img_encodings = face_recognition.face_encodings(img, known_face_locations=[face_loc])[0]
        except Exception as e:
            print(f"Error al procesar la imagen del usuario: {e}")
            self.face_img_encodings = None
            
    def fly_recognition(self, frame):
        # Validamos si la codificación del usuario está cargada
        if self.face_img_encodings is None:
            print("No se puede realizar el reconocimiento, codificación facial no válida.")
            return None, None  # Retorna None si la codificación no es válida

        # Detectamos rostros en el frame
        face_locations = face_recognition.face_locations(frame, model="hog")
        if not face_locations:
            print("No se detectaron rostros en el frame.")
            return None, None  # Retorna None si no hay rostros detectados

        # Procesamos cada rostro detectado
        for face_location in face_locations:
            # Obtenemos las codificaciones del rostro detectado
            face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]
            # Comparamos con el rostro del usuario
            result = face_recognition.compare_faces([self.face_img_encodings], face_frame_encodings)
            print("Result:", result)
            
            if result[0] == True:
                return result, face_location  # Retorna el resultado y la ubicación si hay coincidencia

        return None, None  # Retorna None si no hay coincidencia



#! Ejemplo de uso
# # # Pruebas
# img_prueba = cv2.imread(r"ProyectoSAVA\prueba_re.jpg")
# # #img_prueba = cv2.imread(r"ProyectoSAVA\prueba_otro.jpg")
# img_prueba = cv2.resize(img_prueba, (640, 360))

# img_path = r"ProyectoSAVA\Data_BaseUsers\2020680111.jpeg"

# prueba = UserFaceRecognition()
# prueba.array_recognition(img_path)
# prueba.fly_recognition(img_prueba)
