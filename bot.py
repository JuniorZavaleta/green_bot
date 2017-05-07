#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask running'

if __name__ == '__main__':
    app.run(debug=True)
