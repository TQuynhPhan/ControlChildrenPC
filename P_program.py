import os
from tkinter import *
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk,Image, ImageFile
from datetime import date, datetime, timedelta
import time
from MainFunctions import *
from ParentFunction import updateTimeFile
from helper import getOneDrivePath

ImageFile.LOAD_TRUNCATED_IMAGES = True

def changePass(win, onedrivePath, oldPass, newPass, confirmPass, kind='parent'):
    # Check blank
    if oldPass=='' or newPass=='' or confirmPass=='':
        messagebox.showwarning('Warning', 'Password cannot be blank!', parent=win)
        return

    # Check current password and new password
    if oldPass==newPass:
        messagebox.showwarning('Warning', 'New password cannot be the same as current password!', parent=win)
        return

    # Check new password and confirm password
    if newPass!=confirmPass:
        messagebox.showwarning('Warning', 'New password and confirm password must be the same!', parent=win)
        return

    filePFlag = onedrivePath + '/Pflag.txt'
    filePPass = onedrivePath + '/ParentPassword.txt'
    fileCFlag = onedrivePath + '/Cflag.txt'
    fileCPass = onedrivePath + '/ChildrenPassword.txt'

    if checkingFlag(filePFlag):
        while checkingFlag(filePFlag):
            time.sleep(5)
    setFlag(filePFlag, '1')
    if checkingFlag(fileCFlag):
        while checkingFlag(fileCFlag):
            time.sleep(5)
    setFlag(fileCFlag, '1')
    
    with open(fileCPass, 'r') as f:
        CPass = f.readline().strip()
    with open(filePPass, 'r') as f:
        PPass = f.readline().strip()
    if kind=='parent':
        # Check current password
        if PPass!=oldPass:
            messagebox.showerror('Error', 'Wrong Password!', parent=win)
            setFlag(filePFlag, '0')  # set lại cờ là 0
            setFlag(fileCFlag, '0')
            return
        if newPass==CPass:
            messagebox.showwarning('Warning', "Parent's password and children's password cannot be the same!", parent=win)
            setFlag(filePFlag, '0')  # set lại cờ là 0
            setFlag(fileCFlag, '0')
            return
        with open(filePPass, 'w') as f:
            f.write(newPass)
        messagebox.showinfo('Notification', 'Success!', parent=win)
    else:
        # Check current password
        if CPass!=oldPass:
            messagebox.showerror('Error', 'Wrong Password!', parent=win)
            setFlag(filePFlag, '0')  # set lại cờ là 0
            setFlag(fileCFlag, '0')
            return
        if newPass==PPass:
            messagebox.showwarning('Warning', "Parent's password and children's password cannot be the same!", parent=win)
            setFlag(filePFlag, '0')  # set lại cờ là 0
            setFlag(fileCFlag, '0')
            return
        with open(fileCPass, 'w') as f:
            f.write(newPass)
        messagebox.showinfo('Notification', 'Success!', parent=win)
        
    win.destroy()

    setFlag(fileCFlag, '0')
    setFlag(filePFlag, '0')

def change_password(onedrivePath, kind='parent'):
    pass_win = Toplevel()
    if kind=='parent':
        pass_win.title(" Change Parent's Password")
    else:
        pass_win.title(" Change Children's Password")
    pass_win.geometry('500x250+310+170')
    pass_win.resizable(False, False)
    # pass_win.iconbitmap('icons/key.ico')

    old_title = Label(pass_win, text='Current password:', font=tkFont.Font(size = 14))
    old_title.place(x=20, y=23)
    old_pass = Entry(pass_win, width=27, font=tkFont.Font(size = 13), show='*')
    old_pass.place(x=225, y=27)

    new_title = Label(pass_win, text='New password:', font=tkFont.Font(size = 14))
    new_title.place(x=20, y=73)
    new_pass = Entry(pass_win, width=27, font=tkFont.Font(size = 13), show='*')
    new_pass.place(x=225, y=77)

    confirm_title = Label(pass_win, text='Confirm password:', font=tkFont.Font(size = 14))
    confirm_title.place(x=20, y=123)
    confirm_pass = Entry(pass_win, width=27, font=tkFont.Font(size = 13), show='*')
    confirm_pass.place(x=225, y=127)

    btn = Button(pass_win, text='Save change', width=15, font=tkFont.Font(size = 14), command=lambda: changePass(pass_win, onedrivePath, old_pass.get(), new_pass.get(), confirm_pass.get(), kind))
    btn.place(x=155, y=185)

    pass_win.mainloop()

