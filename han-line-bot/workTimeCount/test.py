from workTimeCount.getWTime import transTime, halfHour
text = '1000-1730'
timeAnaly = text.split('-')
print(len(text))
workTime = transTime(timeAnaly[1]) - transTime(timeAnaly[0])
replyText = halfHour(workTime)
print('結果')
print(replyText)