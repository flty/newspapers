#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import datetime
import os
from PIL import Image , ImageEnhance 
from StringIO import StringIO

import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')   


def grey(img):
    """灰度化"""
    img = img.convert('RGB')
    img.save('3.jpg')
    return img

def binary(img,r=90,g=200,b=0):
    """二值化"""
    pixdata = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][0] < r:
                pixdata[x, y] = (0, 0, 0, 255)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][1] < g:
                pixdata[x, y] = (0, 0, 0, 255)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][2] > b:
                pixdata[x, y] = (255, 255, 255, 255)
    img.save('4.jpg')
    return img

def denoisepoint(img, n, opt_point=0):
    """去噪点"""
    direct=[[1,1],[1,0],[1,-1],[0,-1],
            [-1,-1],[-1,0],[-1,1],[0,1]]
    num=0 #操作数量
    point=0 #噪点量
    pix=img.load()
    size=img.size
    for y in range(size[1]):
        for x in range(size[0]):
            num+=1
            if pix[x,y][0]<n:
                nearpoint=0
                for (a,b) in direct:
                    if (x+a>=0 and x+a<=size[0]-1)and(y+b>=0 and y+b<=size[1]-1):
                    #如果遇到边界外的点不处理
                        if pix[x+a,y+b][0]<n:
                            nearpoint+=1
                if nearpoint<=opt_point:
                    pix[x,y]=(255, 255, 255, 255)
                    point+=1
    img.save('6.jpg')
    return img

def devide(img, n):
    """分割图像"""
    #n 分割的阀值
    flagx=[0 for x in range(img.size[0])]
    result=[]
    pix=img.load()
    #横坐标上的像素分布
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if pix[x,y][0]<90:
                flagx[x]+=1
    print flagx
    for i in range(img.size[0]):
        if flagx[i]>n and flagx[i-1]<=n:
            tmp=i
        if flagx[i-1]>n and flagx[i]<=n:
            #纵坐标上的分布
            flagy=[0 for x in range(img.size[1])]
            for y in range(img.size[1]):
                for x in range(i+1)[tmp:]:
                    if pix[x,y][0]<90:
                        flagy[y]+=1
            print x,flagy
            ttmp=0
            #有待改善
            bug=1
            for j in range(img.size[1]):
                if flagy[j]>n and flagy[j-1]<=n:
                    ttmp=j
                if flagy[j-1]>n and flagy[j]<=n:
                    result.append([tmp,i,ttmp,j])
                    bug=0
                    break
            if bug==1:
                result.append([tmp,i,ttmp,img.size[1]])
    print result
    i=1
    for [x1,x2,y1,y2] in result:
        img.crop((x1,y1,x2,y2)).save('char%d.jpg'%i)
        i+=1
    return i-1

def enlargechar():
    """放大字符"""
    for i in range(6)[1:]:
        if i!=5 or os.path.exists(dir+'char5.jpg'):
            img=Image.open(dir+'char%d.jpg'%i)
            img.resize((60,60),Image.NEAREST).save(dir+'char%d-big.jpg'%i)

def recognize(n):
    """识别单个字符"""
    fontMods=[]
    fontdir="./font/"
    for file in os.listdir(fontdir):
        if file.endswith('.jpg'):
            fontMods.append((file[:1],Image.open(fontdir+file)))
    target=Image.open(dir+'char%d-big.jpg'%n)
    points = []
    for mod in fontMods:
        diffs = 0
        for yi in range(60):
            for xi in range(60):
                if mod[1].getpixel((xi, yi)) != target.getpixel((xi, yi)):
                    diffs += 1
        points.append((diffs, mod[0]))
    points.sort()
    return points[0][1]

def fontsave(n,str):
    """字符存入字库"""
    fontdir='./font/'
    img=Image.open(dir+'char%d-big.jpg'%n)
    i=1
    while(os.path.exists(fontdir+str+'-%d.jpg'%i)):
        i+=1
    img.save(fontdir+str+'-%d.jpg'%i)


def enlargeimage(f):
    """放大图片显示"""
    img=Image.open(dir+f)
    big=img.resize((400,175),Image.NEAREST)
    big.save(dir+'big.jpg')


def test():
    img=Image.open(dir+'3.jpg')
    pix=img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pix[x,y]>(90,90,90):
                pix[x,y]=(255,255,255,255)
            else:
                pix[x,y]=(0,0,0,0)
    img.show()
    img.save(dir+'test.jpg')

def denoise(img, n, opt_point=3):
    pix=img.load()
    size=img.size
    for x in range(size[0]):
        point=0
        for y in range(size[1]):
            if pix[x,y][0]<n:
                point += 1
        if point<=opt_point:
            for y in range(size[1]):
                pix[x,y]=(255, 255, 255, 255)
    img.save('5.jpg')
    return img


if __name__ == '__main__':
    url1 = 'http://apply.guilinlife.com/mbb/votes/id/2446'
    url2 = 'http://apply.guilinlife.com/index/verify/?0.5118171076755971'
    headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Host':'apply.guilinlife.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
    }

    # s = requests.Session()
    # req = s.get(url1, headers = headers, timeout=10 )
    # req = s.get(url2, headers = headers, timeout=10 )
    # i = Image.open(StringIO(req.content))
    # i.save('1.png')
    i = Image.open('1.png')
    x, y = i.size
    bg = Image.new('RGB', i.size, (255,255,255))
    bg.paste(i,(0, 0, x, y))
    bg.save("2.jpg")
    img = Image.open('2.jpg')
    img = grey(img)
    img = binary(img,r=200,g=200,b=200)
    img = denoise(img, 10, opt_point=3)
    img = denoisepoint(img, 10, 3)
    devide(img, 10)

