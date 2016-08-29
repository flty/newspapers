#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import datetime

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')   

def newest_trade_day():
	url = 'http://tools.2345.com/rili.htm'
	headers = {
	'Host': 'tools.2345.com',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
	'Accept-Encoding': 'gzip, deflate, sdch',
	'Accept-Language': 'zh-CN,zh;q=0.8'
	}

	req = requests.get(url, headers = headers, timeout=1.1 )
	req.encoding = 'GB2312'
	text = req.text

	reg = re.compile('class=\"today(^ .*?)\">')
	res = reg.findall(text)
	res = ''.join(res)
	if res == '':
		return datetime.datetime.today().strftime('%Y-%m-%d')
	elif 'rest' in res:
		return (datetime.datetime.today() + datetime.timedelta(days = -2)).strftime('%Y-%m-%d')

if __name__ == '__main__':
	print newest_trade_day()

