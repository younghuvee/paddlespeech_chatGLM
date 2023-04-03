import requests
import json
import sounddevice as sd
from scipy.io.wavfile import write
import pyaudio
import numpy as np
from scipy import fftpack
import wave
import os

import pygame
pygame.mixer.init()

print("loading asr and tts ... ...")
from paddlespeech.cli.asr.infer import ASRExecutor
from paddlespeech.cli.tts.infer import TTSExecutor
# recognizer = sr.Recognizer()
asr = ASRExecutor()
tts = TTSExecutor()
print("loading asr and tts success!")

# http://portaudio.com/docs/v19-doxydocs/compile_linux.html
def recording(filename, time=0, threshold=3000):
    """
    :param filename: 文件名
    :param time: 录音时间,如果指定时间，按时间来录音，默认为自动识别是否结束录音
    :param threshold: 判断录音结束的阈值
    :return:
    """
    CHUNK = 1024  
    FORMAT = pyaudio.paInt16  
    CHANNELS = 1  
    RATE = 16000  
    RECORD_SECONDS = time 
    WAVE_OUTPUT_FILENAME = filename 
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("* listening...")
    frames = []
    if time > 0:
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
    else:
        stopflag = 0
        stopflag2 = 0
        while True:
            data = stream.read(CHUNK)
            rt_data = np.frombuffer(data, np.dtype('<i2'))
            # print(rt_data*10)
     
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]

            # print(sum(fft_data) // len(fft_data))


            if sum(fft_data) // len(fft_data) > threshold:
                stopflag += 1
            else:
                stopflag2 += 1
            oneSecond = int(RATE / CHUNK)
            if stopflag2 + stopflag > oneSecond:
                if stopflag2 > oneSecond // 3 * 2:
                    break
                else:
                    stopflag2 = 0
                    stopflag = 0
            frames.append(data)
    print("* end")
    stream.stop_stream()
    stream.close()
    p.terminate()
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))





while True:

    print("Say something please ...")
    xx = input("start ? (Enter)")
    # audio = recognizer.listen(source)
    # recording("middle.wav", time=5)  
    recording("middle.wav")  

    result = asr(audio_file="./middle.wav")
    print("You said : {}".format(result))
    res = requests.post(url='http://xxx.xxx.xxx.xxx:xxxx',
    headers={"Content-Type": "application/json"},
    json={"prompt":result,"history": []})
    
    
    answer = json.loads(res.text)["response"]
    print(answer)

    tts(text=answer, output="output.wav")
    
    pygame.mixer.music.load('output.wav')  
    pygame.mixer.music.set_volume(0.5) 
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # 在音频播放为完成之前不退出程序
        pass
    # os.remove("./output.wav")
    pygame.mixer.music.unload()
