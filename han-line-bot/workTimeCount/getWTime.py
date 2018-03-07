def transTime(workTime):
    if int(workTime) < 1000 :
        hourTime = int(workTime[:1])
    else :
        hourTime = int(workTime[:2])
    minuteTime = int(workTime[-2:]) / 60
    resultT = hourTime + minuteTime
    return resultT


def halfHour(countingNumber):
    roundTime = round(countingNumber, 0)

    if roundTime <= countingNumber :
        halfCount = int(countingNumber)
    elif roundTime > countingNumber :
        halfCount = int(countingNumber) + 0.5

    return halfCount