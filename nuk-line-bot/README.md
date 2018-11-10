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

## 執行畫面

Server端執行視窗畫面

右方為中央氣象局提供給學校單位安裝的地震警報程式，也就是nuk-line-bot抓取地震警報的來源，左上為tkinter建立的介面，主要作為操作的應用程式，左下為命令列視窗，是tkinter背景執行命令列，主要作為除錯時瞭解錯誤資訊。
![Server端視窗畫面](/DemoScreenShot/nuk-line-bot2.png)

當蒐集到CAP資訊時就會立刻傳送資料到Line聊天室，如下圖。

|手機預覽畫面|Line聊天室畫面|
|:---:|:---:|
|![LINE預覽畫面](/DemoScreenShot/nuk-line-bot3.png)|![LINE聊天室畫面](/DemoScreenShot/nuk-line-bot4.png)|

當收到警報時(共兩個範例)
警報1
  ![警報1](/DemoScreenShot/earthquakeAlarm.jpg)
警報2
  ![警報2](/DemoScreenShot/earthquakeAlarm2.jpg)

|Line警報通知1|Line警報通知2|
|:---:|:---:|
|![LINE預覽畫面](/DemoScreenShot/LineAlarm.jpg)|![LINE聊天室畫面](/DemoScreenShot/LineAlarm2.jpg)|