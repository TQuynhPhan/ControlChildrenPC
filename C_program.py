from ast import Global
import os
# from signal import SIGABRT
from tkinter import *
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox
import time
from datetime import datetime, timedelta
import multiprocessing
from threading import Timer
from MainFunctions import *
from ChildFunction import *
from screenshot import take_screenshots
from helper import getOneDrivePath

countdownThread = None
start = time.time()

def disable_exit():
    pass

def forceShutdown():
    os.system("shutdown /s /t 1")

def update_clock(new_time, show, win=None, time_reuse=None, shutDown=True):
    show.config(text=f'{new_time}')
    if new_time==timedelta(0):
        win.destroy()
        if shutDown==True:
            # Shut down
            os.system("shutdown /s /t 1")
            # print('shutdown')
        return
    if time_reuse!=None and new_time<=timedelta(minutes=1):
        noti = Label(win, text=f'Computer is able to be used at {time_reuse.hour:02.0f}:{time_reuse.minute:02.0f}', font=tkFont.Font(size = 12))
        noti.place(x=7, y=55)
        show.config(fg='red')
        win.geometry('420x100+0+0')
        win.wm_deiconify()
        time_reuse = None

    new_time -= timedelta(seconds=1)
    show.after(1000, update_clock, new_time, show, win, time_reuse, shutDown)

def countdown(time_remain, time_reuse=None):
    win = Tk()
    win.title('Countdown')
    win.protocol("WM_DELETE_WINDOW", disable_exit)
    win.geometry('400x70+0+0')
    win.resizable(False, False)

    info_text = Label(text='Time remains:', font=tkFont.Font(size = 15))
    info_text.place(x=50, y=14)

    time_text = Label(text='', font=tkFont.Font(size = 15))
    time_text.place(x=250, y=14)

    if time_reuse==None:
        update_clock(time_remain, time_text, win, shutDown=False)
    else:
        update_clock(time_remain, time_text, win, time_reuse)

    win.mainloop()

def lock_computer():
    win = Tk()
    win.title('Locked')
    w = win.winfo_screenwidth()
    h = win.winfo_screenheight()
    win.geometry(f'{w}x{h}+0+0')
    win.overrideredirect(True)
    win.state('zoomed')

    lock_noti = Label(text='This computer is locked for 10 minutes!', font=tkFont.Font(size = 30), fg='red')
    lock_noti.place(x=500, y=200)

    countdown_label = Label(text='Shut down in:', font=tkFont.Font(size = 28))
    countdown_label.place(x=800, y=400)

    countdown_time = Label(text='', font=tkFont.Font(size = 28))
    countdown_time.place(x=870, y=500)
    
    update_clock(timedelta(minutes=10), countdown_time, win)
    # update_clock(timedelta(seconds=5), countdown_time, win)     # test

    win.mainloop()

