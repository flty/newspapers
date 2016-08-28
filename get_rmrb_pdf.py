# !/usr/bin/env python
# -*- coding:utf-8 -*- 

from pytesser import *

import string
import datetime
import time
import ImageEnhance 
import requests
import os
import re
import PyPDF2
from threading import Thread
from multiprocessing import Process, Lock, Pool, Manager

import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

UPDATE_INTERVAL = 0.01

requests.adapters.DEFAULT_RETRIES = 10

headers = {
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
    "Connection":"keep-alive",
    "Accept-Encoding": "gzip,deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def today():
	today = datetime.datetime.today().date()
	return str(today)

def get_rmrb_pdf_urls():
	url = r'http://paper.people.com.cn/rmrb/paperindex.htm'
	s = requests.Session() 

	r = s.get(url, headers=headers)

	text = r.content
	pattern = re.compile(r'<META HTTP-EQUIV=\"REFRESH\" CONTENT=\"0; URL=(.*?)\">')
	real_url= re.findall(pattern,text)[0] 


	real_url = "http://paper.people.com.cn/rmrb/" + real_url

	r = s.get(real_url, headers=headers)
	text = r.content
	pattern = re.compile(r'<div class=\"right_title-pdf\"><a href=(.*?)><img src=\"../../../tplimg/ico3.gif\" border=0 /></a>')
	pdf_urls= re.findall(pattern,text)

	return pdf_urls

def save_rmrb_pdf(lock, filename, save_dir='./'):
	s = requests.Session()
	r = s.get("http://paper.people.com.cn/pdfcheck/check/checkPdf.jsp?filename=%s"%filename, headers=headers)
	# time.sleep(10)
	for retry in range(3):
		try:  
			lock.acquire() 
			print filename

			r = s.get("http://paper.people.com.cn/pdfcheck/validatecodegen", headers=headers)

			with open('./tmp.png','wb') as f:
				for chunk in r.iter_content(chunk_size=1024):  
					if chunk: 
						f.write(chunk)  
						f.flush()  
							
			image = Image.open('./tmp.png')

			enhancer = ImageEnhance.Contrast(image) 
			image_enhancer = enhancer.enhance(1) 

			checkcode = image_to_string(image_enhancer)[0:4]
			print checkcode

			pdfurl = "http://paper.people.com.cn/pdfcheck/check/checkCode.jsp?filename=%s&checkCode=%s"%(filename, checkcode)
			r = s.post(pdfurl, timeout=30, headers=headers )
			
		finally:
			lock.release()

		if r.content[:4] == r'%PDF':
			break


	with open(save_dir+filename[-18:],'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):  
			if chunk: 
				f.write(chunk)  
				f.flush()  
		f.close()


	return 0


def merge_pdf(save_dir=None ):

	pdf_output = PyPDF2.PdfFileWriter()

	pdf_name = save_dir[:-11]+r'%s.pdf'%save_dir[-11:-1]
	print pdf_name

	if os.path.exists(pdf_name):
		os.remove(pdf_name)

	files = os.listdir(save_dir)
	files.sort()
	for eachfile in files:
		if eachfile[-4:] == '.pdf':
			input_stream = file(save_dir+eachfile, 'rb')
			pdf_input = PyPDF2.PdfFileReader(input_stream)
			page = pdf_input.getPage(0)
			pdf_output.addPage(page)

	output_stream = file( pdf_name,'wb')
	pdf_output.write(output_stream) 
	output_stream.close()
	input_stream.close()

	print 'Done!'

	return 0

class URLThread(Thread):
	def __init__(self, lock, url, save_dir = './'):
		super(URLThread, self).__init__()
		self.filename = url[9:]
		self.save_dir = save_dir
		self.lock = lock

	def run(self):
	    try:
			save_rmrb_pdf(self.lock, self.filename, self.save_dir)
	    except Exception , what:
			print what
			pass

def multi_get(lock, uris, save_dir='./'):

	def alive_count(lst):
		alive = map(lambda x : 1 if x.isAlive() else 0, lst)
		return reduce(lambda a,b : a + b, alive)

	threads = [ URLThread(lock, uri, save_dir) for uri in uris ]
	for thread in threads:
		thread.start()
	while alive_count(threads) > 0:
		time.sleep(UPDATE_INTERVAL)
	return 0

def run_proc(lock, filename, save_dir):
	return save_rmrb_pdf(lock, filename, save_dir)
	

if __name__ == '__main__':
	start = time.clock()
	save_dir =  r'G:/rmrb/%s/'%(today())
	if not os.path.isdir(save_dir):
		os.mkdir(save_dir)
	
	pdf_urls = get_rmrb_pdf_urls()
	lock = Lock()

	# 第一种方式，多线程，耗时约119.114498 s

	multi_get(lock, pdf_urls, save_dir)
		
	# 第二种方式，单进程，耗时约135.520388 s
	# for each in pdf_urls:
	# 	filename = each[9:]
	# 	print filename
	# 	save_rmrb_pdf(filename, save_dir)

	# 第三种方式，多进程，耗时约98.431271 s
	# plist = []

	# for each in pdf_urls:
	# 	filename = each[9:]
	# 	p = Process(target = run_proc, args = (lock, filename, save_dir))
	# 	plist.append(p)
	# 	p.start()

	# for each in plist:
	# 	each.join()


	# 第四种方式，多进程池，不成功 
	# lock = Manager().Lock()
	# pool = Pool(processes=3)
	# plist = []

	# for each in pdf_urls:
	# 	filename = each[9:]
	# 	result = pool.apply_async( run_proc, (lock, filename, save_dir))
	
	# pool.close()
	# pool.join()

	# if result.successful():
	# 	print 'successful'



	merge_pdf(save_dir)

	end = time.clock()
	print "耗时: %f s" % (end - start)
