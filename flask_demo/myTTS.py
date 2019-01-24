from aip import AipSpeech
from pydub import AudioSegment
from io import BytesIO
import functools
import librosa
import numpy as np
import jieba
import os

class RoboRap():

    def __init__(self):
        self._APP_ID = '15476217'
        self._API_KEY = 'HsZZTStCTwgtpiY6xAx7eWOt'
        self._SECRET_KEY = '90ANCnFxOFFdaEGosFugbVCSxf4ZwH1W'
        self.client = AipSpeech(self._APP_ID, self._API_KEY, self._SECRET_KEY)

        self.BPM = 160
        self.SPB = 60 / self.BPM

        self.intro = 13.3

    def get_rhythm(self, sentence):
        length = len(sentence)

        # Get a list og possible rhythms
        rhythm_list = []
        if length == 5:
            rhythm_list = ['*--****-', '**-***--']
        if length == 6:
            rhythm_list = ['**-****-', '*-*****-']
        if length == 7:
            rhythm_list = ['*******-', '**-^***-', '*-**^**-', '***-^**-']
        if length == 8:
            rhythm_list = ['****^**-', '^**-^**-']
        if length == 9:
            rhythm_list = ['^*******', '^***^**-']
        if length == 12:
            rhythm_list = ['**********-**---', '***********-*---']
        if length == 13:
            rhythm_list = ['********^**-*---']
        if length == 14:
            rhythm_list = ['^************---']
        if length == 15:
            rhythm_list = ['^*******^****---']
        if length == 16:
            rhythm_list = ['^***^***^****---']
        if len(rhythm_list)==0:
            rhythm_list = ['*'*(length-2)+'^']

        # TODO: Choose the best rhythm according to the sentence
        # word_list = list(jieba.cut(sentence))
        # min_error = len(sentence)
        # best_index = -1
        # for i, rhythm in rhythm_list:
        #     error = 0
        #     for word in word_list:
        #         pass

        return rhythm_list[0]

    def text2rap(self, text, outputDir = os.getcwd()):
        content = text.split("\n")
        total_num = len(content)
        rap_sounds = []
        for i, sentence in enumerate(content):
            # self.status_bar.setText('Rappify: {0}%'.format(100*i/total_num))
            print('Rappify: {0}%'.format(100*i/total_num))
            rap_sounds.append(self.get_rap(sentence))
        rap = functools.reduce(lambda x, y: x+y, rap_sounds)
        #add beats
        intro_sec_segment = AudioSegment.silent(duration=self.intro*1000)  #duration in milliseconds
        beat = AudioSegment.from_file("static/audio/beat.wav")
        song = (intro_sec_segment + rap).overlay(beat)
        outputFile = outputDir + "/song.wav"
        song.export(outputFile, format='wav')
        return outputFile

    def get_rap(self, sentence):
        word_sounds = []
        for word in sentence:
            result  = self.client.synthesis(word, 'zh', 1, {'vol': 9, 'per':3, 'spd':1, 'pitch':9})
            print(BytesIO(result))
            sound = AudioSegment.from_mp3(BytesIO(result))
            word_sounds.append(sound)
        silence = AudioSegment.silent(duration=self.SPB*500)

        rhythm = self.get_rhythm(sentence)
        i = 0
        beat_sounds = []
        for c in rhythm:
            if c == '*':
                beat_sounds.append(self.time_stretching(word_sounds[i], self.SPB))
                i += 1
            if c == '^':
                beat_sounds.append(self.time_stretching(word_sounds[i], self.SPB / 2) + self.time_stretching(word_sounds[i+1], self.SPB / 2))
                i += 2
            if c == '-':
                beat_sounds.append(silence)
        rap = functools.reduce(lambda x, y: x+y, beat_sounds)

        return rap


    def setBPM(self, bpm):
        self.BPM = bpm
        self.SPB = 60 / self.BPM


    def read_sentences(self, filename):
        with open(filename, 'r') as f:
            content = [line.strip() for line in f]
        return content


    def change_sound(self, sound:AudioSegment, time_duration, pitch_step):
        sound = self.time_stretching(sound, time_duration)
        sound = self.pitch_shifting(sound, pitch_step)
        return sound


    def time_stretching(self, sound:AudioSegment, time_duration):

        sound.export('tmp.mp3', format='mp3')
        y, sr = librosa.load('tmp.mp3')
        y_stretch = librosa.effects.time_stretch(y, sound.duration_seconds / time_duration)
        librosa.output.write_wav('tmp.wav', y_stretch, sr)
        new_sound = AudioSegment.from_wav('tmp.wav')
        return new_sound

        # y = np.array(sound.get_array_of_samples(), dtype='float32')
        # y_stretch = librosa.effects.time_stretch(y, speed)
        # new_sound = sound._spawn(y_stretch)


    def pitch_shifting(self, sound:AudioSegment, step):

        sound.export('tmp.mp3', format='mp3')
        y, sr = librosa.load('tmp.mp3')
        y_shift = librosa.effects.pitch_shift(y, sr, n_steps=step, bins_per_octave=8)
        librosa.output.write_wav('tmp.wav', y_shift, sr)
        new_sound = AudioSegment.from_wav('tmp.wav')
        return new_sound
