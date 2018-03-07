# Line bot

from linebot import LineBotApi

from linebot.models import TextSendMessage

from linebot.exceptions import LineBotApiError

import requests
from time import strftime, localtime, sleep
from datetime import datetime, date
import pytz

tpe = pytz.timezone('Asia/Taipei')
goGetColor = False
line_bot_api = LineBotApi('Channel Access Token') #Your Channel Access Token
handler = WebhookHandler('Channel Secret') #Your Channel Secret

def push_message(pushtext):
    line_bot_api.push_message(["id1","id2"], TextSendMessage(text=pushtext))

while 1:
    utcNow = datetime.utcnow()
    now = tpe.fromutc(utcNow).strftime("%H:%M")

    if now == "00:00":
        print ('Crawler starting...')
        goGetColor = True
    elif now == "00:30" and goGetColor == True:
        print('Crawler stop!')
        push_message('對不起，我失敗了......\n顏色抓取失敗：%s' % now)
        goGetColor = False

    if goGetColor == True:
        todayTime = str(int(strftime("%Y"))-1911) +'年'+ tpe.fromutc(utcNow).strftime('%m') + '月' + tpe.fromutc(utcNow).strftime('%d') + '日'
    #   print (str(int(strftime("%Y"))-1911)+strftime("年%m月%d日", localtime()))
        #print(todayTime)
        getdate, gColor, bColor = getColorToday()
        if getdate == todayTime:
            print ('update:%s', todayTime)
            getdate, gColor, bColor = colorRequest()
            msgtext = ('%s，吉色：%s，忌色：%s' % (getdate, gColor, bColor))
            try:
           		push_message(msgtext)
                goGetColor = False
                print('Cralwer stop!')
            except LineBotApiError as e:
                # error handle
                print (e)
        break
    else:
        sleep(60)
