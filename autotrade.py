#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tushare as ts 
import pandas as pd
import requests
import re
import datetime
import os

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

	req = requests.get(url, headers = headers, timeout=10 )
	req.encoding = 'GB2312'
	text = req.text

	reg = re.compile('class=\"today(^ .*?)\">')
	res = reg.findall(text)
	res = ''.join(res)
	if res == '':
		return datetime.datetime.today().strftime('%Y-%m-%d')
	elif 'work' in res:
		return datetime.datetime.today().strftime('%Y-%m-%d')
	else:
		return None


if __name__ == '__main__':
	newest_trade_day = newest_trade_day()
	if newest_trade_day:
		trade_data_file = './stock/%s.csv'%newest_trade_day
		result_file = './stock/result%s.csv'%newest_trade_day
		if os.path.exists(trade_data_file):
			df_today_all = pd.read_csv(trade_data_file, encoding='GBK')
		else:
			df_today_all = ts.get_today_all()
			df_today_all.to_csv(trade_data_file, encoding='GBK')

		all_codes = df_today_all['code']

		df_result = pd.DataFrame({'code':[], 'time':[]})

		for code in all_codes:
			code = '%06d'%int(code)
			df_stock_amount = ts.get_stcok_amount(code, date = newest_trade_day )
			if df_stock_amount.size >= 21 and df_stock_amount.get_value(0,'type') == '买盘' \
						and df_stock_amount.get_value(0,'type') == df_stock_amount.get_value(1,'type') \
						and df_stock_amount.get_value(1,'type') == df_stock_amount.get_value(2,'type') :
				print code, df_stock_amount.get_value(0,'date')
				df_result = df_result.append({'code':code, 'time':df_stock_amount.get_value(0,'date')}, ignore_index = True )

		df_result.to_csv(result_file, encoding= 'GBK')

		dflist = list(df_result['code'])
		dfresult =[str(code) for code in dflist]

		df = ts.get_realtime_quotes(dfresult)
		df.to_csv('./stock/1.csv', encoding = 'gbk')

	else:
		print 'Today is not a trade day. Wish you earn many many more money! Bye!'


