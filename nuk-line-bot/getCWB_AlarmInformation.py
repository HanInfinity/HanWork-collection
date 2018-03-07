# encoding: utf-8
from xml.dom.minidom import parse
import xml.dom.minidom
import os, time

## 讀取CAP警訊及解析會用到
import ssl
from urllib.request import urlopen
import json
from datetime import datetime
# Line bot====================================================================================
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
## 使用postgresQL資料庫
import psycopg2

# Tkinter GUI
from tkinter import *
from tkinter.filedialog import askdirectory


def browseFolder():
    global path_to_watch, before
    path_to_watch=askdirectory() + '/'
    before = dict ([(f, None) for f in os.listdir (path_to_watch+'.')])
    f_path.insert('1.0',path_to_watch)


## 設定資料庫連結資訊
conn = psycopg2.connect(database="linedatabasename",
                        user="username",
                        password="pass",
                        host="hostname",
                        port="5432")
cur = conn.cursor()
tableList = {"push_list": "id serial primary key, idtype varchar(50),userid varchar(50)", "cap_kaohsiung": """id serial primary key,
                cap_id varchar(500),
                category integer,
                urgency integer,
                severity integer,
                certainty integer,
                effective timestamptz,
                expires timestamptz,
                senderName integer,
                headline varchar(100),
                description varchar(500),
                instruction varchar(100),
                web varchar(500),
                event integer,
                responseType integer,
                alert_title varchar(100),
                alert_color integer,
                msgType integer
                """}

DB_Dic = {"cap_category": "name",
          "cap_sender": "sender_name",
          "cap_event": "event_name",
          "cap_alert_Color": "color",
          "cap_certainty": "name",
          "cap_urgency": "name",
          "cap_serverity": "name",
          "cap_responseType": "type_name",
          "cap_msgType": "type_name"}

## 設定line bot參數並建立推送函數
line_bot_api = LineBotApi('LineBotApiaccesstoken')



def push_message(msgtext):
    try:
        cur.execute('SELECT * FROM push_list')
        rows = cur.fetchall()
        for row in rows:
            ## line_bot_api.push_message('<user_id>', text)
            line_bot_api.push_message(row[2], TextSendMessage(text=msgtext))
        print ('push %s success!'%(msgtext.split('\n')[0]))
        info.insert('1.0', 'push %s success!\n'%(msgtext.split('\n')[0]))
    except LineBotApiError as e:
        # error handle
        print (e)

# 地震資訊====================================================================================
def difEarth(fileName):
    DOMTree = xml.dom.minidom.parse(fileName)
    collection = DOMTree.documentElement
    onsites = collection.getElementsByTagName("onsite")
    locations = collection.getElementsByTagName("location")
    center = collection.getElementsByTagName("epicenter")[0]
    center_Lon = center.getElementsByTagName("epicenterLon")[0].childNodes[0].data
    center_Lat = center.getElementsByTagName("epicenterLat")[0].childNodes[0].data
    depth = collection.getElementsByTagName("depth")[0].childNodes[0].data
    magnitude_value = collection.getElementsByTagName("magnitudeValue")[0].childNodes[0].data
    earth_info = "震央位於座標({lat}, {lon}),地震規模約{mag}，深度達{dep}公里。\n".format(lat=center_Lat, lon=center_Lon, mag = magnitude_value, dep = depth)


    for onsite in onsites:
        print ("地震!!!!!\n*****地區資訊*****")
        msgtext = getInfo(onsite, "onsite", earth_info)
        push_message(msgtext)
        info.insert('1.0', '{}'.format(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))+msgtext)

##    for location in locations:
##        print ("*****地方政府*****")
##        getInfo(location, "location")

