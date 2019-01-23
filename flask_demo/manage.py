import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory,session

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    audio_id = "default.mp3"  # 音频文件名
    if request.method == 'POST':
        news_content = request.form['news_content']
        print(news_content)
        # audio_id = generate_audio()
        audio_id = news_content
        return render_template('index.html', message=audio_id)
    return render_template('index.html', message=audio_id)


@app.route('/audio')
def audio():
    return render_template('test_audio.html')

if __name__ == '__main__':
    app.run(debug=True)