def show_screenshot(screenshotPath):
    folder = filedialog.askdirectory(initialdir=screenshotPath)
    pics = os.listdir(folder)
    if len(pics)==0:
        messagebox.showinfo('Notice','No screenshot found!')
        return
    folder += '/'
    curr = [0]

    slideShow = Toplevel()
    slideShow.title(f' Day: {folder[len(folder)-11:len(folder)-1]}')
    slideShow.geometry('900x560+230+70')
    slideShow.resizable(False, False)
    # slideShow.iconbitmap('icons/picture.ico')

    img = ImageTk.PhotoImage((Image.open(folder+pics[0])).resize((850,500)))
    show = Label(slideShow, image=img)
    show.place(x=25, y =10)

    name = Label(slideShow, text=datetime.strptime(pics[0][:8],'%H-%M-%S').strftime('%H:%M:%S'), font=tkFont.Font(size = 14))
    name.place(x=420, y=523)

    def next_img():
        curr[0] = (curr[0] + 1) % len(pics)
        img = ImageTk.PhotoImage((Image.open(folder+pics[curr[0]])).resize((850,500)))
        show.configure(image=img)
        show.image = img
        name.config(text=datetime.strptime(pics[curr[0]][:8],'%H-%M-%S').strftime('%H:%M:%S'))

    next_btn = Button(slideShow, text='>>', command=next_img, width=7)
    next_btn.place(x=730, y=523)

    def prev_img():
        curr[0] = (curr[0] - 1 + len(pics)) % len(pics)
        img = ImageTk.PhotoImage((Image.open(folder+pics[curr[0]])).resize((850,500)))
        show.configure(image=img)
        show.image = img
        name.config(text=datetime.strptime(pics[curr[0]][:8],'%H-%M-%S').strftime('%H:%M:%S'))

    prev_btn = Button(slideShow, text='<<', command=prev_img, width=7)
    prev_btn.place(x=120, y=523)

    slideShow.mainloop()

def show_time_list(view, timeArr):
    cnt = 0
    for info in timeArr:
        cnt += 1
        view.insert(parent='', index='end', iid=cnt, text=cnt, values=(info['F'],info['T'],info['D'],info['I'],info['S']))

def delete_time(view, timeArr):
    selected = [timeArr[int(i)-1] for i in view.selection()]
    for row in selected:
        timeArr.remove(row)
    for child in view.get_children():
        view.delete(child)
    # Update list mới vào file
    updateTimeFile(timeArr)
    show_time_list(view, timeArr)

