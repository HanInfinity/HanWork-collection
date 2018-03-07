# encoding: utf-8
import requests
from bs4 import BeautifulSoup
from time import strftime, localtime, sleep
from datetime import datetime, date
import pytz

# Line bot
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

tpe = pytz.timezone('Asia/Taipei')
goGetColor = False

line_bot_api = LineBotApi('Your Channel Access Token') #Your Channel Access Token

def push_message(pushtext):
	for push_id in ["id1","id2"]:
		line_bot_api.push_message(push_id, TextSendMessage(text=pushtext))

def findColor(colorList, colorIndex):
	#判定如果沒有抓到顏色（如空白）則回傳空白文字，避免錯誤。
	try:
		color = list(colorList[colorIndex].stripped_strings)[0]
	except:
		color = "無"
	return color

def getColorToday():
	reqContent = requests.get('http://www.bestradio.com.tw/Almanac.aspx')
	#print (reqContent.text.encode('utf-8'))

	soup=BeautifulSoup(reqContent.text.encode('utf-8'), "html.parser")
	number = 0

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

def sendEmail(contentText, subject):
#	print('%s，吉色：%s，忌色：%s' % (dateList, good, bad))
	me = 'test1223@gmail.com'
	recipients = ['test1223@gmail.com', 'test12564@gmail.com']
	msg = MIMEText(contentText)
	msg['Subject'] = subject
	msg['From'] = me
	msg['To'] = ', '.join(recipients)
	s = smtplib.SMTP('smtp.gmail.com', 587)
	#s.set_debuglevel(1)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login('htest@gmail.com', 'thepassword')
	try:
		s.sendmail(me, recipients, msg.as_string())
		print ('email send successfully!')
	except:
		print ('Failed to send email!!')
	s.quit()

while 1:
	utcNow = datetime.utcnow()
	now = tpe.fromutc(utcNow).strftime("%H:%M")

	if now < "00:30":
		print ('Crawler starting...')
		goGetColor = True
	elif now == "00:30" and goGetColor == True:
		print('Crawler stop!')
		sendEmail('對不起主人，我失敗了......', '顏色抓取失敗：%s' % now)
		push_message('對不起主人，我失敗了......\n顏色抓取失敗：%s' % now)
		goGetColor = False

	if goGetColor == True:
		todayTime = str(int(strftime("%Y"))-1911) +'年'+ tpe.fromutc(utcNow).strftime('%m') + '月' + tpe.fromutc(utcNow).strftime('%d') + '日'
		#	print (str(int(strftime("%Y"))-1911)+strftime("年%m月%d日", localtime()))
		#print(todayTime)
		getdate, gColor, bColor = getColorToday()
		if getdate == todayTime:
			print ('update:%s', todayTime)
			msgtext = ('%s，吉色：%s，忌色：%s' % (getdate, gColor, bColor))
			push_message(msgtext)
			#sendEmail('%s顏色建議，%s忌%s' % (getdate,gColor,bColor), '%s，吉色：%s，忌色：%s' % (getdate, gColor, bColor))
			goGetColor = False
			print('Cralwer stop!')
		break
	else:
		sleep(60)
