import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory,session

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)