def add_time(view, timeArr):
    add_win = Toplevel()
    add_win.title(' Add Time')
    add_win.geometry('300x300+400+200')
    # add_win.iconbitmap('icons/add.ico')
    add_win.resizable(False, False)

    f_title = Label(add_win, text='From\t             :', font=tkFont.Font(size = 16))
    f_title.place(x=30, y =30)
    f_hour = Spinbox(add_win, from_=0, to=23, wrap=True, width=3, font=tkFont.Font(size = 14), format='%02.0f')
    f_hour.place(x=141, y=33)
    f_min = Spinbox(add_win, from_=0, to=59, wrap=True, width=3, font=tkFont.Font(size = 14), format='%02.0f')
    f_min.place(x=228, y=33)

    t_title = Label(add_win, text='To\t             :', font=tkFont.Font(size = 16))
    t_title.place(x=30, y =70)
    t_hour = Spinbox(add_win, from_=0, to=23, wrap=True, width=3, font=tkFont.Font(size = 14),format='%02.0f')
    t_hour.place(x=141, y=72)
    t_min = Spinbox(add_win, from_=0, to=59, wrap=True, width=3, font=tkFont.Font(size = 14),format='%02.0f')
    t_min.place(x=229, y=72)

    d_title = Label(add_win, text='Duration\t               mins', font=tkFont.Font(size = 16))
    d_title.place(x=30, y=110)
    d_val = Entry(add_win, width=5, font=tkFont.Font(size = 16))
    d_val.place(x=141, y=110)

    i_title = Label(add_win, text='Interrupt\t               mins', font=tkFont.Font(size = 16))
    i_title.place(x=30, y=150)
    i_val = Entry(add_win, width=5, font=tkFont.Font(size = 16))
    i_val.place(x=141, y=150)

    s_title = Label(add_win, text='Total time\t               mins', font=tkFont.Font(size = 16))
    s_title.place(x=30, y=190)
    s_val = Entry(add_win, width=5, font=tkFont.Font(size = 16))
    s_val.place(x=141, y=190)

    def add_new_time():
        try:
            f = f'{int(f_hour.get()):02.0f}:{int(f_min.get()):02.0f}'
            t = f'{int(t_hour.get()):02.0f}:{int(t_min.get()):02.0f}'
            if datetime.strptime(t, "%H:%M") - datetime.strptime(f, "%H:%M") < timedelta(minutes=2):
                raise ValueError
            info = {'F': f, 'T': t, 'D':d_val.get(), 'I':i_val.get(), 'S':s_val.get()}
            if info['D']=='':
                info['I'] = ''
            else:
                if info['I']=='':
                    info['I'] = '5'
            if info in timeArr:
                messagebox.showwarning(title='Existed Time', message='Same value already!', parent=add_win)
                return
            d_val.delete(0, END)
            i_val.delete(0, END)
            s_val.delete(0, END)
            timeArr.append(info)
            timeArr.sort(key=lambda x: f"{x['F']}{x['T']}")
            # Remove all item in treeview
            for row in view.get_children():
                view.delete(row)
            # Update list mới vào file
            updateTimeFile(timeArr)
            # Show new list
            show_time_list(view, timeArr)
        except:
            messagebox.showerror(title='Invalid', message='Invalid value', parent=add_win)
    add_btn = Button(add_win, text='Add', font=tkFont.Font(size = 14), command=add_new_time)
    add_btn.place(x=120, y=240)

    add_win.mainloop()

def updateTime(update_win, view, f_hour, f_min, t_hour, t_min, d, i, s, timeArr, idx):
    try:
        f = f'{int(f_hour):02.0f}:{int(f_min):02.0f}'
        t = f'{int(t_hour):02.0f}:{int(t_min):02.0f}'
        if datetime.strptime(t, "%H:%M") - datetime.strptime(f, "%H:%M") < timedelta(minutes=2):
            raise ValueError
        info = {'F': f, 'T': t, 'D':d, 'I':i, 'S':s}
        if info['D']=='':
            info['I'] = ''
        else:
            if info['I']=='':
                info['I'] = '5'
        idx = int(idx) - 1
        if info==timeArr[idx]:
            messagebox.showinfo(title='Update', message='There is nothing new!', parent=update_win)
            return
        else:
            if info in timeArr:
                messagebox.showwarning(title='Update', message='Same value already!', parent=update_win)
                return
            update_win.destroy()
            timeArr[idx] = info
            timeArr.sort(key=lambda x: f"{x['F']}{x['T']}")
            # Remove all item in treeview
            for row in view.get_children():
                view.delete(row)
            # Update list mới vào file
            updateTimeFile(timeArr)
            # Show new list
            show_time_list(view, timeArr)
    except:
        messagebox.showerror(title='Invalid', message='Invalid value!', parent=update_win)

