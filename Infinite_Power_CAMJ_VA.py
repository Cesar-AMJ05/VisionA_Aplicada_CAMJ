#Importamos librerias 🤯
import cv2
import mediapipe as mp

# Iniciamos metodos de dibujo y de modelo del MediaPipe 😈
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

#Cargamos el video de entrada 🥵
cap = cv2.VideoCapture(r"Tarea_06\prueba1.mp4")

#Nombre del archio de salida 🎥
output_video = "procesado1.mp4"

# Obtener propiedades del video original 🎞
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
# Empleamos un codec para guardar el video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  

# Creamos el objeto VideoWriter para guardar el video procesado 📽
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

#Iniciamos el modelo de Holistic para generar los puntos  (LandMarks)✏ 
with mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1) as holistic:

    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        #Pasamos a espacio de color RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)

        # Landmarks del Rostro 👩‍🦲
        mp_drawing.draw_landmarks(
            frame, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION,
            mp_drawing.DrawingSpec(color=(255, 0, 75), thickness=1, circle_radius=1),
            mp_drawing.DrawingSpec(color=(255, 255, 185), thickness=2))
          
          # Landmarks del Mano izquierda (amarillo)💪
        mp_drawing.draw_landmarks(
            frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(230, 255, 0), thickness=2, circle_radius=1),
            mp_drawing.DrawingSpec(color=(120, 120, 120), thickness=2))
          
          # Landmarks del Mano derecha (azul)💪
        mp_drawing.draw_landmarks(
            frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(240, 255, 5), thickness=2, circle_radius=1),
            mp_drawing.DrawingSpec(color=(120, 120, 120), thickness=2))
          
          # # Landmarks de la Postura (verde) 🧍‍♂️
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(5, 250, 70), thickness=2, circle_radius=1),
            mp_drawing.DrawingSpec(color=(240, 240, 240), thickness=2))
        #Mostramos el frame procesado
        frame = cv2.flip(frame, 1)
        out.write(frame)  # Escribir el frame procesado en el archivo de salida
        #Invertimos valores para prueba 1 o 2 (debido a las propiedades de video)
        cv2.imshow("Frame", cv2.resize(frame, (480,720), interpolation =cv2.INTER_LINEAR))
        #Salida de panico (ESC) 😨
        if cv2.waitKey(1) & 0xFF == 27:
            break

#Inicismos el proceso
cap.release()
out.release()
cv2.destroyAllWindows()