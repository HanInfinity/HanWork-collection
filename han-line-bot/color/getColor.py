import requests
from bs4 import BeautifulSoup

def findColor(colorList, colorIndex):
	#判定如果沒有抓到顏色（如空白）則回傳空白文字，避免錯誤。
	try:
		color = list(colorList[colorIndex].stripped_strings)[0]
	except:
		color = "無"
	return color

def colorRequest():
	reqContent = requests.get('http://www.bestradio.com.tw/Almanac.aspx')
	#print (reqContent.text.encode('utf-8'))
	soup=BeautifulSoup(reqContent.text.encode('utf-8'), "html.parser")
	#從class=back中，先找到吉色的位置
	for line in soup.select('.back'):
		if list(line.stripped_strings)[0] == '國曆':
			dateList = list(list(line.next_siblings)[1].stripped_strings)[0]
			print(dateList)
		#從吉色列出brother tags，吉色與忌色的顏色為[1],[3]
		if list(line.stripped_strings)[0] == '吉色':
			colorList = list(line.next_siblings)
			good = findColor(colorList, 1)
			bad = findColor(colorList, 5)
			print('吉色', good)
			print('忌色', bad)
	return dateList, good, bad
