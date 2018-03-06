import time
from datetime import datetime, timedelta
import json
from urllib.request import urlopen
from pg import DB
from datetime import datetime, date
import pytz

#dt = datetime.now() + timedelta(hours=48)
tpe = pytz.timezone('Asia/Taipei')
utcNow = datetime.utcnow()
now = tpe.fromutc(utcNow)
thisMonth = now.strftime("%m")


db = DB(dbname='dataName',
        host='ipaddress',
        port=5432,
        user='idname',
        passwd='password')
lastUpdate = ''

def defindColumn(field):
    try:
        db.query("SELECT {0} FROM debris_10min_{1}{2}".format(field, now.year, thisMonth))
    except:
        db.query("ALTER TABLE debris_10min_{1}{2} ADD COLUMN {0} numeric(5,1)".format(field, now.year, thisMonth))
        print ("Add {0} Column!!".formate(field))


def updateTable():
    global lastUpdate
    global updateTime
    #抓取土石流網站資訊
    jsonContent = urlopen('http://246.swcb.gov.tw/webService/GetRainData.ashx').read()
    rainStationList = json.loads(jsonContent.decode("utf-8"))

    fieldName = ""
    stationList = []
    min10 = []
    #篩選高雄市雨量站
    for rainstation in rainStationList:
        if rainstation['county'] == '高雄市':
            #print (rainstation['rainStationName'])
            nameList = rainstation['rainStationName'].split('(',1)
            #print (len(nameList))
            if len(nameList) > 1:
                stationName = nameList[0] + '_' + nameList[1].split(')',1)[0]
                #print('trans to %s' % stationName)
            else:
                stationName = nameList[0]

            if rainstation['rainStationName'] == '古亭坑' and rainstation['belong'] == '局屬無人測站':
                stationName = '古亭坑_2'
            if rainstation['rainStationName'] == '東沙':
                stationName = '東沙島'
            stationList.append(stationName)
            if rainstation['min10'] == '-':
                min10.append('0')
            else:
                min10.append(rainstation['min10'])
            try:
                defindColumn(stationName)
            except:
                pass
            fieldName = " numeric(5,1), ".join(stationList) + " numeric(5,1)"

    fieldName = "updateTime varchar(30), " + "date date, " + fieldName

    #print (", ".join(stationList))
    updateTime = ''
    updateTime = rainStationList[0]['time']
    updateMes =  updateTime.split('T', 1)
    #print (fieldName)

    try:
        db.query("SELECT * FROM debris_10min_%d%s" % (now.year, thisMonth))
    except:
        db.query("""CREATE TABLE debris_10min_%d%s(id serial primary key, %s)""" % (now.year, thisMonth, fieldName))
        print ("Create table successed!")


    db.query("""INSERT INTO debris_10min_%d%s(updateTime, date, %s)
                        VALUES (%s, %s, %s)""" %(now.year, thisMonth, ", ".join(stationList) , "'" + updateMes[1] + "'", "'" + updateMes[0] + "'", ', '.join(min10)))
    print("update time: %s" % updateTime)




#updateTable()

while 1:
    try:
        jsonContent = urlopen('http://246.swcb.gov.tw/webService/GetRainData.ashx').read()
        rainStationList = json.loads(jsonContent.decode("utf-8"))
        updateTime = rainStationList[0]['time']
        #nowUpdate = "{0}-{1}-{2}T{3}:{4}0:00".format(now.year, thisMonth, now.strftime("%d"), now.hour, thisMonth[:1])
    except:
        time.sleep(10)
        continue



    try:
        lastRec = db.query("SELECT updateTime FROM debris_10min_%d%s ORDER BY id DESC LIMIT 1" % (now.year, thisMonth)).getresult()[0][0]
    except:
        lastRec = 0

    if updateTime.split('T')[1] != lastRec:
        try:
            updateTable()
            break
        except:
            time.sleep(10)
    else:
        print ('update renew!')
        time.sleep(30)
