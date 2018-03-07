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

from color.getColor import colorRequest
from workTimeCount.getWTime import transTime, halfHour
import requests
from time import strftime, localtime, sleep
from datetime import datetime, date
import pytz

#建立AI機器人
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

chatbot = ChatBot(
    "DoBe",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database='./dobe_ai.sqlite3',
    )

# 設定訓練
chatbot.set_trainer(ChatterBotCorpusTrainer)
# 使用中文语料库训练它
chatbot.train("chatterbot.corpus.tchinese")

app = Flask(__name__)

line_bot_api = LineBotApi('Your Channel Access Token') #Your Channel Access Token
handler = WebhookHandler('Your Channel Secret') #Your Channel Secret

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
    timeAnaly = text.split('-')

    if text == "color" or  text == "顏色":
        getdate, gColor, bColor = colorRequest()
        replyText = ('%s，吉色：%s，忌色：%s' % (getdate, gColor, bColor))
    elif len(text) == 9 and len(timeAnaly) == 2:
        workTime = transTime(timeAnaly[1]) - transTime(timeAnaly[0])
        replyText = halfHour(workTime)
    else:
        try:
            bot_respose = chatbot.get_response(text)
            replyText = bot_respose.text
        except(KeyboardInterrupt, EOFError, SystemExit):
            pass

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=replyText))
import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
