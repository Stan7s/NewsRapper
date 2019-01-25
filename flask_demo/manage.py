# coding=utf-8
import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory,session
import textrank
from myTTS import RoboRap
from rappify_one_article import split_article


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    audio_path = "default.mp3"
    lyric='-'
    context = {'audio_path': audio_path, 'lyric': lyric}
    if request.method == 'POST':
        original_news = request.form['news_content']
        print(original_news)
        summary = textrank.summarize(original_news)
        print(summary)
        lyric = split_article(summary)
        print(lyric)
        lyric_str = ""
        for line in lyric:
            lyric_str += line + '\n'
        print("Lyric:")
        print(lyric_str)
        roborap = RoboRap()
        audio_path = roborap.text2rap(lyric_str)
        context = {'audio_path': audio_path, 'lyric': lyric}
        return render_template('index.html', **context)
    return render_template('index.html', **context)


@app.route('/audio')
def audio():
    return render_template('test_audio.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
