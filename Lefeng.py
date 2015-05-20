#!/usr/bin/python
#-*-coding:utf-8-*-
# Author: Kaysen
# Date: 2014-09-13
# 采集乐峰数据脚本，用于后台统计图分析价格和其他属性的变化情况

import re
import urllib
import MySQLdb
import sys
import time
import random
import os
import socket
socket.setdefaulttimeout(30)
reload(sys)
sys.setdefaultencoding('utf-8')

class Lefeng(object):
	def __init__(self, host, user, passwd, db):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.db = db
	
	def run(self):
		conn=MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
		cursor = conn.cursor()
		cursor.execute('SELECT id,name,lefeng_href FROM lefeng_category WHERE pid>0')
		results = cursor.fetchall()
		cursor.close()

		for row in results:
			categoryId = row[0]
			goodsType = 'meizhuang'
			pageContent = urllib.urlopen(row[2]).read()
			reg = r'class="tpageNum">.*<\/i>[\s\/]+(.*)</em>'
			pageTotal = re.findall(re.compile(reg), pageContent)
			del pageContent
		
			condition = 'all'
			if len(sys.argv)>1 and sys.argv[1] == 'delta':
				condition = 'delta'
			
			self.findCategoryAllGoods(row, categoryId, goodsType, pageTotal)

	def findCategoryAllGoods(self, row, categoryId, goodsType, pageTotal):
		for key in range(1, int(pageTotal[0])+1):
			print '%s============== %s/%s =============== %s' % (row[1], key, pageTotal[0], \
					time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time())))
			currUrl = row[2].strip().rstrip('.html') + '_0_0_0_0_0_5|0_' + str(key) + '.html#list'
			print currUrl
			pageContent = urllib.urlopen(currUrl).read()
			status = self.getPageAllInfo(pageContent, categoryId, goodsType)
			print '完成当前页数据抓取 === 状态：%s' % (status)

	def getPageAllInfo(self, pageContent, categoryId, goodsType):
		reg = r'class="nam">.*href="(.*)" target.*</dd>'
		goodsUrlList = re.findall(re.compile(reg), pageContent)
		print '获取商品地址中...   ',
		print '[finish]'

		reg = r'class="nam">.*title="(.*)".*</dd>'
		titleList = re.findall(re.compile(reg), pageContent)
		print '获取商品标题中...   ',
		print '[finish]'

		reg = r'<img src2="(.*)".*alt'
		picList = re.findall(re.compile(reg), pageContent)
		print '获取商品图片中...   ',
		print '[finish]'

		reg = r'class="buynum".*>\D+(\d+)\D+</a>'
		volumeList = re.findall(re.compile(reg), pageContent)
		del pageContent
		
		priceList = []
		priceNum = 0
		print '获取商品价格中...   ',
		
		for url in goodsUrlList:
			priceNum += 1
			#time.sleep(random.randint(1, 2))
			goodsId = url.split('/')[-1].strip().rstrip('.html')
			priceContent = urllib.urlopen('http://wap.lefeng.com/index.php/goods/detail/goodsId/' + goodsId).read()
			reg = r' <p>乐蜂价:.*class="red">(.*)</span></p>'
			price = re.findall(re.compile(reg), priceContent)
			del priceContent
			if type(price)==list and  len(price)>0:
				priceList.append(str(price[0]))
			else:
				priceList.append('0')
		print '[finish]'
		
		return self.insertDbGoods(goodsUrlList, titleList, picList, priceList, volumeList, categoryId, goodsType)

	def insertDbGoods(self, goodsUrlList, titleList, picList, priceList, volumeList, categoryId, goodsType):
		putawayTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		conn=MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
		cursor = conn.cursor()	
		
		if len(sys.argv)>1 and sys.argv[1] == 'delta':
			dataList = []
			for key in range(0, len(goodsUrlList)):
				existStatus = cursor.execute('SELECT id FROM lefeng_goods WHERE goods_url LIKE "%' + str(goodsUrlList[key]) + '%"')
				if int(existStatus) == 0:
					param = (MySQLdb.escape_string(titleList[key]), goodsUrlList[key], picList[key], categoryId, str(priceList[key]), volumeList[key], goodsType)
					status = cursor.executemany('INSERT IGNORE INTO lefeng_goods (title, goods_url, image, category, price, volume, type) VALUES (%s, %s, %s, %s, %s, %s, %s)', [param])
				del existStatus

				existStatus = cursor.execute('SELECT id FROM lefeng_goods WHERE goods_url LIKE "%' + str(goodsUrlList[key]) + '%"')
				existResults = cursor.fetchall()

				if int(existStatus) > 0:
					sql = 'INSERT INTO lefeng_goods_alter (goods_id, new_price, new_volume, update_time) VALUES (%s, %s, %s, %s)'
					param = (str(existResults[0][0]), str(priceList[key]), str(volumeList[key]), str(putawayTime))
					status = cursor.execute(sql,param)
		else:
			dataList = []
			for key in range(0, len(goodsUrlList)):
				dataList.append((MySQLdb.escape_string(titleList[key]), goodsUrlList[key], picList[key], categoryId, str(priceList[key]), volumeList[key], goodsType))
			status = cursor.executemany('INSERT IGNORE INTO lefeng_goods (title, goods_url, image, category, price, volume, type) VALUES (%s, %s, %s, %s, %s, %s, %s)', dataList)
		
		cursor.close()	
	
		del goodsUrlList
		del titleList
		del picList
		del priceList
		del volumeList
		del putawayTime
		del dataList

		return status;

Lefeng = Lefeng('localhost', 'root', '', 'beauty')
Lefeng.run()
