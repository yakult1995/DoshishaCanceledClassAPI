#!/bin/env python
# coding: utf-8
import sys
sys.path.append('./vendor')

import os
import re
from flask import Flask, render_template, request, abort, jsonify
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta

# スクレイピング用ライブラリ
import urllib.request
from bs4 import BeautifulSoup	

JST = timezone(timedelta(hours =+ 9), 'JST')

app = Flask(__name__)
app.config['DEBUG'] = True
# 日本語文字化け対策
app.config['JSON_AS_ASCII'] = False

# ルート
@app.route('/')
def index():
	return 'index'

@app.route('/api/v1/<int:campus>')
def json(campus):
# 現在時刻取得
	date = datetime.now(JST).strftime("%H:%M:%S")

# 存在しないキャンパスを指定された場合
	if not (campus == 1 or campus == 2):
		return '存在しないキャンパスです'

# webのスクレイピング開始
	if campus == 1:
		html = urllib.request.urlopen("http://openpc.doshisha.ac.jp/Openpc/classroom_listDetail.aspx?campus=1").read()
		soup = BeautifulSoup(html, 'lxml')
		result = {
			"Result":{
				"campus": "今出川",
				"date": date
			}
		}
	elif campus == 2:
		html = urllib.request.urlopen("http://openpc.doshisha.ac.jp/Openpc/classroom_listDetail.aspx?campus=2").read()
		soup = BeautifulSoup(html, "lxml")
# trを全て抽出
		rows = soup.find_all("tr", {"style": "font-weight:bold"})
		room_result = {}
		room_name = ""
		room_status = ""

# 各行ごとの処理
		for row in rows:
			room = row.find_all("td")
			room_name = room[0].text
			room_status = room[1].get_text()
			room_status = room_status.replace('\r\n','')
			# print(f'{room_name} - {room_status}')
			room_result[room_name] = room_status

# 結果
		result = {
			"Result":{
				"campus": "京田辺",
				"date": date
			}
		}
		result['status'] = room_result
	
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