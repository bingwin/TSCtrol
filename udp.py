from PyQt5.Qt import *
import socket
import threading
from resources.ui.mainwindowui import Ui_MainWindow
from API.FileCtrol import FileTool
import configobj
import json
import os


class Udpscanning(QMainWindow, Ui_MainWindow,FileTool):
    def __init__(self):
        super(Udpscanning, self).__init__()
        self.sever_socket = None
        self.client_socket = None
        self.address = None
        self.sever_th = None

    def udp_server_start(self):
        self.sever_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            port = int("5555")
            address = ('',port)
            self.sever_socket.bind(address)
        except Exception as ret:
            msg = 'UDP服务开启失败 请检查端口号5555是否被占用'

        else:
            self.sever_th = threading.Thread(target=self.udp_server_concurrency)
            self.sever_th.start()
            msg = 'UDP服务端正在监听端口:5555'

        self.statusbar.showMessage(msg)

    def udp_server_concurrency(self): #监听返回
        while True:
            print("listening...")
            try:
                recv_msg, recv_addr = self.sever_socket.recvfrom(1024)
                msg = recv_msg.decode('utf-8')
                res = json.loads(msg)
                did = res["deviceid"]
                config = configobj.ConfigObj(self.resource_path("resources/dev.ini"), encoding='UTF8')
            except:
                return
            try:
                print(config[did])
            except:
                config[did] ={}
                item_checked = QStandardItem()
                item_checked.setCheckState(Qt.Unchecked)
                item_checked.setCheckable(True)
                self.model.appendRow([
                    QStandardItem(item_checked),
                    QStandardItem(res["deviceid"]),
                    QStandardItem(res["devname"]),
                    QStandardItem(res["ip"]),
                    QStandardItem(0),
                ])
                self.actionHandler(6)
            config[did]['devname'] = res["devname"]
            config[did]['ip'] = res["ip"]
            config[did]['group'] = 0
            config.write()
            '''
              p1[res.get(["deviceid"])] = dict(
                devname=res.get("devname"),
                ip=res.get("ip"),
                group=0,
            )
            plistlib.writePlist(p1,"dev.plist")
            res.get(["deviceid"])=dict(
                deviceid = res.get("deviceid") 
            item_checked = QStandardItem()
            item_checked.setCheckState(Qt.Unchecked)
            item_checked.setCheckable(True)
            self.model.appendRow([
                QStandardItem(item_checked),
                QStandardItem(res.get("deviceid")),
                QStandardItem(res.get("devname")),
                QStandardItem(res.get("ip")),
                QStandardItem(''),
            ])
            '''

    def udp_close(self):
        try:
            stopThreading.stop_thread(self.sever_th)
        except Exception:
            pass

        try:
            self.sever_socket.close()
            self.statusbar.showMessage('已断开网络\n')
        except Exception as ret:
            pass
    def udp_scanning(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        adrs = str.split(str(self.lineEditIP.text()),".")
        if len(adrs) >=3 :
            if len(adrs) ==3:
                adr3=adrs[0]+'.'+adrs[1]+'.'+adrs[2]
                for i in range(1,256):
                    adr = adr3+'.'+ str(i)
                    try:
                        self.address = (adr, int(14099))
                    except Exception as ret:
                        msg = '请检查目标IP，目标端口\n'
                    else:
                        msg = 'UDP客户端已启动\n'
                    self.statusbar.showMessage(msg+"\n")
                    dataDict = {"ip": self.ipAdr, "port": 5555}
                    self.udp_send(json.dumps(dataDict))
            else:
                adr = str(self.lineEditIP.text())
                self.address = (adr, int(14099))
                dataDict = {"ip":self.ipAdr, "port": 5555}
                self.udp_send(json.dumps(dataDict))

    def udp_send(self,data):
        send_msg = (str(data)).encode('utf-8')
        try:
            self.client_socket.sendto(send_msg, self.address)
            msg = '发送成功' + data
            print(msg)
        except Exception as ret:
            msg = '发送失败' + data
            print(msg)

    def click_get_ip(self):
        # 获取本机ip
        my_addr = ""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            my_addr = s.getsockname()[0]
        except Exception as ret:
            # 若无法连接互联网使用，会调用以下方法
            try:
                my_addr = socket.gethostbyname(socket.gethostname())
            except Exception as ret_e:
                self.statusbar.showMessage("无法获取ip，请连接网络！\n")
        finally:
            s.close()

        return my_addr

    def getData(self):
        try:
            config = configobj.ConfigObj(self.resource_path("resources/dev.ini"), encoding='UTF8')
            for key in config.keys():
                devname = config[key]['devname']
                ip = config[key]['ip']
                item_checked = QStandardItem()
                item_checked.setCheckState(Qt.Unchecked)
                item_checked.setCheckable(True)
                self.model.appendRow([
                    QStandardItem(item_checked),
                    QStandardItem(key),
                    QStandardItem(devname),
                    QStandardItem(ip),
                    QStandardItem(''),
                ])
        except:
            self.deletFaile(self.resource_path("resources/dev.ini"))
            self.createFiles(self.resource_path("resources/dev.ini"))
        self.actionHandler(6)

    def resource_path(self, relative_path):
        cdir = QDir.homePath() +"/Documents/TSCtrolConfig"
        self.creeatFloder(cdir)
        return cdir+"/"+relative_path


if __name__ == '__main__':
    import  sys
    app = QApplication(sys.argv)
    ui = Udpscanning()
    ui.show()
    sys.exit(app.exec_())