def parent_program(onedrivePath):
    win = Tk()
    win.title(' Parental Control')
    win.geometry('700x500+200+50')
    win.resizable(False, False)
    # win.iconbitmap('icons/chars.ico')

    timeArr = readTimeFile(onedrivePath + '/time.txt')

    menu = Menu(win)
    win.config(menu=menu)
    # Change password button
    menu.add_command(label="Parent's Password", command=lambda: change_password(onedrivePath, 'parent'))
    menu.add_command(label="Children's Password", command=lambda: change_password(onedrivePath, 'children'))

    navigation = LabelFrame(win, text='Control', padx=30, pady=10)
    navigation.pack(padx=15, pady=15)
    # Add button
    add_btn = Button(navigation, text='Add Time', font=tkFont.Font(size = 14), command=lambda: add_time(list_time, timeArr))
    add_btn.pack(side=LEFT, padx=(15,10), pady=(5,15))
    # Delete button
    del_btn = Button(navigation, text='Delete Time', font=tkFont.Font(size = 14), command=lambda: delete_time(list_time, timeArr))
    del_btn.pack(side=LEFT, padx=30, pady=(5,15))
    # Show screenshot button
    show_img_btn = Button(navigation, text='Show screenshots', font=tkFont.Font(size = 14), command=lambda: show_screenshot(onedrivePath + '/Screenshot'))
    show_img_btn.pack(side=LEFT, padx=(15,10), pady=(5,15))

    list_time = ttk.Treeview(win, height=14)
    list_time.pack(padx=25, pady=20)
    list_time['columns'] = ('From', 'To', 'Duration', 'Interrupt', 'Total')
    # format columns
    list_time.column('#0', width=50, minwidth=30, anchor=CENTER)
    list_time.column('From', width=100, minwidth=50, anchor=CENTER)
    list_time.column('To', width=100, minwidth=50, anchor=CENTER)
    list_time.column('Duration', width=120, minwidth=50, anchor=CENTER)
    list_time.column('Interrupt', width=120, minwidth=50, anchor=CENTER)
    list_time.column('Total', width=120, minwidth=50, anchor=CENTER)
    # create headings
    list_time.heading('#0', text='#', anchor=CENTER)
    list_time.heading('From', text='From', anchor=CENTER)
    list_time.heading('To', text='To', anchor=CENTER)
    list_time.heading('Duration', text='Duration', anchor=CENTER)
    list_time.heading('Interrupt', text='Interrupt Time', anchor=CENTER)
    list_time.heading('Total', text='Total Time', anchor=CENTER)

    show_time_list(list_time, timeArr)

    # Bindings treeview (update time)
    def update_time(event):
        update_win = Toplevel()
        update_win.title(' Update Time')
        update_win.geometry('300x300+400+200')
        # update_win.iconbitmap('icons/add.ico')
        update_win.resizable(False, False)

        idx = list_time.focus()
        row = list_time.item(idx,'values')
        f_hour_str = StringVar()
        f_hour_str.set(row[0][:2])
        f_min_str = StringVar()
        f_min_str.set(row[0][3:5])
        t_hour_str = StringVar()
        t_hour_str.set(row[1][:2])
        t_min_str = StringVar()
        t_min_str.set(row[1][3:5])

        f_title = Label(update_win, text='From\t             :', font=tkFont.Font(size = 16))
        f_title.place(x=30, y =30)
        f_hour = Spinbox(update_win, textvariable=f_hour_str, from_=0, to=23, wrap=True, width=3, font=tkFont.Font(size = 14), format='%02.0f')
        f_hour.place(x=141, y=33)
        f_min = Spinbox(update_win, textvariable=f_min_str, from_=0, to=59, wrap=True, width=3, font=tkFont.Font(size = 14), format='%02.0f')
        f_min.place(x=228, y=33)

        t_title = Label(update_win, text='To\t             :', font=tkFont.Font(size = 16))
        t_title.place(x=30, y =70)
        t_hour = Spinbox(update_win, textvariable=t_hour_str, from_=0, to=23, wrap=True, width=3, font=tkFont.Font(size = 14),format='%02.0f')
        t_hour.place(x=141, y=72)
        t_min = Spinbox(update_win, textvariable=t_min_str, from_=0, to=59, wrap=True, width=3, font=tkFont.Font(size = 14),format='%02.0f')
        t_min.place(x=229, y=72)

        d_title = Label(update_win, text='Duration\t               mins', font=tkFont.Font(size = 16))
        d_title.place(x=30, y=110)
        d_val = Entry(update_win, width=5, font=tkFont.Font(size = 16))
        d_val.place(x=141, y=110)
        d_val.insert(0, row[2])

        i_title = Label(update_win, text='Interrupt\t               mins', font=tkFont.Font(size = 16))
        i_title.place(x=30, y=150)
        i_val = Entry(update_win, width=5, font=tkFont.Font(size = 16))
        i_val.place(x=141, y=150)
        i_val.insert(0, row[3])

        s_title = Label(update_win, text='Total time\t               mins', font=tkFont.Font(size = 16))
        s_title.place(x=30, y=190)
        s_val = Entry(update_win, width=5, font=tkFont.Font(size = 16))
        s_val.place(x=141, y=190)
        s_val.insert(0, row[4])

        update_btn = Button(update_win, text='Update', font=tkFont.Font(size = 14),
                            command=lambda: updateTime(update_win, list_time,
                                                        f_hour.get(), f_min.get(),
                                                        t_hour.get(), t_min.get(),
                                                        d_val.get(), i_val.get(), s_val.get(),
                                                        timeArr, idx))
        update_btn.place(x=120, y=240)

        update_win.mainloop()

    list_time.bind("<Double-1>", update_time)
    
    # After every 5sec, check if time.txt file has update from another computer
    def check(timeArr):
        newTime = getTimeList(onedrivePath)
        if timeArr != newTime:
            timeArr.clear()
            for item in newTime:
                timeArr.append(item)
            # Remove all item in treeview
            for row in list_time.get_children():
                list_time.delete(row)
            # Show new list
            show_time_list(list_time, timeArr)
            messagebox.showinfo(title='Update', message='New update!', parent=win)
        
    def checkUpdate():
        check(timeArr)
        win.after(5000, checkUpdate)

    checkUpdate()

    win.mainloop()

def checkParentPass(password, win):
    onedrivePath = getOneDrivePath()

    # Parent's password
    if checkPassword(onedrivePath + '/ParentPassword.txt', password):
        win.destroy()
        parent_program(onedrivePath)
    else:
        messagebox.showerror('Notification', 'Wrong password!')

def SignIn():
    win = Tk()
    win.title('Parental Control')
    # win.iconbitmap('icons/lock.ico')
    # Set size and position
    w, h = 480, 200
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width/2) - (w/2)
    y = (screen_height/2) - (h/2)
    win.geometry('%dx%d+%d+%d' % (w, h, x, y))
    win.resizable(False, False)

    announce = Label(text='Enter Password', font=tkFont.Font(size = 15))
    announce.grid(row=0, column=1, columnspan=3, padx=10, pady=20)

    password = Entry(show='*', width=50, font=tkFont.Font(size = 13))
    password.grid(row=1, column=0, columnspan=5, padx=12, pady=15)

    enter_btn = Button(text='Enter', width=12, font=tkFont.Font(size = 11), command=lambda: checkParentPass(password.get(), win))
    enter_btn.grid(row=2, column=2, padx=10, pady=20)

    win.mainloop()

def main():
    SignIn()

if __name__ == "__main__":
    main()