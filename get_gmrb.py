# !/usr/bin/env python
# -*- coding:utf-8 -*- 

import string
import datetime
import time

import re
import os
import PyPDF2

import requests
from threading import Thread

import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

UPDATE_INTERVAL = 0.01

headers = {	'Accept-Encoding': 'gzip,deflate','User-Agent':'Mozilla/5.0'}

def today():
	today = datetime.datetime.today().date()
	return str(today)

def get_gmrb_pdf_urls():
	url = r'http://epaper.gmw.cn/gmrb/paperindex.htm'
	s = requests.Session() 

	r = s.get(url, headers= headers)

	text = r.content

	pattern = re.compile(r'<META HTTP-EQUIV=\"REFRESH\" CONTENT=\"0; URL=(.*?)\">')
	real_url= re.findall(pattern,text)[0] 


	real_url = "http://epaper.gmw.cn/gmrb/" + real_url

	r = s.get(real_url, headers= headers)

	text = r.content

	pattern = re.compile(r'<a href=../../../(.*?)>')
	pdf_urls = re.findall(pattern,text)

	return pdf_urls


def save_to_file(url=None, save_dir=None ):

	filename = url[-18:]

	r = requests.get("http://epaper.gmw.cn/gmrb/"+url, headers = headers)

	print "I'am writing file"

	with open(save_dir+filename,'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):  
			if chunk: 
				f.write(chunk)  
				f.flush()  

	return 0

class URLThread(Thread):
	def __init__(self, url, save_dir = './'):
		super(URLThread, self).__init__()
		self.filename = url
		self.save_dir = save_dir

	def run(self):
	    try:
			save_to_file(self.filename, self.save_dir)
	    except Exception , what:
			print what
			pass

def multi_get(uris, save_dir='./'):

	def alive_count(lst):
		alive = map(lambda x : 1 if x.isAlive() else 0, lst)
		return reduce(lambda a,b : a + b, alive)

	threads = [ URLThread(uri, save_dir) for uri in uris ]
	for thread in threads:
		thread.start()
	while alive_count(threads) > 0:
		time.sleep(UPDATE_INTERVAL)

def merge_pdf(save_dir=None ):

	pdf_output = PyPDF2.PdfFileWriter()

	pdf_name = save_dir[:-11]+r'%s.pdf'%save_dir[-11:-1]
	print pdf_name

	if os.path.exists(pdf_name):
		os.remove(pdf_name)

	files = os.listdir(save_dir)
	files.sort()
	for eachfile in files:
		if eachfile[-8:] == '_pdf.pdf':
			input_stream = file(save_dir+eachfile, 'rb')
			pdf_input = PyPDF2.PdfFileReader(input_stream)
			page = pdf_input.getPage(0)
			pdf_output.addPage(page)


	output_stream = file( pdf_name,'wb')
	pdf_output.write(output_stream) 
	output_stream.close()
	input_stream.close()
	print 'Done!'

			# PdfFileMerger', 'PdfFileReader', 'PdfFileWriter'

	return 0

if __name__ == '__main__':
	save_dir =  r'G:/gmrb/%s/'%(today())
	if not os.path.isdir(save_dir):
		os.mkdir(save_dir)

	pdf_urls = get_gmrb_pdf_urls()
	print pdf_urls

	# save_to_file(pdf_urls[0], save_dir)

	multi_get( pdf_urls, save_dir)

	merge_pdf(save_dir)


