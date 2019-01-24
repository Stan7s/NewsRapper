from aip import AipSpeech
from pydub import AudioSegment
from io import BytesIO
import functools
import librosa
import numpy as np
import jieba
import os
from gtts import gTTS,lang

class RoboRap():

    def __init__(self):
        self._APP_ID = '15476217'
        self._API_KEY = 'HsZZTStCTwgtpiY6xAx7eWOt'
        self._SECRET_KEY = '90ANCnFxOFFdaEGosFugbVCSxf4ZwH1W'
        self.client = AipSpeech(self._APP_ID, self._API_KEY, self._SECRET_KEY)

        self.BPM = 185  # = beat tempo * 2
        self.SPB = 60 / self.BPM

        self.intro = 13.44435374
        self.beat = "static/audio/beat.wav"

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
        #beat tempo and times; onset detection
        y, sr = librosa.load(self.beat)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        self.setBPM = tempo * 2

        #rapify sentences
        content = text.split("\n")
        total_num = len(content)
        rap_sounds = []

        time_cnt = self.intro
        time_cnt_idx = 0
        sentence_silence_increment = 0
        for i, sentence in enumerate(content):
            # self.status_bar.setText('Rappify: {0}%'.format(100*i/total_num))
            print('Rappify: {0}%'.format(100*i/total_num))
            sentenceSound = self.get_rap_sentence(sentence)
            # sentenceSound = self.get_rap_word(sentence)
            time_cnt += sentenceSound.duration_seconds
            #add silence to meet next nearest beat peak time
            while(time_cnt_idx < len(beat_times)):
                if beat_times[time_cnt_idx] > time_cnt:
                    sentence_silence_increment = beat_times[time_cnt_idx] - time_cnt
                    sentenceSound = sentenceSound + AudioSegment.silent(duration=sentence_silence_increment*1000)
                    time_cnt = beat_times[time_cnt_idx]
                    break
                time_cnt_idx += 1
            print(time_cnt_idx, time_cnt, beat_times[time_cnt_idx])
            rap_sounds.append(sentenceSound)

        #align sentences
        rap = functools.reduce(lambda x, y: x+y, rap_sounds)

        #add beats
        intro_sec_segment = AudioSegment.silent(duration=self.intro*1000)  #duration in milliseconds
        beat = AudioSegment.from_file(self.beat)
        song = (intro_sec_segment + rap + intro_sec_segment).overlay(beat)
        
        #export
        outputFile = outputDir + "/song.wav"
        song.export(outputFile, format='wav')
        print("save audio to " + outputFile)
        
        return outputFile

    # def test_single_word(self):
    #     result  = self.client.synthesis('重', 'zh', 3, {'vol': 15, 'per':3, 'spd':5, 'pitch':5})
    #     sound = AudioSegment.from_mp3(BytesIO(result))
    #     sound.export("word1.wav", format = 'wav')
    #     result  = self.client.synthesis('庆', 'zh', 3, {'vol': 15, 'per':3, 'spd':5, 'pitch':5})
    #     sound = AudioSegment.from_mp3(BytesIO(result))
    #     sound.export("word2.wav", format = 'wav')

    def get_rap_sentence(self, sentence):
        #result  = self.client.synthesis(sentence, 'zh', 3, {'vol': 15, 'per':3, 'spd':5, 'pitch':5})
        #sound = AudioSegment.from_mp3(BytesIO(result))
        tts = gTTS(text=sentence, lang='zh-cn')#use decode to solve ascii error
        tts.save("speech.mp3")
        sound = AudioSegment.from_mp3("speech.mp3")
        return sound


    def get_rap_word(self, sentence):
        word_sounds = []
        for word in sentence:
            result  = self.client.synthesis(word, 'zh', 3, {'vol': 15, 'per':3, 'spd':1, 'pitch':5})

            sound = AudioSegment.from_mp3(BytesIO(result))
            word_sounds.append(sound)
        silence = AudioSegment.silent(duration=self.SPB*1000)

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
        #add trim
        # y_stretch = librosa.effects.time_stretch(y, sound.duration_seconds / time_duration)
        yt, index = librosa.effects.trim(y)
        y_stretch = librosa.effects.time_stretch(yt, librosa.get_duration(yt) / time_duration)

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
