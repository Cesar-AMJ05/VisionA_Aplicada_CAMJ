# Import the Gtts module for text  
# to speech conversion 
from gtts import gTTS 
  
# import Os module to start the audio file
import os 
  
mytext = 'Escanea el codigo QR, despues el reconocimento facial'
  
# Language we want to use 
language = 'es'

myobj = gTTS(text=mytext, lang=language , tld='com.mx', slow=False) 
  
myobj.save("init.mp3") 
  
# Play the converted file 
os.system("start init.mp3") 