def getInfo(infoType, typeStr, earth_info):
    siteName = infoType.getElementsByTagName(typeStr + 'Desc')[0]
    print ("Name: %s" % siteName.childNodes[0].data)
    siteLon = infoType.getElementsByTagName(typeStr + 'Lon')[0]
    print ("Lon: %s" % siteLon.childNodes[0].data)
    siteLat = infoType.getElementsByTagName(typeStr + 'Lat')[0]
    print ("Lat: %s" % siteLat.childNodes[0].data)
    rating = infoType.getElementsByTagName(typeStr + 'Dist')[0]
    print ("距離震央: %s公里" % rating.childNodes[0].data)
    sitePGA = infoType.getElementsByTagName(typeStr + 'PGA')[0]
    print ("PGA: %sgal" % sitePGA.childNodes[0].data)
    siteInt = infoType.getElementsByTagName(typeStr + 'Intensity')[0]
    print ("震度: %s級" % siteInt.childNodes[0].data)
    warnTime = infoType.getElementsByTagName(typeStr + 'WarningTime')[0]
    print ("抵達時間: %s秒" % warnTime.childNodes[0].data)
    msgtext = "===========地震警報({meg}級/{arriveTime}秒)===========\n{info}\n警報行政區: {siteName} \n警報座標: ({Lon}, {Lat})\n距離震央: {distant}公里\nPGA: {pga}gal\n震度: {meg}級\n抵達時間: {arriveTime}秒" .format(
        info = earth_info,
        siteName = siteName.childNodes[0].data,
        Lon = siteLon.childNodes[0].data,
        Lat = siteLat.childNodes[0].data,
        distant = rating.childNodes[0].data,
        pga = sitePGA.childNodes[0].data,
        meg = siteInt.childNodes[0].data,
        arriveTime = warnTime.childNodes[0].data)
    info.insert('1.0',msgtext)
    return msgtext


# CAP Function====================================================================================
## 建立資料前，先測試資料表是否存在
def db_Check(dbName, dbColumn):
    try:
        cur.execute("SELECT * FROM %s" %(dbName))
        #print ("Find table:%s" %(dbName))
        conn.commit()
    except:
        conn.commit()
        cur.execute("CREATE TABLE %s (%s)" %(dbName, dbColumn))
        print ("Create table %s successed!" %(dbName))
        conn.commit()
## CAP Relate資料庫讀取
def checkRelateTable(table, columnName, checkValue):
    cur.execute("SELECT * FROM %s"%table)
    raw = cur.fetchall()
    result = [f for f in raw if f[1] == checkValue]
    conn.commit()
    if result:
        relate_id = result[0][0]
    else:
        cur.execute("INSERT INTO %s (%s) VALUES ('%s') RETURNING id"%(table, columnName, checkValue))
        relate_id = cur.fetchone()[0]
        conn.commit()
    return relate_id

