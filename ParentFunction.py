# Functions use for parent program
from copy import copy
from time import sleep
from MainFunctions import *
from helper import getOneDrivePath

def checkTimeEle(x, y):
    if x['F']!=y['F']:
        return False
    if x['T']!=y['T']:
        return False
    if x['D']!=y['D']:
        return False
    if x['I']!=y['I']:
        return False
    if x['S']!=y['S']:
        return False
    return True

def updateFiletest(file, timeArr):
    arr = getUsedTimeList(file, False)
    f = open(file, 'w')
    # Delete
    if len(timeArr) < len(arr):
        for timeEle in arr:
            for row in timeArr:
                if checkTimeEle(timeEle, row):
                    f.write(json.dumps(timeEle))
                    f.write("\n")
                    break
    # Update / Add
    else:
        for row in timeArr:
            check = False
            for timeEle in arr:
                # Old time
                if checkTimeEle(timeEle, row):
                    f.write(json.dumps(timeEle))
                    f.write("\n")
                    check = True
                    break
            # New time
            if not check:
                info = copy(row)
                info['breakTimeI'] = ''
                info['usedS'] = 0
                f.write(json.dumps(info))
                f.write("\n")
    f.close()

def  updateTimeFile(timeArr):
    onedrivePath = getOneDrivePath()
    onedriveTimeFile, onedriveFlag = onedrivePath + '/time.txt', onedrivePath + '/flag.txt'
    if checkingFlag(onedriveFlag):  # đọc được là 1 tức là có người đang trong miền găng
        while checkingFlag(onedriveFlag):
            # đợi 5 đọc lại
            sleep(5)
    setFlag(onedriveFlag, '1')  # set cờ là 1
    writeTimeFile(onedriveTimeFile,timeArr)
    updateFiletest(onedrivePath + '/testWrite.txt', timeArr)
    setFlag(onedriveFlag, '0')  # viết xong set ngược lại cờ là 0
    return 0
