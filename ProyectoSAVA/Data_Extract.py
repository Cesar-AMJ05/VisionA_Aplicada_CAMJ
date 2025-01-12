import requests
from bs4 import BeautifulSoup
import numpy as np
import cv2
import base64

class requestData:
    def __init__(self, url):
        """
        Inicializacion de la clase
        Args:
            url (str): Localizador URL del usuario
        """
        self.url = url
        self.data_user = []
        self.img_user = []
        self.htmlresquest = None
    
    def requestURL(self):
        """
        Verifica si el URL es valid mediante un codigo de estado
        Returns:
           imagen (obj): Imagen del usuario recuperada del URL
           metadata (array) : Datos del usuario
        """
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                print("Status URL -> OK")
                self.htmlresquest = response
                imagen, metadata = self.Metadata_Extraction()
                return imagen, metadata
            else:
                print(f"URL Invalid -> Status Code {response.status_code}")
                exit()
        except requests.exceptions.RequestException as e:
            print(f"Error al intentar acceder al enlace: {e}")
        return None
       
        
    def Metadata_Extraction(self):
        """
        Extre la informacion e imagen de usuario obtenida del URL del codigo QR leido, mediante las 
        etiquetas en HTML
        Returns:
           imagen (obj): Imagen del usuario recuperada del URL
           metadata (array) : Datos del usuario
        """
        
        # Objeto BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(self.htmlresquest.content, 'html.parser')
        # Datos (texto) a extraer
        class_find = ['nombre', 'boleta', 'carrera', 'escuela']
        metadata = []
        # Extraemos y guardamos los datos en arreglo
        for class_name in class_find:
            elements = soup.find_all('div', class_=class_name)
            for element in elements:
                metadata.append(element.get_text(strip=True))
        # Buscamos todas las imágenes
        img_tags = soup.find_all('img')
        # Elegir la segunda imagen (índice 1)
        if len(img_tags) > 1:
            desired_img = img_tags[1]  # Índice de la imagen
            src = desired_img.get('src')  # Tipo de imagen
            if src.startswith('data:image'): 
                imagen_base64 = src.split(',')[1]
                image_data = base64.b64decode(imagen_base64)
                image_array = np.frombuffer(image_data, dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            elif src.startswith('http'):
                print(f"La imagen es una URL: {src}")
        else:
            print("No se encontraron suficientes imágenes.")
        return image, metadata
        
        
#! Ejemplo de uso       
# url = 'https://servicios.dae.ipn.mx/vcred/?h=b1cec1faf437bc8750d23220714efc2f37505d521b1f83b35708db4a97bb89b'       
# qr_data = requestData(url)

# img, metadata = qr_data.requestURL()

# print(metadata)
# cv2.imshow('Imagen', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()