# coding=utf-8
import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory,session
import textrank
from myTTS import RoboRap


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    audio_id = "default.mp3"
    if request.method == 'POST':
        original_news = request.form['news_content']
        print(original_news)
        summary = textrank.summarize(original_news)
        print(summary)
        lyric = summary
        # lyric = generate_lyric(summary)
        roborap = RoboRap()
        outputFileFullPath = roborap.text2rap(lyric)
        return render_template('index.html', message=audio_id)
    return render_template('index.html', message=audio_id)


@app.route('/audio')
def audio():
    return render_template('test_audio.html')


if __name__ == '__main__':
    app.run(debug=True)
