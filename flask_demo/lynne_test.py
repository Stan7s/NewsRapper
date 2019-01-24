# coding=utf-8
from myTTS import RoboRap
from pydub import AudioSegment
AudioSegment.converter = r"C:\Users\Lingbo\AppData\Local\Programs\Python\Python35\Lib\site-packages\ffmpeg\ffmpeg\bin\ffmpeg"

with open('test.mp3', 'r') as f:
    sound = AudioSegment.from_mp3(f)
# roborap = RoboRap()
# text = '重庆市委书记\n他们结合实际'
# outputFileFullPath = roborap.text2rap(text)