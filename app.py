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

app = Flask(__name__)
app.config['DEBUG'] = True
# 日本語文字化け対策
app.config['JSON_AS_ASCII'] = False

# ルート
@app.route('/')
def index():
	return render_template('index.html')

# OPENPCのindex
@app.route('/openpc')
def openpc():
	return render_template('openpc_index.html')

# CANCELLのindex
@app.route('/cancell')
def cancell():
	return render_template('cancell_index.html')

# -------------------
# OPENPC API
# -------------------

# すべての教室の状況
@app.route('/openpc/api/v1/<int:campus>')
def pc(campus):
# 存在しないキャンパスを指定された場合
	if not (campus == 1 or campus == 2):
		return '存在しないキャンパスです'
	else:
# webのスクレイピング開始
		result = get_room_status(campus)
		return jsonify(result)

# 開いてる教室の状況
@app.route('/openpc/api/v1/<int:campus>/open')
def open(campus):
# 存在しないキャンパスを指定された場合
	if not (campus == 1 or campus == 2):
		return '存在しないキャンパスです'
	else:
# webのスクレイピング開始
		result = get_room_status(campus, mode='open')
		return jsonify(result)

# 教室状況取得メソッド
def get_room_status(campus, mode='all'):
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
	room_result = []
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
			detail['room'] = room_name
			detail['free'] = number[0]
			detail['max'] = number[1]
			room_result.append(detail)
		else:
			if mode == 'all':
				detail = {
					'room': room_name,
					'status': room_status
				}
				room_result.append(detail)

# 結果
	result = {
		"data":{
			"campus": campus_name,
			"date": date
		}
	}
	result['status'] = room_result

	return result
# ここまで
# 教室状況取得メソッド

# -------------------
# CANCELL API
# -------------------

@app.route('/cancell/api/v1/<int:campus>/<string:target_day>')
def cancel(campus, target_day):
	# 存在しないキャンパスを指定された場合
	if not (campus == 1 or campus == 2 or campus == 3):
		return '存在しないキャンパスです'
	else:
		result = get_cancelled_class(campus, target_day)
		return jsonify(result)

# 休講情報取得メソッド
def get_cancelled_class(campus, target_day):
# 現在時刻取得
	date = datetime.now().strftime("%m月%d日 %H:%M:%S")

# キャンパス名設定
	if campus == 1:
		campus_name = '今出川'
	elif campus == 2:
		campus_name = '京田辺'
	elif campus == 3:
		campus_name = '大学院'

# 結果用配列
	result = {
		"data":{
			"campus": campus_name,
			"date": date
		}
	}

# データ収集
	if target_day == 'today':
		html = urllib.request.urlopen('https://duet.doshisha.ac.jp/kokai/html/fi/fi050/FI05001G.html')
		search_day = datetime.now(JST).strftime("%m月%d日")
	elif target_day == 'tomorrow':
		html = urllib.request.urlopen('https://duet.doshisha.ac.jp/kokai/html/fi/fi050/FI05001G_02.html')
		tomorrow = datetime.now(JST) + timedelta(1)
		search_day = tomorrow.strftime("%m月%d日")
	elif target_day == 'dad':
		html = urllib.request.urlopen('https://duet.doshisha.ac.jp/kokai/html/fi/fi050/FI05001G_03.html')
		tomorrow = datetime.now(JST) + timedelta(1)
		search_day = tomorrow.strftime("%m月%d日")
	else:
		result['error'] = '実装されてない検索日です'
		return result
	result['data']['search_day'] = search_day

	soup = BeautifulSoup(html, "lxml")
	rows = soup.find_all('table', class_='data table')
	cancelled_class = []
	for c, row in enumerate(rows):
		if c == campus - 1:
			print('---------')
			for i, subject in enumerate(row.find_all('tr')):
				if i == 0:
					continue
				classes = {}
				print(i)
				for j, detail in enumerate(subject.find_all('td')):
					if j % 4 == 0:
						classes['class_hour'] = detail.text
					elif j % 4 == 1:
						classes['class_name'] = detail.text
					elif j % 4 == 2:
						classes['calss_teacher'] = detail.text
					elif j % 4 == 3:
						classes['class_cause'] = detail.text
				print(classes)
				cancelled_class.append(classes)
				classes = {}

	result['cancelled_classes'] = cancelled_class
	return result

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(port=port)