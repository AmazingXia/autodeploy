#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
from pywinauto.application import Application
import pyperclip
import io
import sys
import time
# import pyautogui
import common
import sched
import threading
import win32gui
import win32con
scheduler = sched.scheduler(time.time, time.sleep)

EL = None
count = 0
search_count = 10
# pyautogui.FAILSAFE = False  # 关闭自动保护机制

# 改变标准输出的默认编码
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

# 根据进程名获取到对应的id ,用于连接

def get_pid(processName):
    for process in psutil.process_iter():
        try:
            if(process.name() == processName and not process.parent()):
                return process
        except psutil.NoSuchProcess:
            pass
    return -1

def find_window_movetop(topOrback):
    hwnd = win32gui.FindWindow("StandardFrame_DingTalk", "钉钉")
    win32gui.ShowWindow(hwnd, topOrback)
    # win32gui.ShowWindow(hwnd, win32con.SHOW_FULLSCREEN) #显示在最前且最大化
    # win32gui.ShowWindow(hwnd, win32con.SW_RESTORE) #重新显示在最前端
    # win32gui.ShowWindow(hwnd, win32con.HIDE_WINDOW) #重新显示在最前端
    win32gui.SetForegroundWindow(hwnd)

# 发送对应的消息给指定的联系人
def sendInfo(info=u'hello', friend=u'小明'):
    global count, search_count
    print('count===>', count)
    pyperclip.copy(friend)
    if(info is None):
        print("************ 任务终止，传入的信息为空 ******************")
        return
    # 获取到程序进程 PID
    proc = get_pid("DingTalk.exe")
    procId = proc.pid

    if(procId == -1):
        common.alert(f"请登录钉钉")
        return
    try:
        # 打开钉钉窗口
        find_window_movetop(win32con.SW_RESTORE)
        # app = Application(backend='uia').start(proc.exe())
        app = Application(backend='uia').connect(process=procId)

        main_Dialog = app.window(
            title=u"钉钉", class_name="StandardFrame_DingTalk")

        main_Dialog.type_keys('^+f')
        pyperclip.copy(friend)
 
        advancedSearch = main_Dialog.child_window(
            title="advancedSearch", class_name="UICef2WndSearch")
        advancedSearch.wait('visible', timeout = 3)
        
        childWindow = advancedSearch.child_window(control_type="Document").child_window(
            title="联系人", control_type="TabItem").click_input()

        def search():
            global count, search_count
            pyperclip.copy(friend)
            main_Dialog.type_keys('^a')
            main_Dialog.type_keys('^v')

            result_box = advancedSearch.child_window(
                control_type='Text', found_index=0)
            result_box.wait('visible', timeout=0.5)
            print('resultText===>', result_box.window_text())
            if (result_box.window_text() in '找不到相关的结果  请稍候...'):
                if (search_count > 0):
                    search_count -= 1
                    search()
        search()
        
        

        # 打开指定用户的发消息页面 
        # 搜索用户
        main_Dialog.type_keys('{ENTER}')
        # 等待UI显示
        # # 发送消息
        # print("********* 发送消息 ****************")
        pyperclip.copy(info)

        chat = main_Dialog.child_window(title="请输入消息", control_type="Edit")
        chat.wait('visible', timeout=2)
        main_Dialog.type_keys('^a')
        main_Dialog.type_keys('^v')
        # main_Dialog.type_keys('{BACKSPACE}')
        main_Dialog.type_keys('{ENTER}')
        main_Dialog.minimize()
        count = 0
    except Exception as e:
        common.alert(f"{e}")
        count += 1
        print('sendinfo.py 75 Exception===>', e)
        if count < 2:
            sendInfo()

def task(info=u'hello', friend=u'小明', delay = 4):
    global EL
    EL = scheduler.enter(delay, 1, sendInfo, (info, friend))
    t = threading.Thread(target = scheduler.run)
    t.setDaemon(True)
    t.start()

def cancel_task():
    try:
        if not scheduler.empty():
            scheduler.cancel(EL)
    except Exception as reason:
        print('cancle_task.py 75 Exception===>', reason)

if __name__ == "__main__":
    sendInfo('hello', '小明')