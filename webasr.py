import json
import gradio as gr
import numpy as np
import requests
import json
import sounddevice as sd
from scipy.io.wavfile import write
import pyaudio
import numpy as np
from scipy import fftpack
import wave
import os
import gradio as gr
print("loading asr and tts ... ...")
from paddlespeech.cli.asr.infer import ASRExecutor
from paddlespeech.cli.tts.infer import TTSExecutor
# recognizer = sr.Recognizer()
asr = ASRExecutor()
tts = TTSExecutor()
print("loading asr and tts success!")
import os
import librosa
import pygame
pygame.mixer.init()
import soundfile


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

def generateAudio(text):
    #由于TTS无法很好地处理回车符和空格，需要对text里的回车符进行替换
    text = text.replace("\n",",")
    text = text.replace(" ","")
    tts(text, output="output.wav")
    
    audio, sr = librosa.load(path="output.wav")
    return  sr,audio


# wenet.set_log_level(2)
# decoder = wenet.Decoder(lang='chs')

# def recognition(audio):
#     sr, y = audio
#     assert sr in [48000, 16000]
#     if sr == 48000:  # Optional resample to 16000
#         y = (y / max(np.max(y), 1) * 32767)[::3].astype("int16")
#     ans = decoder.decode(y.tobytes(), True)
#     return json.loads(ans)

# text = "Speech Recognition in WeNet | 基于 WeNet 的语音识别"
# gr.Interface(recognition, inputs="mic", outputs="json",
#              description=text).launch()

class historyList():
    
    hlist = []
    def __init__(self):
        self.hlist1 = []


def main(audio):
    
    s,y = audio
    
    print(s)
    assert s in [48000, 16000]
    if s == 48000:  # Optional resample to 16000
        y = (y / max(np.max(y), 1) * 32767)[::3].astype("int16")
    soundfile.write("./input.wav",y,16000)

    wav_res = asr(audio_file="./input.wav")
    print("You said : ", wav_res)
    res = requests.post(url='http://10.10.239.164:8088',
    headers={"Content-Type": "application/json"},
    json={"prompt":wav_res,"history": historyList.hlist})
    
    
    answer = json.loads(res.text)["response"]
    history = json.loads(res.text)["history"]
    

    print(answer)
    # print("historyList: ", historyList.hlist)
    # print("history: ", history)
    # print("history ll: ", len(historyList.hlist))

    if len(history)>=5:
        historyList.hlist = history[-2:-1]
    else:
        historyList.hlist = history

    tts(text=answer, output="output.wav")
    # audio, sr = librosa.load(path="output.wav")
    path1="output.wav"
    return answer, path1



# text1 = "BOE智能语音问答DEMO"
title = "BOE智能语音问答DEMO"
gr.Interface(fn=main, inputs="mic", outputs=[gr.Textbox(label="answer"), gr.Audio(label="audio")], title = title).launch(share=True)
