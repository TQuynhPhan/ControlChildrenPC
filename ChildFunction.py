# Functions use for children program
# Import thêm thư viện cần thiết
from copy import copy
from msilib.schema import Environment
import os
import base64
import pandas as pd
import json
import time
from time import sleep
from datetime import datetime, timedelta
from autorun import add_to_startup
from helper import getOneDrivePath
from screenshot import take_screenshots
from MainFunctions import *

def checkUseTime(timeArr, start):
    onedrivePath = getOneDrivePath()
    # Trong thời gian sử dụng, trả về time chứa thời gian đó
    # K trong thời gian sử dụng, trả về time được sử dụng gần nhất
    arr = getUsedTimeList(onedrivePath + "/testWrite.txt")
    for timeEle in timeArr:
        usedTimeS = arr[timeArr.index(timeEle)]['usedS']
        # usedTimeD = (arr[timeArr.index(timeEle)])['usedD']
        tmpF = datetime.strptime(timeEle['F'], "%H:%M")
        tmpT = datetime.strptime(timeEle['T'], "%H:%M")
        if tmpF.time() <= datetime.now().time() < tmpT.time():
            # trường hợp time có F,T
            if timeEle['D'] == '' and timeEle['S'] == '':
                return 0, timeEle  # trong thời gian sử dụng

            # trường hợp time có F,T,S
            if timeEle['D'] == '':
                # usedTimeS=0
                # trong thời gian sử dụng
                if usedTimeS < int(timeEle['S']):
                    return 0, timeEle

                # k trong thời gian sử dụng, tắt máy khi dùng đủ S trước thời gian T
                else:
                    if timeArr.index(timeEle) == len(timeArr) - 1:  # time là phần tử cuối
                        return 1, timeArr[0]
                    return 2, timeArr[timeArr.index(timeEle) + 1]

            resTime = (tmpT - timedelta(hours=datetime.now().time().hour,
                                        minutes=datetime.now().time().minute,
                                        seconds=datetime.now().time().second)).time()
            resMinuteTime = resTime.hour * 60 + resTime.minute + resTime.second / 60
            timeD = int(timeEle['D'])

            usedTimeD = (time.time() - start) // 60

            # trường hợp time có F,T,D,I
            # trong thời gian sử dụng
            if timeEle['S'] == '':
                if usedTimeD < timeD:
                    # sẽ ngắt máy do tới thời gian T trước
                    if resMinuteTime < timeD - usedTimeD:
                        return 0, timeEle
                    # sẽ ngắt máy do dùng đủ D trước
                    return 3, timeEle
                else:  # k trong thời gian sử dụng, trong thời gian ngắt máy trong vòng I sau khi dùng đủ D trong 1 lần bật
                    return 7, arr[timeArr.index(timeEle)]

            # th time có F,T,D,I,S
            timeS = int(timeEle['S'])
            # trong thời gian sử dụng (có 3 th sẽ ngắt máy: do tới thời gian T, do dùng đủ D, do dùng đủ S)
            if usedTimeD < timeD and usedTimeS < timeS:
                minTime = [resMinuteTime, timeD - usedTimeD, timeS - usedTimeS]
                # sẽ ngắt máy do tới thời gian T trước
                if min(minTime) == resMinuteTime:
                    return 0, timeEle
                # sẽ ngắt máy do dùng đủ D trước
                if min(minTime) == timeD - usedTimeD:
                    return 3, timeEle
                # sẽ ngắt máy do dùng đủ S trước
                return 4, arr[timeArr.index(timeEle)]
            # k trong thời gian sử dụng
            else:

                # k trong thời gian sử dụng, tắt máy khi dùng đủ S trước thời gian T
                if usedTimeS + (time.time() - start) // 60 >= timeS:
                    if timeArr.index(timeEle) == len(timeArr) - 1:  # time là phần tử cuối
                        return 1, timeArr[0]
                    return 2, timeArr[timeArr.index(timeEle) + 1]

                # k trong thời gian sử dụng, ngắt máy trong vòng I sau khi dùng đủ D trong 1 lần bật
                return 7, arr[timeArr.index(timeEle)]

        if datetime.now().time() < tmpF.time():
            return 5, timeEle  # k trong thời gian sử dụng, nhỏ hơn thời gian bắt đầu trong 1 dòng

    # k trong thời gian sử dụng, lớn hơn thời gian T cuối cùng (tính thời gian trước 12h, vì là 12h thì tính là 0h)
    return 6, timeArr[0]
    # res=0,3,4: trong thời gian sử dụng
    # res=1,2,5,6,7: k trong thời gian sử dụng


