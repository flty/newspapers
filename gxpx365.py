#!/usr/bin/python
#-*-coding:gbk*-
import time
import json
import random
import string
import requests
from lxml import etree

import logging

logging.basicConfig(level=logging.INFO,
                format='%(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='gxpx365.log',
                filemode='w')

def enterCourseInfo(le_id,tc_id,tl_id,kj_type,iEntyClass,total_time,total_open_amount):
    url="http://www.gxpx365.com/cmd/LessonStudyControl?flag=LessonStudyInfo2&tl_id=%d&le_id=%d&tc_id=%d&type=%d&iEntyClass=%s&total_time=%d&total_open_amount=%d"%(tl_id,le_id,tc_id,kj_type,iEntyClass,total_time,total_open_amount);
    return url

def previewMinutes(le_id,tl_id,type,tc_id,isStation,isEnty,isSelected):
    url = "LessonStudyControl?flag=study&tl_id="+tl_id+"&le_id="+le_id+"&isStation="+isStation+"&tc_id="+tc_id+"&type="+type+"&isEnty="+isEnty+"&isSelected="+isSelected+"&flag=true" ;
    return url


s = requests.Session()
s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.35'
# s.headers['Referer'] = 'http://www.gxpx365.com/jsp/portal/index.jsp'

url = 'http://www.gxpx365.com/jsp/portal/index.jsp'

req = s.get(url)

url1 = 'http://www.gxpx365.com/jsp/portal/logining1.jsp'

name = u' '

req = s.post(url1, data= {'name':name.encode('gb2312'),'pwd':'8888','role':'student'})

url2 = 'http://www.gxpx365.com/cmd/LessonStudyControl?flag=list&CurrentResourceID=36662'

req = s.get(url2)


tr = etree.HTML(req.text)

lessons = tr.xpath('.//td[@id="td2"]/img')
les = lessons[0].get('onclick')[12:-1]
print 'les = %s' %les

url3 = eval(les)

print url3
req = s.get(url3)

url4 = 'http://www.gxpx365.com/resource/course/2015-LE-00971/XueXi.htm?flag=video&s=1915'
req = s.get(url4)
logging.info( req.content)
