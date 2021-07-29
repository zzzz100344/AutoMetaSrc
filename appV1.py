import sys
from PyQt5.QtWidgets import *
from V2 import Ui_mainWindow      #search_ui 是你的.py檔案名字
from PyQt5 import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import win32api
from urllib import request
import urllib.request
import requests
import threading
import webbrowser
import base64
import time
import win32com
from win32com.client import Dispatch, constants, GetObject
import pythoncom
import inspect
import ctypes
import os
from bs4 import BeautifulSoup

readyCheck=0
path=""
url_prefix=""
authorization=""
headers=""
threadList=[]
thread=0
last_champ="None"
now_champ="None"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        global readyCheck,url_prefix,authorization,headers,path
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        #self.show()
        #---讀取當前版本和英雄列表---
        version = request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json").read().decode("utf-8")
        version = version.split('"')
        self.ui.dataBase.setText("資料庫版本:"+version[1])
        champList = request.urlopen("https://ddragon.leagueoflegends.com/cdn/"+version[1]+"/data/en_US/champion.json").read().decode("utf-8")
        #champList = json.loads(champList);
        #champList = champList['data']
        champList = champList.split(',')
        
        def load_lockfile():
            global readyCheck,url_prefix,authorization,headers,path
            pythoncom.CoInitialize()
            while readyCheck == 0:
                filepath = self.ui.lineEdit.text() + '\\lockfile'
                if os.path.isfile(filepath):
                    lockfile = self.ui.lineEdit.text() + '\\lockfile'
                    with open(lockfile, 'r') as f:
                        data = f.read()
                        data = data.split(':')
                        # data[0] == 'LeagueClient'
                        # data[1] ==  I dont't know
                        # data[2] ==  Port number
                        # data[3] ==  Authorization token
                        # data[4] ==  Connecton method
            
                        host              = '127.0.0.1'
                        port              =  data[2]
                        connection_method =  data[4]
                        authorization     = 'Basic ' + base64.b64encode(('riot:' + data[3]).encode(encoding = 'utf-8')).decode('utf-8')
            
                        # Format url like : https://127.0.0.1:1337
                        url_prefix = connection_method + '://' + host + ':' + port
                        headers    = {'Accept' : 'application/json', 'Authorization' : authorization}
            
                        # """ Debug
                        print('Host             : ' + host)
                        print('Port             : ' + port)
                        print('Connecton method : ' + connection_method)
                        print('Authorization    : ' + authorization)
                        print('\n')
                        # """
                        readyCheck = 1   
                        readyMatch = threading.Thread(target = find_match)
                        readyMatch.setDaemon(True)
                        readyMatch.start()
                else :
                    try:
                        mywmi = GetObject("winmgmts:")
                        objs = mywmi.InstancesOf("Win32_Process")
                        for obj in objs:
                            if (obj.Name == "LeagueClient.exe"):
                                path=obj.ExecutablePath
                                print(path)
                        path = path.rsplit("\\",1)
                        if len(path)==2:
                            self.ui.lineEdit.setText(path[0])
                    except:
                        readyCheck=0
                        time.sleep(1)
                        s = self.ui.state.text()
                        if len(s)<9:
                            s += "."
                        else :
                            s = '未啟動客戶端'
                        self.ui.state.setText(s)
                        pass
                #print(lockfile)
                    
                    # Load lockfile
                    
                    
                
        def find_match():
            global now_champ,last_champ
            requests.packages.urllib3.disable_warnings()
    
    
            """
            gameflow_list = ['"None"'      , '"Lobby"'       , '"Matchmaking"',
                             '"ReadyCheck"', '"ChampSelect"' , '"InProgress"' ,
                             '"Reconnect"' , '"PreEndOfGame"', '"EndOfGame"' ,]
            """
            while readyCheck==1:
                time.sleep(1)
                gameflow = get_gameflow()
                if gameflow == '"None"':
                    self.ui.state.setText("大廳")
                    now_champ = get_champ_select()
                    last_champ=now_champ
                    self.ui.champIcon.setPixmap(QPixmap(""))
                    self.ui.champName.setText("")
                    self.ui.itemIcon_1.setPixmap(QPixmap(""))
                    self.ui.itemIcon_2.setPixmap(QPixmap(""))
                    self.ui.itemIcon_3.setPixmap(QPixmap(""))
                    self.ui.itemIcon_4.setPixmap(QPixmap(""))
                    self.ui.itemIcon_5.setPixmap(QPixmap(""))
                    self.ui.itemIcon_6.setPixmap(QPixmap(""))
                if gameflow == '"Lobby"':
                    self.ui.state.setText("組隊房間")
                    now_champ = get_champ_select()
                    last_champ=now_champ
                    self.ui.champIcon.setPixmap(QPixmap(""))
                    self.ui.champName.setText("")
                    self.ui.itemIcon_1.setPixmap(QPixmap(""))
                    self.ui.itemIcon_2.setPixmap(QPixmap(""))
                    self.ui.itemIcon_3.setPixmap(QPixmap(""))
                    self.ui.itemIcon_4.setPixmap(QPixmap(""))
                    self.ui.itemIcon_5.setPixmap(QPixmap(""))
                    self.ui.itemIcon_6.setPixmap(QPixmap(""))
                if gameflow == '"Matchmaking"':
                    self.ui.state.setText("配對中")
                if gameflow == '"InProgress"':
                    self.ui.state.setText("遊戲中")
                if gameflow == '"ReadyCheck"':
                    self.ui.state.setText("配對準備")
                    if (self.ui.checkBox.isChecked()):    
                        accept_matchmaking()
                if gameflow == '"ChampSelect"':
                    self.ui.state.setText("選擇英雄中")
                    now_champ = get_champ_select()
                    if(last_champ!=now_champ and now_champ!='None'):
                        #print(now_champ)
                        #print(now_champ_1)
                        if(self.ui.checkBox_2.isChecked()):
                            if (self.ui.Metasrc.isChecked()):
                                if (self.ui.radioButton.isChecked()):
                                    metaSrc = 'https://www.metasrc.com/aram/champion/'
                                    webbrowser.get('windows-default').open(metaSrc+str(now_champ))
                                if (self.ui.radioButton_2.isChecked()):
                                    metaSrc = 'https://www.metasrc.com/5v5/champion/'
                                    webbrowser.get('windows-default').open(metaSrc+str(now_champ))
                            if (self.ui.OPGG.isChecked()):
                                if (self.ui.radioButton.isChecked()):
                                    OPGG = 'https://na.op.gg/aram/'+now_champ+'/statistics/'
                                    webbrowser.get('windows-default').open(OPGG)
                                if (self.ui.radioButton_2.isChecked()):
                                    OPGG = 'https://na.op.gg/champion/'+now_champ+'/statistics/'
                                    webbrowser.get('windows-default').open(OPGG)
                        last_champ = now_champ
                        self.ui.champName.setText(now_champ)
                        champIconUrl = "http://ddragon.leagueoflegends.com/cdn/11.15.1/img/champion/"+now_champ+".png"    
                        data = urllib.request.urlopen(champIconUrl).read()
                        champImg = QPixmap()
                        champImg.loadFromData(data)
                        self.ui.champIcon.setPixmap(champImg)
                        
       #                 itemIconUrl = "https://ddragon.leagueoflegends.com/cdn/11.15.1/img/item/3111.png"
       #                 icondata = urllib.request.urlopen(itemIconUrl).read()
       #                 itemIcon = QPixmap()
       #                 itemIcon.loadFromData(icondata)
       #                 self.ui.itemIcon_.setPixmap(itemIcon)
                        
                        if(self.ui.radioButton.isChecked()):
                            response = requests.get('https://www.metasrc.com/aram/champion/'+str(now_champ))
                        if(self.ui.radioButton_2.isChecked()):
                            response = requests.get('https://www.metasrc.com/5v5/champion/'+str(now_champ))
                            
                        soup = BeautifulSoup(response.text, 'html.parser')
                        itemdivs = soup.find('div', '_sfh2p9-3')     
                        itemdivs = itemdivs.select('img')
                        num = 1
                        strlist = []
                        lasticon = ''
                        for icon in itemdivs:
                            i = icon['data-src']
                            strlist.append(str(i))
                        
                        for url in strlist:
                        
                            if url.rsplit("/",1)[1] == 'coin.png' and num <7:
                                itemImg = getattr(self.ui, 'itemIcon_{}'.format(num))
                                itemIconUrl = lasticon
                                icondata = urllib.request.urlopen(itemIconUrl).read()
                                itemIcon = QPixmap()
                                itemIcon.loadFromData(icondata)
                                itemImg.setPixmap(itemIcon)
                                num += 1
                                
                            else:
                                lasticon = url

                        
                        
                        
                if gameflow == '"InProgress"':
                    now_champ = get_champ_select()
                    last_champ=now_champ
                    
        def get_gameflow():
            global thread,readyCheck
            try:
                # GET /lol-gameflow/v1/gameflow-phase HTTP/1.1
                response = requests.get(url = url_prefix + '/lol-gameflow/v1/gameflow-phase', headers = headers, verify = False)
                return response.text
            except:
                print("API連線異常1:執行緒列",len(threadList))
                self.ui.state.setText("未啟動客戶端")
                readyCheck = 0
                if not threadList[thread].is_alive():
                    threadList.append(threading.Thread(target = load_lockfile))
                    thread += 1
                    threadList[thread].setDaemon(True)
                    threadList[thread].start()
    
        def accept_matchmaking():
            global thread,readyCheck
            try:
                # POST /lol-matchmaking/v1/ready-check/accept HTTP/1.1
                response = requests.post(url = url_prefix + '/lol-matchmaking/v1/ready-check/accept', headers = headers, verify = False, data = {})
            except:
                print("API連線異常2:執行緒列",len(threadList))
                self.ui.state.setText("未啟動客戶端")
                readyCheck = 0
                if not threadList[thread].is_alive():  
                    threadList.append(threading.Thread(target = load_lockfile))
                    thread += 1
                    threadList[thread].setDaemon(True)
                    threadList[thread].start()

        def get_champ_select():
            global thread,readyCheck
            try:
                response = requests.get(url = url_prefix + '/lol-champ-select/v1/current-champion', headers = headers, verify = False)
                #response = requests.post(url = self.url_prefix + '/lol-champ-select-legacy/v1/battle-training/launch', headers = self.headers, verify = False, data = {})
                champID = response.text
            except:
                print("API連線異常3:執行緒列",len(threadList))
                self.ui.state.setText("未啟動客戶端")
                readyCheck = 0
                if not threadList[thread].is_alive():
                    threadList.append(threading.Thread(target = load_lockfile))
                    thread += 1
                    threadList[thread].setDaemon(True)
                    threadList[thread].start()
            try:
                champKey = champList.index('"key":"'+champID+'"')
                champIndex = champList[champKey-1]
                champIndex = champIndex.split('"')
                return champIndex[3]
            except:
                return 'None'
        '''
        def get_path(self):
            lockfile = self.lineEdit.text() + '\\lockfile'
            if os.path.isfile(lockfile) == False:
                print('路徑不存在或遊戲客戶端未啟動 !\n\n')
                win32api.MessageBox(0, '路徑不存在或遊戲客戶端未啟動 !', '錯誤')
            return lockfile'''
        
        
        threadList.append(threading.Thread(target = load_lockfile))
        threadList[thread].setDaemon(True)
        threadList[thread].start()

        
        #load_lockfile()
    def closeEvent(self, event):
        """
        對MainWindow的函式closeEvent進行重構
        退出軟體時結束所有程序
        :param event:
        :return:
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '關閉確認',
                                               "是否要退出程式？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            os._exit(0)
        else:
            event.ignore()
            '''---關閉執行緒CODE
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)'''
    
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())
        
    
    
    
    