def initial():
    global run
    run = True
    info.insert('1.0',"{}監聽中!!\n".format(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
    startApp()

def stop():
    global run
    run = False
    info.insert('1.0', '{}暫停\n'.format(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))

def startApp():
    global run, before
    if run == True:
        # 在需要修改全域變量的函數中，需先指定該變量為全域變量global，python才會將這個變量以全域變量去執行。
        global timeCount
        # timeCount = 0
        # while 1:
        #time.sleep (1)
        # 地震警報====================================================================================
        ## 監測是否有新增地震警報
        after = dict ([(f, None) for f in os.listdir (path_to_watch+'.')])
        #print ('b:{}\na:{}'.format(before,after))
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added:
            for ear in added:
                print ("Added: ", ", ".join (added))
                difEarth(path_to_watch + ear)
        if removed: print ("Removed: ", ", ".join (removed))
        before = after
        timeCount = timeCount + 1
        if timeCount == 100:
            try:
                # print ('{}:開始抓取CAP資料'.format(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
                info.insert('1.0','{}:開始抓取CAP資料\n'.format(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
                # CAP====================================================================================
                ## 確認CAP資料庫是否存在，若無則建立資料庫
                for tableName in tableList:
                    db_Check(tableName, tableList[tableName])
                for relateTable in DB_Dic:
                    #print (relateTable)
                    db_Check(relateTable, "id serial primary key, %s varchar(50)"%(DB_Dic[relateTable]))

                ## 監測CAP訊息
                context = ssl._create_unverified_context()
                capList_url = urlopen('https://alerts.ncdr.nat.gov.tw/JSONAtomFeed.ashx?County=%E9%AB%98%E9%9B%84%E5%B8%82', context = context)
                capList_info = json.loads(capList_url.read().decode('utf-8'))
                cap_date = datetime.strptime(capList_info['entry'][0]['updated'].split('+')[0], "%Y-%m-%dT%H:%M:%S")
                api_key = 'apikey'

                ## 取得相對應id的CAP內容
                idList = []
                for cap in capList_info["entry"]:
                    cur.execute("SELECT * FROM cap_kaohsiung")
                    raw = cur.fetchall()
                    cap_id = [f for f in raw if f[1] == cap['id']]
                    conn.commit()
                    if cap_id:
                        #print ('資料已存在！')
                        pass
                    else:
                        ## 針對每一項CAP_ID的內容進行處理================================================
                        capURL = urlopen('https://alerts.ncdr.nat.gov.tw/api/dump/datastore?apikey=%s&capid=%s&format=json'%(api_key, cap['id']))
                        cap_content = json.loads(capURL.read().decode('utf-8'))
                        #cap_status = cap_content['status']
                        cap_effective = cap_content['info'][0]['effective']
                        cap_expires = cap_content['info'][0]['expires']
                        cap_headline = cap_content['info'][0]['headline']
                        cap_description = cap_content['info'][0]['description']
                        cap_instruction = cap_content['info'][0]['instruction']
                        cap_web = cap_content['info'][0]['web']
                        ## 以下參數需check Relate
                        cap_event = cap_content['info'][0]['certainty']
                        cap_responseType = cap_content['info'][0]['certainty']
                        cap_msgType = cap_content['info'][0]['certainty']
                        cap_sender = cap_content['info'][0]['senderName']
                        cap_category = cap_content['info'][0]['category']
                        cap_urgency = cap_content['info'][0]['urgency']
                        cap_severity = cap_content['info'][0]['severity']
                        cap_certainty = cap_content['info'][0]['certainty']
                        ## part of caps didn't contain alert_color
                        for para in cap_content['info'][0]['parameter']:
                            ## alert_color
                            if para['valueName'] == 'alert_color':
                                cap_alert_Color = para['value']
                            else:
                                cap_alert_Color = 'NA'
                            ## alert_title (無relate)
                            if para['valueName'] == 'alert_title':
                                cap_alert_title = para['value']
                            else:
                                cap_alert_title = None
                        ## 建立Check Dictionary
                        relateCheckList = {"cap_category": cap_category,
                                           "cap_sender": cap_sender,
                                           "cap_event": cap_event,
                                           "cap_alert_Color": cap_alert_Color,
                                           "cap_certainty": cap_certainty,
                                           "cap_urgency": cap_urgency,
                                           "cap_serverity": cap_severity,
                                           "cap_responseType": cap_responseType,
                                           "cap_msgType": cap_msgType}

                        for relateitem in DB_Dic:
                            ## 建立動態變數，如cap_catrgory_id = checkRelateTable('cap_catrgory', relateCheckList['cap_catrgory'])
                            locals()['%s_id'%relateitem] = int(checkRelateTable(relateitem, DB_Dic[relateitem], relateCheckList[relateitem]))
                            idList.append(locals()['%s_id'%relateitem])
                        ids = ', '.join(str(e) for e in idList)
                        print(ids)
                        ## 將資料存入資料庫中
                        cur.execute("""INSERT INTO cap_kaohsiung (cap_id, alert_title, effective, expires, headline, description, instruction, web, category, senderName, event, alert_color, certainty, urgency, severity, responseType, msgType) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s)"""%(cap['id'], cap_alert_title, cap_effective, cap_expires, cap_headline, cap_description, cap_instruction, cap_web, ids))
                        conn.commit()
                        idList.clear()
                        ## 傳送CAP訊息至使用者
                        capMsgText = "========%s========\n訊息種類:%s\n警報類型:%s\n%s by%s\n%s:%s\n生效時間:%s\n失效時間:%s"%(cap_headline, cap_msgType, cap_category, cap_description, cap_sender, cap_instruction, cap_web, cap_effective, cap_expires)
                        push_message(capMsgText)
            except:
                msgtext = '{time}:{capid}資料出現意外!'.format(time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), capid = cap['id'])
                # print (msgtext)
                info.insert('1.0',msgtext+'\n')
                pass
            timeCount = 0
        app.after(1000, startApp)


run = False
timeCount = 0
app = Tk()
#===========路徑功能，選擇監聽路徑
label=Label(app,text="選擇路徑：")
label.grid(row=0,column=0)
f_path = Text(app, height=1, width =60)
f_path.grid(row=0, column=1, columnspan=2)
getFolder_btn = Button(app,text='選擇地震訊息資料夾', command=browseFolder)
getFolder_btn.grid(row=0, column=3)

#===========資訊顯示區
info = Text(app)
info.grid(row=1, column=0, rowspan=4, columnspan=3)

#===========開始及結束
startButton = Button(app, text='開始監聽地震及CAP資訊', command=initial)
startButton.grid(row = 1, column = 3)
stopButton = Button(app, text='暫停', command=stop)
stopButton.grid(row = 2, column = 3)

app.mainloop()
