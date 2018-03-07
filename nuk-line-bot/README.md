# Line Bot for NUKDPC

> 只傳送高雄地區


## 提供服務

- 使用者加入好友後，輸入`地震`，BOT便將對方的user_id加入資料庫中，以後有警報時，將警報傳送給資料庫中的所有user_id
- 若發布地震警報會立刻將資料傳送到LINE的聊天室中(包含地震發生的地點＋預計震波抵達秒數)
- 將高雄市範圍之CAP存入資料庫中，並傳送到LINE聊天室。

## 環境

1. Heroku（存取`地震`資訊)
2. Server On Windows
    > 透過tkinter建立應用程式，在Windows上執行抓取地震警報資訊及CAP資訊
3. line-bot-python-heroku
