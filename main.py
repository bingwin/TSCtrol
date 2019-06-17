from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp,Qt,QTime,QRect
from PyQt5.QtWidgets import QMessageBox,QWidget

from udp import Udpscanning
from queue import Queue
from API.Order import Order
from resources.ui.FormSnapShot import Ui_Form
from API.myoss import OSS
import re
import configobj

import resource

'''
  QMessageBox.information 信息框
  QMessageBox.question 问答框
  QMessageBox.warning 警告
  QMessageBox.ctitical危险
  QMessageBox.about 关于
'''

class MainWindow(Udpscanning,QWidget):
        def __init__(self):
            super().__init__()
            self.setupUi(self)
            self.setWindowTitle(u"TS控制器")
            self.setWindowIcon(QIcon(":/resources/ico/AppIcon.ico"))
            self.model = QStandardItemModel()
            self.model.setHorizontalHeaderLabels(['选择','设备ID','设备名', '设备IP', '消息'])

            self.tableViewDevice.setModel(self.model)
            self.tableViewDevice.setColumnWidth(0,30)
            self.tableViewDevice.setColumnWidth(1,0)
            self.tableViewDevice.setColumnWidth(2,100)
            self.tableViewDevice.setColumnWidth(3,120)
            self.tableViewDevice.setColumnWidth(4,310)
            self.tableViewDevice.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)   #固定列宽
            self.tableViewDevice.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
            self.tableViewDevice.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            self.tableViewDevice.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
            self.tableViewDevice.setSelectionBehavior(QAbstractItemView.SelectRows)              #整行选取
            self.tableViewDevice.setEditTriggers(QAbstractItemView.NoEditTriggers)               #不可编辑
            self.tableViewDevice.horizontalHeader().sectionClicked.connect(self.HorSectionClicked)  # 表头单击信号
            self.tableViewDevice.setGeometry(QRect(10, 80, 630, 651))
            self.modelSp = QStandardItemModel()
            self.modelSp.setHorizontalHeaderLabels(['文件名','路径','状态'])
            self.tableViewScript.setModel(self.modelSp)
            self.tableViewScript.setColumnWidth(0, 150)
            self.tableViewScript.setColumnWidth(1, 0)
            self.tableViewScript.setColumnWidth(2, 70)

            self.tableViewScript.setEditTriggers(QAbstractItemView.NoEditTriggers)               #不可编辑
            self.tableViewScript.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)   #固定列宽
            self.tableViewScript.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)   #固定列宽
            self.tableViewScript.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)   #固定列宽

            self.listViewGroup.setGeometry(QRect(650, 80, 236, 190))
            self.listModel = QStringListModel()
            self.listViewGroup.setModel(self.listModel)
            self.listViewGroup.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 不可编辑
            row = self.listViewGroup.currentIndex().row()
            if row == -1:
                row = 0
                self.listModel.insertRows(int(row), 1)
                self.listModel.setData(self.listModel.index(row),"全部设备")
            self.listViewGroup.doubleClicked.connect(lambda: self.getData(self.listModel.itemData(self.listViewGroup.currentIndex()).get(0)))

            #self.listViewGroup.setViewMode(QListView.IconMode)

            self.tableViewScript.setGeometry(QRect(650, 280, 236, 451))
            self.tableViewScript.doubleClicked.connect(lambda: self.getOssDir(self.tableViewScript.currentIndex().row()))
            self.tableViewDevice.doubleClicked.connect(lambda: self.showSnapShotWindow(self.tableViewDevice.model().item(self.tableViewDevice.currentIndex().row(), 3).text(), 1))

            self.pushButtonUninstallDeb.clicked.connect(self.uninstallDeb)
            self.pushButtonUninstallApp.clicked.connect(self.uninstallApp)


            regExp = QRegExp('^((2[0-4]\d|25[0-5]|[1-9]?\d|1\d{2})\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?):\d{1,5}$')
            self.lineEditIP.setValidator(QRegExpValidator(regExp, self))
            self.lineEditIP.setFont(QFont( "Timers" , 28 ,  QFont.Bold))
            self.labelGroupName.setFont(QFont( "Timers" , 15 ,  QFont.Bold))
            self.ipAdr = self.click_get_ip()
            self.lineEditIP.setText(str(self.ipAdr))
            self.udp_server_start()
            self.creeatFloder(self.resource_path("resources"))
            self.creeatFloder(self.resource_path("resources/root"))
            self.creeatFloder(self.resource_path("resources/root/lua"))
            self.creeatFloder(self.resource_path("resources/root/deb"))
            self.creeatFloder(self.resource_path("resources/root/plugin"))
            self.createFiles(self.resource_path("resources/dev.ini"))
            self.getData(0)
            self.getListData()
            self.createRightMenu()
            self.sWindow = RemoteWindow()
            self.isSelect = False
            self.getOssDir(-1)
        def clearDevice(self):
            print("清空设备")
            reply = QMessageBox.question(self, "清空设备", "是否清空设备", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.model.removeRows(0,self.model.rowCount())
                self.writeFile(self.resource_path("resources/dev.ini"),"")
                self.actionHandler(6)

        def repairTS(self):
            print("清理脚本")
            reply = QMessageBox.question(self, "清理脚本", "是否清理脚本", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.ThreadCtorl(Order.ORDER_ORDER_DELALLLUA)
        def checkStatus(self):
            print("检测状态")
            self.ThreadCtorl(Order.ORDER_STATUS)

        def scanningDevice(self):
            print("扫描设备")
            self.udp_scanning()

        def closeEvent(self, QCloseEvent):
            print("结束应用")
            self.udp_close()
            self.sWindow.handle_close()

        def checkAllDevice(self):
            self.actionHandler(5)

        def HorSectionClicked(self,index):
            head = self.model.horizontalHeaderItem(index).text()
            if index == 0:
                self.isSelect = not self.isSelect
                self.actionHandler(7) if self.isSelect else self.actionHandler(8)
            elif index == 2:
                if head == '设备名 ⬆':
                    self.model.sort(index,Qt.DescendingOrder)
                    item = QStandardItem()
                    item.setText("设备名 ⬇︎")
                    self.model.setHorizontalHeaderItem(index, item)
                else:
                    self.model.sort(index, Qt.AscendingOrder)
                    item = QStandardItem()
                    item.setText("设备名 ⬆")
                    self.model.setHorizontalHeaderItem(index,item)
            elif index ==3:
                if head == '设备IP ⬆':
                    self.model.sort(index, Qt.DescendingOrder)
                    item = QStandardItem()
                    item.setText("设备IP ⬇︎")
                    self.model.setHorizontalHeaderItem(index, item)
                else:
                    self.model.sort(index, Qt.AscendingOrder)
                    item = QStandardItem()
                    item.setText('设备IP ⬆')
                    self.model.setHorizontalHeaderItem(index, item)
            elif index == 4:
                if head == '消息 ⬆':
                    self.model.sort(index, Qt.DescendingOrder)
                    item = QStandardItem()
                    item.setText("消息 ⬇︎")
                    self.model.setHorizontalHeaderItem(index, item)
                else:
                    self.model.sort(index, Qt.AscendingOrder)
                    item = QStandardItem()
                    item.setText('消息 ⬆')
                    self.model.setHorizontalHeaderItem(index, item)

        def createRightMenu(self):
            self.tableViewDevice.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tableViewDevice.customContextMenuRequested.connect(self.showContextMenu1)
            self.contextMenu1 = QMenu(self)
            self.Menu1_actionA = self.contextMenu1.addAction(u'勾选选中')
            self.Menu1_actionB = self.contextMenu1.addAction(u'取消勾选')
            self.Menu1_actionC = self.contextMenu1.addAction(u'全部勾选')
            self.Menu1_actionD = self.contextMenu1.addAction(u'全部取消')
            self.Menu1_actionG = self.contextMenu1.addAction(u'加入分组')
            self.contextMenu1.addSeparator()
            self.Menu1_actionE = self.contextMenu1.addAction(u'远程屏幕')
            self.Menu1_actionF = self.contextMenu1.addAction(u'查看日志')
            self.Menu1_actionA.triggered.connect(lambda:self.actionHandler(1))
            self.Menu1_actionB.triggered.connect(lambda:self.actionHandler(2))
            self.Menu1_actionC.triggered.connect(lambda:self.actionHandler(3))
            self.Menu1_actionD.triggered.connect(lambda:self.actionHandler(4))
            self.Menu1_actionE.triggered.connect(lambda:self.showSnapShotWindow(self.tableViewDevice.model().item(self.tableViewDevice.currentIndex().row(),3).text(),1))
            self.Menu1_actionF.triggered.connect(lambda:self.showSnapShotWindow(self.tableViewDevice.model().item(self.tableViewDevice.currentIndex().row(),3).text(),2))
            self.Menu1_actionG.triggered.connect(lambda:self.changeDevGroup())

            self.tableViewScript.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tableViewScript.customContextMenuRequested.connect(self.showContextMenu2)
            self.contextMenu2 = QMenu(self)
            self.Menu2_actionA = self.contextMenu2.addAction(u'下载文件')
            self.Menu2_actionB = self.contextMenu2.addAction(u'上传文件')
            self.Menu2_actionC = self.contextMenu2.addAction(u'删除文件')
            self.Menu2_actionD = self.contextMenu2.addAction(u'刷新目录')
            self.Menu2_actionA.triggered.connect(lambda:self.downloadFileAction(self.tableViewScript.currentIndex().row()))
            self.Menu2_actionB.triggered.connect(lambda:self.uploadFileAction())
            self.Menu2_actionC.triggered.connect(lambda:self.deleteFileAction(self.tableViewScript.currentIndex().row()))
            self.Menu2_actionD.triggered.connect(lambda:self.getOssDir(0,True))

            self.listViewGroup.setContextMenuPolicy(Qt.CustomContextMenu)
            self.listViewGroup.customContextMenuRequested.connect(self.showContextMenu3)
            self.contextMenu3 = QMenu(self)
            self.Menu3_actionA = self.contextMenu3.addAction(u'创建分组')
            self.Menu3_actionB = self.contextMenu3.addAction(u'删除分组')
            self.Menu3_actionA.triggered.connect(lambda: self.CreatDevGroup())
            self.Menu3_actionB.triggered.connect(lambda: self.DeleteDevGroup())
        def CreatDevGroup(self):
            gname, ok = QInputDialog.getText(self, "创建分组", "输入创建的分组名称")
            if ok:
                row = self.listModel.rowCount()
                self.listModel.insertRows(int(row),1)
                self.listModel.setData(self.listModel.index(row),gname)
                config = configobj.ConfigObj(self.resource_path("resources/config.ini"), encoding='UTF8')
                try:
                    print(config["Group"])
                except:
                    config["Group"] = {}
                config["Group"][gname] = row
                config.write()


        def DeleteDevGroup(self):
            print("DeleteDevGroup")
            row =self.listViewGroup.currentIndex().row()
            if row>0:
                gname = self.listModel.itemData(self.listViewGroup.currentIndex()).get(0)
                self.listModel.removeRow(row)
                config = configobj.ConfigObj(self.resource_path("resources/config.ini"), encoding='UTF8')
                del config["Group"][gname]
                config.write()


        def changeDevGroup(self):
            print("changeDevGroup")
            gname = self.listModel.itemData(self.listViewGroup.currentIndex()).get(0)
            if gname:
                rows = self.model.rowCount()
                for i in range(rows):
                    if self.model.item(i, 0).checkState() == 2:
                        did = self.model.item(i, 1).text()
                        config = configobj.ConfigObj(self.resource_path("resources/dev.ini"), encoding='UTF8')
                        config[did]['group'] = gname
                        config.write()

        def downloadFileAction(self,row):
            name = self.modelSp.item(row,0).text()
            cloudPath = self.modelSp.item(row,1).text()
            type = self.modelSp.item(row,2).text()
            if not type == "file":
                self.statusbar.showMessage("不支持的下载格式")
                return
            filepath = QFileDialog.getSaveFileName(self,r"保存文件",self.resource_path("resources/"+cloudPath),r"所有文件 (*)")
            if not filepath[0] == '':
                OSS.downloadFile(self,cloudPath,filepath[0])
        def uploadFileAction(self):
            print("上传")
            filePath = QFileDialog.getOpenFileName(self, "上传文件", self.resource_path("resources/"),"所有文件 (*)")
            cloudPath = self.modelSp.item(0, 1).text()
            if not filePath[0] == '':
                fileName = self.getFileName(filePath[0])
                localPath = filePath[0]
                OSS.uploadFile(self,cloudPath+fileName,localPath)
                self.getOssDir(0,True)
        def deleteFileAction(self,row):
            cloudPath = self.modelSp.item(row, 1).text()
            reply = QMessageBox.question(self, "删除云文件", "是否删除此文件", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                OSS.deleteFile(self, cloudPath)
                self.getOssDir(0, True)

        def actionHandler(self,order):#计算勾选数量 并勾选
            checkNum = 0
            allDevice = 0
            if order == 1 or order == 2 :
                selections = self.tableViewDevice.selectionModel()
                selected = selections.selectedIndexes()
                for index in selected:
                    self.model.item(index.row(), 0).setCheckState(Qt.Checked) if order ==1 else self.model.item(index.row(), 0).setCheckState(Qt.Unchecked)
            elif order ==3 or order==4:
                rows = self.model.rowCount()
                for i in range(rows):
                    self.model.item(i, 0).setCheckState(Qt.Checked) if order == 3 else self.model.item(i, 0).setCheckState(Qt.Unchecked)
            elif order ==5:
                rows = self.model.rowCount()
                for i in range(rows):
                    self.model.item(i, 0).setCheckState(Qt.Checked) if self.cbCheckAllDevice.isChecked() else self.model.item(i, 0).setCheckState(Qt.Unchecked)
            elif order ==7:
                rows = self.model.rowCount()
                for i in range(rows):
                    self.model.item(i, 0).setCheckState(Qt.Checked)
            elif order ==8:
                rows = self.model.rowCount()
                for i in range(rows):
                    self.model.item(i, 0).setCheckState(Qt.Unchecked)

            rows = self.model.rowCount()
            for i in range(rows):
                allDevice+=1
                if self.model.item(i, 0).checkState() == 2:
                    checkNum+=1
            self.cbCheckAllDevice.setText(u"全/反选 (已选: "+str(checkNum) + "\t全部:" + str(allDevice)+ ")")

        def showSnapShotWindow(self,ip,order):
            self.sWindow.handle_click(ip,order)

        def showContextMenu1(self, pos):
            self.contextMenu1.exec_(QCursor.pos())  # 在鼠标位置显示

        def showContextMenu2(self, pos):
            self.contextMenu2.exec_(QCursor.pos())  # 在鼠标位置显示

        def showContextMenu3(self, pos):
            self.contextMenu3.exec_(QCursor.pos())  # 在鼠标位置显示

        def checkClaculate(self): #点击表格事件
            index = self.tableViewDevice.currentIndex()
            if index.column() ==0:
                self.actionHandler(6)

        def runScript(self):
            print("运行脚本")
            filepath =  QFileDialog.getOpenFileName(self,"请选择脚本或者插件",self.resource_path("resources/root/"),"运行加密脚本(*.tsp);;运行普通脚本 (*.lua);;安装DEB包 (*.deb);;发送触动插件 (*.so *.dylib);;发送资源 (*)")

            self.textEdit.setText(filepath[0])
            if not filepath[0] == '':
                s = str.split(filepath[0],".")
                suffix = s[len(s)-1]
                if suffix =="tsp" or suffix == "lua":
                    print("运行脚本")
                    self.ThreadCtorl(Order.ORDER_RUNLUA,filepath[0])
                elif suffix =="so" or suffix == "dylib":
                    print("发送插件")
                    self.ThreadCtorl(Order.ORDER_UPLOAD, filepath[0])
                elif suffix =="deb":
                    print("安装deb")
                    self.ThreadCtorl(Order.ORDER_INSTALLDEB, filepath[0])
                else:
                    print("发送资源")
                    self.ThreadCtorl(Order.ORDER_UPLOAD, filepath[0])

        def stopScript(self):
            print("停止脚本")
            self.ThreadCtorl(Order.ORDER_STOPLUA)

        def signOutDevice(self):
            print("注销设备")
            reply = QMessageBox.question(self, "注销设备", "是否执行注销设备指令", QMessageBox.Yes | QMessageBox.No)
            if reply==QMessageBox.Yes:
                self.ThreadCtorl(Order.ORDER_ZHUXIAO)

        def rebootDevice(self):
            print("重启设备")
            reply = QMessageBox.question(self, "重启设备", "是否执行重启设备指令", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.ThreadCtorl(Order.ORDER_REBOOT)


        def uninstallDeb(self):
            print("卸载插件")
            filename,ok = QInputDialog.getText(self,"卸载DEB","请输入你要卸载的DEB包名")
            if ok:
                reply = QMessageBox.question(self, "卸载插件", "是否执行卸载插件:"+filename, QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.ThreadCtorl(Order.ORDER_UNINSTALLDEB,filename)

        def uninstallApp(self):
            print("卸载App")
            filename, ok = QInputDialog.getText(self, "卸载App", "请输入你要卸载的App包名")
            if ok:
                reply = QMessageBox.question(self, "卸载App", "是否执行卸载App:"+filename, QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.ThreadCtorl(Order.ORDER_UNINSTALLAPP)

        def ThreadCtorl(self,order,filePath ="",isAll=False): #多线程控制器
            queueDevice = Queue()
            #fileName =self.getFileName(filePath)
            fileName = filePath if order==Order.ORDER_UNINSTALLAPP or order == Order.ORDER_UNINSTALLDEB else self.getFileName(filePath)

            rows = self.model.rowCount()
            data = self.readFile(filePath)
            for i in range(rows):
                if isAll == True or self.model.item(i, 0).checkState() == 2:
                    self.model.item(i, 4).setText(u"队列等待")
                    items = {
                        "index":i,
                        "IP": self.model.item(i, 3).text(),
                        "order":order,
                        "fileName":fileName,
                        "fileData":data,
                    }
                    queueDevice.put(items)


            while True :
                if queueDevice.empty():
                    print("消息列队为空")
                    break
                for i in range(0,1):
                    try:
                        items = queueDevice.get_nowait()
                    except:
                        return
                    thread = OrderThread(self,items)
                    def setStatus(items):
                        self.model.item(items["index"],4).setText(items["status"])
                    thread.getOrderStatus.connect(setStatus)
                    thread.start()
                print("结束线程")
        def getOssDir(self,row,cur=False):
            floder="root/"
            if row >=0:
                if self.modelSp.item(row,1):
                    floder = self.modelSp.item(row,1).text()
            Qitem = self.modelSp.item(row,2)
            if Qitem:
                if Qitem.text()=="root" and cur == False:
                    if not re.split("[^/]+/$", floder)[0] =='':
                        floder = re.split("[^/]+/$", floder)[0]
                elif Qitem.text()=="file":
                    return

            self.modelSp.removeRows(0, self.modelSp.rowCount())
            ret = OSS.getdirectory(floder)
            for key in ret:
                path = key
                split = str.split(key,"/")
                name = ""
                type = ret[key]
                icon = QIcon()
                if type == "root":
                    name = "..."
                elif type == "directory":
                    name = split[len(split) - 2]
                    #icon = QIcon(pkgutil.get_data("ico","directory.ico"))
                    icon = QIcon(":/resources/ico/directory.ico")
                elif type == "file":
                    name = split[len(split) - 1]
                    #icon = QIcon(pkgutil.get_data("ico","file.ico"))
                    icon = QIcon(":/resources/ico/file.ico")
                self.modelSp.appendRow([
                    QStandardItem(name),
                    QStandardItem(path),
                    QStandardItem(type),
                ])

                if self.modelSp.item(self.modelSp.rowCount()-1,0):
                    self.modelSp.item(self.modelSp.rowCount()-1,0).setIcon(icon)




class RemoteWindow(QWidget,Ui_Form):
    def __init__(self, parent=None):
        super(RemoteWindow, self).__init__(parent)
        self.setupUi(self)
        self.labelSnapShot.setScaledContents(True)

    def handle_click(self,ip,order):
        if not self.isVisible():
            self.show()
            self.ip = ip
            self.order = order
            self.setWindowTitle("远程桌面: \t"+ip)
            self.timer = QTimer(self)  # 初始化一个定时器
            if self.order==1:
                self.labelSnapShot.clear()
                self.snapShot(ip)
                self.labelSnapShot.setHidden(False)
                self.textBrowserLog.setHidden(True)
                self.timer.timeout.connect(lambda:self.snapShot(ip))  # 计时结束调用operate()方法
            elif self.order==2:
                self.getLog(ip)
                self.labelSnapShot.setHidden(True)
                self.textBrowserLog.setHidden(False)
                self.timer.timeout.connect(lambda: self.getLog(ip))  # 计时结束调用operate()方法
            self.timer.start(5000)

    def getLog(self,ip):
        print("getLog")
        self.items = {
            "IP": ip,
            "order": Order.ORDER_GETLOG,
            "fileName": "",
            "fileData": "",
        }
        thread = OrderThread(self, self.items)
        def setLog(items):
            # data = bytes(items["status"],encoding="unicode")
            log = items["status"]
            if log:
                self.textBrowserLog.setText(log)
                self.textBrowserLog.moveCursor(self.textBrowserLog.textCursor().End)
        thread.getOrderStatus.connect(setLog)
        thread.start()
    def snapShot(self,ip):
        self.items = {
            "IP": ip,
            "order": Order.ORDER_SNAPSHOT,
            "fileName":"",
            "fileData":"",
        }
        thread = OrderThread(self, self.items)
        def getPix(items):
            photo = QPixmap()
            try:
                pixmap = photo.loadFromData(items["status"])
            except:
                self.labelSnapShot.clear()
                return

            if pixmap:
                self.labelSnapShot.setPixmap(photo)
            else:
                self.labelSnapShot.clear()

        thread.getOrderStatus.connect(getPix)
        thread.start()
    def handle_close(self):
        self.close()

    def closeEvent(self, QCloseEvent):
        print("结束窗体")
        try:
            self.timer.disconnect()
        except:
            pass

class OrderThread(QThread):
    getOrderStatus = pyqtSignal(dict)
    def __init__(self, parent=None,items=None):
        super(OrderThread, self).__init__(parent)
        self.items = items


    def run(self):
        status = Order.TSAPI(self.items)
        self.items["status"] = status
        self.getOrderStatus.emit(self.items)

if __name__ == '__main__':
    import  sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

'''
打包命令:pyinstaller -D -y main.py -i resources/ico/app.ico  


'''