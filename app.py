#!/bin/env python
# coding: utf-8
import sys
sys.path.append('./vendor')

import os
import re
from flask import Flask, render_template, request, abort, jsonify
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours =+ 9), 'JST')

app = Flask(__name__)
app.config['DEBUG'] = True
# 日本語文字化け対策
app.config['JSON_AS_ASCII'] = False

# ルート
@app.route('/')
def index():
	return 'index'

@app.route('/api/v1/<campus>')
def json(campus=''):
	date = datetime.now(JST).strftime("%H:%M:%S")
	if campus == "1":
		result = {
			"Result":{
				"campus": "今出川",
				"date": date
			}
		}
	elif campus == '2':
		result = {
			"Result":{
				"campus": "京田辺",
				"date": date
			}
		}
	else:
		return '該当するキャンパスが存在しません'
	
	return jsonify(result)

# @app.route('/<name>')
# def hello(name=''):
# 	if name == '':
# 		name = u'ななしさん'
# 	# return render_template('hello.html', name=name)
# 	return name

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(port=port)