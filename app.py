#!/bin/env python
# coding: utf-8
import sys
sys.path.append('./vendor')

import os
import re
from flask import Flask, render_template, request, abort
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours =+ 9), 'JST')

app = Flask(__name__)

# ルート
@app.route('/')
def index():
	return 'index'

@app.route('/<name>')
def hello(name=''):
	if name == '':
		name = u'ななしさん'
	return render_template('hello.html', name=name)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(port=port)