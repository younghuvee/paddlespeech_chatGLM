import sounddevice as sd
from scipy.io.wavfile import write

import pygame
pygame.mixer.init()

print("loading asr and tts ... ...")
from paddlespeech.cli.asr.infer import ASRExecutor
from paddlespeech.cli.tts.infer import TTSExecutor
# recognizer = sr.Recognizer()
asr = ASRExecutor()
tts = TTSExecutor()
print("loading asr and tts success!")




while True:

    xx = input("Enter some text that you want to speak >")


    tts(text=xx, output="output.wav")
    
    pygame.mixer.music.load('output.wav')  
    pygame.mixer.music.set_volume(0.5) 
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # 在音频播放为完成之前不退出程序
        pass
    # os.remove("./output.wav")
    pygame.mixer.music.unload()
