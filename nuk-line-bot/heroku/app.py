# encoding: utf-8
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
# 使用postgresQL資料庫
import psycopg2

conn = psycopg2.connect(database="linedatabasename",
                        user="username",
                        password="pass",
                        host="hostname",
                        port="5432")
cur = conn.cursor()

# 建立資料前，先測試資料表是否存在
try:
    cur.execute("SELECT * FROM push_list")
    print ("Find push list")
    conn.commit()
except:
    conn.commit()
    cur.execute("""CREATE TABLE push_list
                (id serial primary key,
                idtype varchar(50),
                userid varchar(50))
                """)
    print ("Create table successed!")
    conn.commit()


app = Flask(__name__)

line_bot_api = LineBotApi('LineBotApiaccesstoken')
handler = WebhookHandler('Channel Secret') #Your Channel Secret

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text #message from user
    user_id = event.source.user_id
    id_type = event.source.type
#    print ("user_id:%s\ntext:%s" %(user_id, line_id, text))
    if text == "地震":
        ##新增已經入資料庫之判別
        cur.execute('SELECT * FROM push_list')
        rows = cur.fetchall()
        result = [row for row in rows if row == user_id]
        if result:
            # 將user_id加入資料庫中
            cur.execute("""INSERT INTO push_list (userid, idtype) VALUES ('%s', '%s')""" %(user_id, id_type))
            conn.commit()
            replyText = "已加入地震警報通知名單"
        else:
            replyText = "您已經在通知名單中"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=replyText))
import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
