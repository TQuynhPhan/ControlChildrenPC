# Functions used for both C_Program and P_Program
import pandas as pd
import json
import time
import os
from datetime import datetime, date

def checkPassword(fileName, password):
    with open(fileName, "r") as f:
        line = f.readline().strip()
        if password == line:
            return True
    return False

def checkInLine(line, c):  # check các kí tự F,T,D,I,S có trong dòng line trong text file
    for i in line.split():
        if c == i[0]:
            return i
    return -1

def writeTimeFile(fileName, TimeArr):
    f = open(fileName, 'w')
    arr = ['F', 'T', 'D', 'I', 'S']
    for timeEle in TimeArr:
        for char in arr:
            if char in timeEle:
                if timeEle[char]!='':
                    f.write(f'{char}{timeEle[char]} ')
        f.write('\n')
    f.close()

def readTimeFile(link):
    timeArr = []
    arr = ['F', 'T', 'D', 'I', 'S']
    f = pd.read_csv(link, header=None)
    for i in range(f.index.start, f.index.stop):
        timeEle = {}
        for c in arr:
            check = checkInLine(f.loc[i][0], c)
            if check == -1:
                timeEle[c] = ''
            else:
                timeEle[c] = check[1:]
        timeArr.append(timeEle)
    return timeArr

def writeFile(fileName, timeArr):
    with open(fileName, "w") as f:
        for timeEle in timeArr:
            f.write(json.dumps(timeEle))
            f.write("\n")

def readFile(fileName):
    arr = []
    with open(fileName, "r") as f:
        for i in f.readlines():
            arr.append(json.loads(i))
    return arr

def setFlag(fileFlagLink, theFlag):
    file = open(fileFlagLink, "w+")
    file.write(theFlag)  # Write new flag
    file.close()

def checkingFlag(fileFlagLink):
    file = open(fileFlagLink, "r")
    flag = file.read()
    file.close()
    return int(flag)  # Convert string to integer

def getTimeList(onedrivePath):
    # Check critical section
    if checkingFlag(onedrivePath+'/flag.txt'):  # Getting 1 means there is a subprocess in critical section
        while checkingFlag(onedrivePath+'/flag.txt'):
            time.sleep(5)        # Wait 5sec, then read flag again
    setFlag(onedrivePath+'/flag.txt', '1')  # set flag=1
    timeArr = readTimeFile(onedrivePath+'/time.txt')
    setFlag(onedrivePath+'/flag.txt', '0')  # set flag=0
    return timeArr

def resetTimeUse(file, rewrite = True):
    arr = readFile(file)
    for info in arr:
        info['breakTimeI'] = ''
        info['usedS'] = 0
    if rewrite:
        writeFile(file, arr)
    return arr

def getUsedTimeList(file, rewrite = True):
    file_date = time.ctime(os.path.getmtime(file))
    file_date = datetime.strptime(file_date, "%a %b %d %H:%M:%S %Y").date()
    today = date.today()
    if today!=file_date:
        arr = resetTimeUse(file, rewrite)
    else:
        arr = readFile(file)
    return arr