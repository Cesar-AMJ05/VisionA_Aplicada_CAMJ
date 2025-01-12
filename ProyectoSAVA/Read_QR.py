from pyzbar.pyzbar import decode
import cv2
import requests
from Data_Extract import requestData

def lector_qr_rapido():
    cap = cv2.VideoCapture(0)
    # Esperar algún QR
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)  # Voltear horizontalmente
        # Crear una copia del frame 
        copyframe = frame.copy()
        
        #Dimenciones
        height, width, _ = frame.shape
        # Coordenadas del cuadrado
        square_size = 200  # Tamaño del cuadrado 
        top_left_x = (width - square_size) // 2
        top_left_y = (height - square_size) // 2
        bottom_right_x = top_left_x + square_size
        bottom_right_y = top_left_y + square_size

        # Dibujar el cuadrado en la imagen
        color = (0, 255, 0)  # Color del cuadrado 
        thickness = 2  # Grosor de la línea del cuadrado
        cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), color, thickness)
        cv2.putText(frame, "Coloca el QR aqui",
                    (top_left_x, top_left_y-20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        try :    
            # Decodificar QR usando pyzbar
            qr_codes = decode(copyframe)
        except:
            print("Coloca bien el QR perra")
        for qr in qr_codes:
            qr_data = qr.data.decode("utf-8")
            response = requests.get(qr_data)
            if response.status_code == 200:
                print(f"QR detectado: {qr_data}")
                qr_data = requestData(qr_data)
                img, metadata = qr_data.requestURL()
                print(metadata)
                cv2.imshow('Imagen', img)
            else:
                print("Escanea otra vez!")
        cv2.imshow("Lector QR", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

lector_qr_rapido()