def calcNextUseTime(res, timeEle):  # chỉ tính trong thời gian trẻ k được dùng máy
    tmpF = datetime.strptime(timeEle['F'], "%H:%M")
    if res == 1:  # k trong thời gian sử dụng, th tắt máy khi dùng đủ S trước thời gian T
        if datetime.now().time() < datetime.strptime("0:00", "%H:%M").time():
            nextUseTime = datetime.strptime("0:00", "%H:%M") + timedelta(hours=tmpF.time().hour,
                                                                        minutes=tmpF.time().minute,
                                                                        seconds=tmpF.time().second)
        else:
            nextUseTime = tmpF
    elif res == 2 or res == 5:
        nextUseTime = tmpF
    elif res == 6:
        nextUseTime = datetime.strptime("0:00", "%H:%M") + timedelta(hours=tmpF.time().hour,
                                                                    minutes=tmpF.time().minute,
                                                                    seconds=tmpF.time().second)

    elif res == 7:
        nextUseTime = datetime.strptime(timeEle['breakTimeI'], "%H:%M") + timedelta(minutes=int(timeEle['I']))

    return nextUseTime.time()


def calcShutdownTime(res, timeEle, start):  # trong thời gian trẻ được dùng máy
    if res == 0:
        tmpT = datetime.strptime(timeEle['T'], "%H:%M")
        shutdownTime = timedelta(hours=tmpT.hour, minutes=tmpT.minute) - timedelta(hours=datetime.now().hour,
                                                                                    minutes=datetime.now().minute,
                                                                                    seconds=datetime.now().second)
    elif res == 3:
        usedTimeD = timedelta(minutes=((time.time() - start) // 60))
        D = timedelta(minutes=int(timeEle['D']))
        if (D > usedTimeD):
            shutdownTime = D - usedTimeD
        else:
            shutdownTime = timedelta(seconds=15)
    elif res == 4:
        usedTimeS = timedelta(minutes=(timeEle['usedS'] + (time.time() - start) // 60))
        S = timedelta(minutes=int(timeEle['S']))
        if (S > usedTimeS):
            shutdownTime = S - usedTimeS
        else:
            shutdownTime = timedelta(seconds=15)

    return shutdownTime  # phút

def updateTestFile(start, res,timeArr, timeEle,arr):
    onedrivePath = getOneDrivePath()
    idx = timeArr.index(timeEle)
    if res == 3:  # dừng máy do đủ D
        for i in range(len(arr)):
            if i == idx:
                arr[i]['breakTimeI'] = datetime.now().strftime("%H:%M")
            else:
                arr[i]['breakTimeI'] = ''
    else:
        for i in range(len(arr)):
            arr[i]['breakTimeI'] = ''

    # ghi phần usedS
    for i in range(len(arr)):
        if i == idx:
            arr[i]['usedS'] = int(arr[i]['usedS'] + (time.time() - start) // 60)
        else:
            arr[i]['usedS'] = 0
    writeFile(onedrivePath + "/testWrite.txt", arr)

def checkUpdateTimeFile(onedrivePath, timeArr, timeEle, arr, res, start):
    timeArrNew=getTimeList(onedrivePath)
    if timeArr!=timeArrNew:
        newArr = copy(timeArrNew)
        # Thêm
        if len(timeArr)<len(timeArrNew):
            if res == 3:  # dừng máy do đủ D
                for t in newArr:
                    if t['F'] == timeEle['F'] and t['T'] == timeEle['T']:
                        t['breakTimeI'] = datetime.now().strftime("%H:%M")
                    else:
                        t['breakTimeI'] = ''
            else:
                for t in newArr:
                    t['breakTimeI'] = ''
            # ghi phần usedS
            for t in newArr:
                if t['F'] == timeEle['F'] and t['T'] == timeEle['T']:
                    t['usedS'] = arr[newArr.index(t)]['usedS'] + (time.time() - start) // 60
                else:
                    t['usedS'] = 0
            res = 'add'
        # Xóa
        elif len(timeArr)>len(timeArrNew):
            if timeEle not in timeArrNew:
                idx = timeArr.index(timeEle)
                arr.pop(idx)
                res = 'del-1'
            else:
                res = 'del-2'
        #Sửa
        else:
            if timeEle in timeArrNew:
                idx = timeArrNew.index(timeEle)
            else:
                idx = 0
                for i in range(len(timeArr)):
                    if timeArr[i] != timeArrNew[i]:
                        idx = i
                        break
            if res == 3:  # dừng máy do đủ D
                for i in range(len(newArr)):
                    if i == idx:
                        newArr[i]['breakTimeI'] = datetime.now().strftime("%H:%M")
                    else:
                        newArr[i]['breakTimeI'] = ''
            else:
                for i in range(len(newArr)):
                    newArr[i]['breakTimeI'] = ''

            # ghi phần usedS
            for i in range(len(newArr)):
                if i == idx:
                    newArr[i]['usedS'] = arr[i]['usedS'] + (time.time() - start) // 60
                else:
                    newArr[i]['usedS'] = 0
            res = 'update'

        writeFile(onedrivePath + "/testWrite.txt",newArr)
        timeArr.clear()
        for i in timeArrNew:
            timeArr.append(i)
        if 'del' not in res:
            arr.clear()
            for i in newArr:
                arr.append(i)
        return res
    else:
        return None

