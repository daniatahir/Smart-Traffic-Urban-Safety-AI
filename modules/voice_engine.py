import os
from gtts import gTTS
from pygame import mixer
import time

# Audio initialize karein
mixer.init()

def play_warning(text):
    filename = "warning.mp3"
    # Text ko voice mein convert karein
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    
    # Play karein
    mixer.music.load(filename)
    mixer.music.play()
    
    # Jab tak play ho raha hai wait karein (optional)
    while mixer.music.get_busy():
        time.sleep(0.1)
    
    # File release karein taaki delete ho sake
    mixer.music.unload()
    if os.path.exists(filename):
        os.remove(filename)

# Test function
# play_warning("Warning! Accident risk detected.")