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
# 存在しないキャンパスを指定された場合
	if not (campus == 1 or campus == 2):
		return '存在しないキャンパスです'

# webのスクレイピング開始
	if campus == 1:
		result = get_room_status(1)
	elif campus == 2:
		result = get_room_status(2)
	
	return jsonify(result)

# @app.route('/<name>')
# def hello(name=''):
# 	if name == '':
# 		name = u'ななしさん'
# 	# return render_template('hello.html', name=name)
# 	return name


# 教室状況取得メソッド
def get_room_status(campus):
# 現在時刻取得
	date = datetime.now(JST).strftime("%H:%M:%S")

	if campus == 1:
		campus_name = '今出川'
		html = urllib.request.urlopen("http://openpc.doshisha.ac.jp/Openpc/classroom_listDetail.aspx?campus=1").read()
	else:
		campus_name = '京田辺'
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

# 閉室じゃない場合更に詳細取得
		if not (room_status == '閉室' or room_status == '授業中'):
			detail = {}
			number = room_status.split('/')
			detail['free'] = number[0]
			detail['max'] = number[1]
			room_result[room_name] = detail
		else:
			room_result[room_name] = room_status

# 結果
	result = {
		"Result":{
			"campus": campus_name,
			"date": date
		}
	}
	result['status'] = room_result

	return result
# ここまで
# 教室状況取得メソッド

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(port=port)