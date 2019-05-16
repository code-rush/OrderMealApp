# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-05-15 18:03:31
# @Last Modified by:   Japan Parikh
# @Last Modified time: 2019-05-15 20:10:13


from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/report')
def report():
    return render_template('report.html')


if __name__ == '__main__':
    app.run()