def child_program():
    # Count numbers of getting wrong password
    cnt = [0]

    win = Tk()
    win.title('Parental Control')

    # Set size and position
    w, h = 500, 240
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width//2) - (w//2)
    y = (screen_height//2) - (h//2)
    win.geometry('%dx%d+%d+%d' % (w, h, x, y))
    win.resizable(False, False)
    # Prevent closing program
    win.protocol("WM_DELETE_WINDOW", disable_exit)
    win.overrideredirect(True)

    announce = Label(text='Enter Password', font=tkFont.Font(size = 15))
    announce.grid(row=0, column=0, columnspan=5, padx=10, pady=20)

    password = Entry(show='*', width=33, font=tkFont.Font(size = 13))
    password.grid(row=1, column=0, columnspan=5, padx=15, pady=15)

    def getPasswordAndCheck():
        global countdownThread
        inputPass = password.get()
        onedrivePath = getOneDrivePath().strip()

        if countdownThread!=None:
            countdownThread.kill()
            countdownThread=None

        # Parent's password
        if checkPassword(onedrivePath+'/ParentPassword.txt', inputPass):
            # Parent are using child's computer
            win.destroy()
            # countdown(timedelta(seconds=5))
            countdown(timedelta(hours=1))       # Use for 1 hour
            child_program()
        # Not parent
        else:
            global start
            # Get list of using time from time.txt
            timeArr = getTimeList(onedrivePath)
            res, timeEle = checkUseTime(timeArr, start)
            
            # Not in using time
            if res == 1 or res == 2 or res == 5 or res == 6 or res == 7:
                messagebox.showwarning("Can't use", "Children are not allowed to use the computer right now!")
                nextUseTime = calcNextUseTime(res, timeEle)
                # multiprocessing to (1)countdown 15sec and (2)ask password again
                subprocess = multiprocessing.Process(target=countdown, args=(timedelta(seconds=15), nextUseTime))
                subprocess.daemon = True
                countdownThread = subprocess
                subprocess.start()

            # In using time
            else:
                # Correct password
                if checkPassword(onedrivePath+'/ChildrenPassword.txt', inputPass):
                    # Calculate minutes left
                    shutdownTime = calcShutdownTime(res, timeEle, start)
                    # Find next usimg time
                    arr = getUsedTimeList(onedrivePath + "/testWrite.txt")
                    if res == 0:  # dừng do tới thời gian T
                        if timeArr.index(timeEle) == len(timeArr) - 1:
                            turnOnTime = datetime.strptime((timeArr[0])['F'], "%H:%M")
                        else:
                            turnOnTime = datetime.strptime((timeArr[timeArr.index(timeEle) + 1])['F'], "%H:%M")

                    if res == 4:  # dừng do dùng đủ S
                        if timeArr.index(timeEle) == len(arr) - 1:
                            turnOnTime = datetime.strptime((arr[0])['F'], "%H:%M")
                        else:
                            turnOnTime = datetime.strptime((arr[arr.index(timeEle) + 1])['F'], "%H:%M")

                    if res == 3:  # dừng do dùng đủ D
                        # ngắt máy trong thời gian I, đến khi có thể bật lại thì vượt quá thời gian T
                        idx = timeArr.index(timeEle)
                        if (datetime.now() + timedelta(minutes=int(arr[idx]['I']))).time() >= (
                        datetime.strptime((arr[idx])['T'], "%H:%M")).time():
                            if idx == len(arr) - 1:
                                turnOnTime = datetime.strptime((arr[0])['F'], "%H:%M")
                            else:
                                turnOnTime = datetime.strptime((arr[idx + 1])['F'], "%H:%M")
                        else:  # ngắt đủ I xong có thể bật lên lại
                            turnOnTime = datetime.now() + timedelta(minutes=int((arr[idx])['I']))
                            turnOnTime.replace(microsecond=0)
                    win.destroy()
                    # multiprocessing to (1)countdown and (2)take screenshot
                    sub1 = multiprocessing.Process(target=countdown, args=(shutdownTime, turnOnTime.time()))
                    sub2 = multiprocessing.Process(target=take_screenshots, args=(onedrivePath+'/Screenshot',))
                    sub3 = Timer(shutdownTime.total_seconds()-1.0, updateTestFile, args=[start,res,timeArr,timeEle,arr])
                    sub2.daemon = True
                    sub1.start()
                    sub2.start()
                    sub3.start()
                    sub1.join()
                    check = False
                    while sub1.is_alive():
                        ans = checkUpdateTimeFile(onedrivePath, timeArr, timeEle, arr, res, start)
                        if ans!=None and ans!='del-2':
                            sub1.kill()
                            sub2.kill()
                            sub3.cancel()
                            check = True
                            break
                        time.sleep(5)
                    if check:
                        child_program()
                # Wrong password
                else:
                    messagebox.showerror('Notification', 'Wrong password!')
                    cnt[0] += 1
                    # Wrong password 3 times
                    if cnt[0] == 3:
                        win.destroy()
                        lock_computer()

    
    # Enter button, get password from user and check
    enter_btn = Button(text='Enter', width=12, font=tkFont.Font(size = 11), command=getPasswordAndCheck)
    enter_btn.grid(row=2, column=1, padx=10, pady=20)

    btn_quit = Button(text="Shut down", width=12, font=tkFont.Font(size = 11), command=forceShutdown)
    btn_quit.grid(row=2, column=3, padx=10, pady=20)

    win.mainloop()

def main():
    child_program()

if __name__ == "__main__":
    main()