# !/usr/bin/env python
# -*- coding:utf-8 -*- 

import string
import datetime
import time
import lxml.html
from lxml import etree
import re
import os
# from docx import Document
# from docx.enum.style import WD_STYLE_TYPE
# from docx.shared import Pt 
import win32com
from win32com.client import Dispatch, constants

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

def today():
	today = datetime.datetime.today().date()
	return str(today)

def get_rmrb_top10():
	url = r'http://paperpost.people.com.cn/all-rmrb-%s.html' %today()
	text = urlopen(url).read()

	pattern = re.compile(r'<a href=\"(.*?)\"')
	top10_urls = re.findall(pattern,text)

	return top10_urls

def save_to_docx(urls=None, save_dir=None ):
	for eachurl in urls:
		try:
			html = lxml.html.parse(eachurl)
		except:
			continue

		res = html.xpath('//div[@id=\"ozoom\"]/p')
		title = ''.join(html.xpath('//h1/text()'))
		author = ''.join(html.xpath('//h4/text()'))
		newdoc = Document()

		newdoc.add_heading(title,0)
		newdoc.add_paragraph(author)


		for node in res:

			paragraph = newdoc.add_paragraph()
			paragraph_format = paragraph.paragraph_format
			paragraph_format.line_spacing = Pt(30)
			run = paragraph.add_run(node.text)
			font = run.font
			font.name = u"微软雅黑"
			font.size = Pt(16)

		newdoc.save(save_dir+title+r'.docx')
	return 0

def save_to_doc(urls=None, save_dir=None ):
	wdApp = win32com.client.DispatchEx('Word.Application')
	wdApp.Visible = 0
	wdApp.DisplayAlerts = 0
	for eachurl in urls:
		try:
			html = lxml.html.parse(eachurl)
		except:
			continue

		res = html.xpath('//div[@id=\"ozoom\"]/p')
		title = ''.join(html.xpath('//h1/text()'))
		author = ''.join(html.xpath('//h4/text()'))

		newdoc = wdApp.Documents.Add() 
		myRange = newdoc.Range(0,0)
		myRange.InsertAfter(title)
		myRange.InsertAfter('\r\n')
		myRange.InsertAfter(author)
		myRange.InsertAfter('\r\n')
		# wdApp.ActiveDocument.Paragraphs(1).Range.InsertAfter(author)
		# iParagraph = 2
		
		# 使用样式

		# newdoc.add_heading(title,0)
		# newdoc.add_paragraph(author)


		for node in res:
			content = node.text.lstrip('　')
			myRange.InsertAfter(content)
			myRange.InsertAfter('\r\n')
			# wdApp.ActiveDocument.Paragraphs(iParagraph).Range.InsertAfter(content)
			# wdApp.ActiveDocument.Paragraphs.Add()

			# iParagraph += 1

		# print r'%s%s.doc'%(save_dir,title)

		newdoc.SaveAs(r'%s%s.doc'%(save_dir,title))		
		newdoc.Close(True)

	time.sleep(1)
	wdApp.Quit()
	return 0

def save_to_doc_new(urls=None, save_dir=None ):
	wdApp = win32com.client.DispatchEx('Word.Application')
	wdApp.Visible = 0
	wdApp.DisplayAlerts = 0
	for eachurl in urls:
		try:
			html = lxml.html.parse(eachurl)
		except:
			continue

		res = html.xpath('//div[@id=\"ozoom\"]/p')
		title = ''.join(html.xpath('//h1/text()'))
		author = ''.join(html.xpath('//h4/text()'))

		newdoc = wdApp.Documents.Add() 
		myRange = newdoc.Range(0,0)
		myRange.InsertAfter(title)
		wdApp.ActiveDocument.Paragraphs(1).Range.InsertAfter(author)
		iParagraph = 2
		
		# 使用样式

		# newdoc.add_heading(title,0)
		# newdoc.add_paragraph(author)

		for node in res:
			content = node.text.lstrip('　')
			wdApp.ActiveDocument.Paragraphs(iParagraph).Range.InsertAfter(content)
			wdApp.ActiveDocument.Paragraphs.Add()

			iParagraph += 1

		# print r'%s%s.doc'%(save_dir,title)

		newdoc.SaveAs(r'%s%s.doc'%(save_dir,title))		
		newdoc.Close(True)

	time.sleep(1)
	wdApp.Quit()
	return 0


if __name__ == '__main__':
	save_dir =  r'G:/rmrb_top10/%s/'%(today())
	if not os.path.isdir(save_dir):
		os.mkdir(save_dir)

	top10_urls = get_rmrb_top10()

	save_to_doc_new(top10_urls, save_dir)
