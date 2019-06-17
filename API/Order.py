from PyQt5.Qt import *
from API.FileCtrol import FileTool
import requests
import json

class Order(QObject,FileTool):
    ORDER_STATUS            = 1  #脚本运行状态
    ORDER_UPLOAD            = 2  #上传文件
    ORDER_SETLUAPATH        = 3  #设置远程路径
    ORDER_RUNLUA            = 4  #远程运行脚本
    ORDER_STOPLUA           = 5  #远程停止脚本
    ORDER_ZHUXIAO           = 6  #注销设备
    ORDER_REBOOT            = 7  #重启设备
    ORDER_SNAPSHOT          = 8  #远程截图
    ORDER_INSTALLDEB        = 9  #安装deb插件
    ORDER_GETLOG            = 10  #获取日志
    ORDER_UNINSTALLDEB      = 11  #卸载插件
    ORDER_UNINSTALLAPP      = 12  #卸载APP
    ORDER_ORDER_DELALLLUA   = 13  #删除所有脚本
    ORDER_ORDER_DELFILE     = 14  #删除所有脚本

    @classmethod
    def TSAPI(cls,items):
        session = requests.session()
        url = "http://"+items["IP"]+":50005/"
        order = items["order"]
        fileName = items["fileName"]
        fileData = items["fileData"]
        if order == Order.ORDER_STATUS: #脚本运行状态
            url = url +"status"
            try:
                res = session.get(url,timeout=(5,9))
            except:
                return "掉线"
            if res.status_code == 200:
                switch = {
                    "f00": lambda: "空闲",
                    "f01": lambda: "运行中",
                    "f02": lambda: "录制中",
                }
                try:
                    return switch[res.text]()
                except:
                    return "未知状态"
            else:
                return "掉线"
        elif order ==Order.ORDER_UPLOAD:#上传文件
            print("上传文件"+fileName)
            url = url + "upload"
            headers = {}
            if fileData is None:
                return "无法打开文件"
            fname = fileName.encode("utf8")
            s = str.split(fileName, ".")
            suffix = s[len(s) - 1]
            if suffix == "lua" or suffix == "tsp":
                headers = {'root': 'lua','path':'/myluas/','filename':fname,'Content-Type':'touchsprite/uploadfile'}
            elif suffix =="so" or suffix == "dylib":
                headers = {'root': 'plugin', 'path': '/', 'filename': fname,'Content-Type': 'touchsprite/uploadfile'}
            else:
                headers = {'root': 'res', 'path': '/', 'filename': fname,'Content-Type': 'touchsprite/uploadfile'}

            try:
                res = session.post(url, headers=headers, data=fileData, timeout=(20,30))
            except:
                return "掉线1"
            if res.status_code == 200:
                if res.text =="ok":
                    return "发送文件: " + fileName +" 成功"
                else:
                    return "发送文件: " + fileName +" 失败"
            elif res.status_code==400:
                return "参数错误"
            elif res.status_code==401:
                return "授权验证失败"
            else:
                return "掉线2"
        elif order == Order.ORDER_SETLUAPATH:  # 设置远程路径
            url = url + "setLuaPath"
            print("设置远程路径: /var/mobile/Media/TouchSprite/lua/myluas/"+fileName)
            data = {"path":"/var/mobile/Media/TouchSprite/lua/myluas/"+fileName}
            try:
                res = session.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data), timeout=(5,9))
            except:
                return "掉线"
            if res.status_code == 200:
                if res.text == "ok":
                    return "设置远程脚本成功"
                else:
                    return "设置远程脚本失败"
            else:
                return "掉线"
        elif order == Order.ORDER_RUNLUA:  # 远程运行脚本
            print("远程运行脚本")
            url = url + "runLua"
            items["order"] = Order.ORDER_STATUS
            status = cls.TSAPI(items)
            if status == "运行中":
                return "已经有脚本正在运行"
            else:
                items["order"] =Order.ORDER_UPLOAD
                status = cls.TSAPI(items)
                if status == "发送文件: " + fileName +" 成功":
                    items["order"] = Order.ORDER_SETLUAPATH
                    status = cls.TSAPI(items)
                    if status == "设置远程脚本成功":
                        try:
                            res = session.get(url, headers={'Content-Type': 'text/html; charset=utf-8'}, timeout=(5,9))
                        except:
                            return "掉线1"
                        if res.status_code == 200:
                            if res.text == "ok":
                                return "启动成功"
                            else:
                                return "启动失败"
                        else:
                            return "掉线2"
                    else:
                        return status
                else:
                    return status
        elif order == Order.ORDER_STOPLUA: #停止脚本
            url = url + "stopLua"
            items["order"] = Order.ORDER_STATUS
            status = cls.TSAPI(items)
            if status == "运行中":
                try:
                    res = session.get(url, headers={'Content-Type': 'text/html; charset=utf-8'}, timeout=(5,9))
                except:
                    return "掉线"
                if res.status_code == 200:
                    print(res.text)
                    if res.text == "ok":
                        return "停止成功"
                    else:
                        return "停止失败"
                else:
                    return "掉线"
            elif status == "掉线":
                return "掉线"
            else:
                return "已停止"
        elif order == Order.ORDER_ZHUXIAO:  # 注销设备
            url = url + "reboot"
            payload = {'type': 0}
            try:
                res = session.get(url, params=payload, headers={'Content-Type': 'text/html; charset=utf-8'},timeout=(5,9))
            except:
                return "掉线"
            if res.status_code == 200:
                if res.text == "ok":
                    return "注销成功"
                else:
                    return "注销失败"
            else:
                return "掉线"
        elif order == Order.ORDER_REBOOT:  # 重启设备
            url = url + "reboot"
            payload = {'type': 1}
            try:
                res = session.get(url, params=payload, headers={'Content-Type': 'text/html; charset=utf-8'}, timeout=(5,9))
            except:
                return "掉线"
            if res.status_code == 200:
                if res.text == "ok":
                    return "重启成功"
                else:
                    return "重启失败"
            else:
                return "掉线"
        elif order == Order.ORDER_SNAPSHOT:  #远程截图
            url = url + "snapshot"
            payload = {'ext':"JPG","compress":0.1,"orient":0}
            try:
                res = session.get(url, params=payload, timeout=(5,9))
            except:
                return "掉线"
            if res.status_code == 200:
                return res.content
            else:
                return "掉线"
        elif order == Order.ORDER_INSTALLDEB:  #安装DEB插件
            items["order"] = Order.ORDER_UPLOAD
            status = cls.TSAPI(items)
            if status == "发送文件: " + fileName + " 成功":
                items["order"] = Order.ORDER_RUNLUA
                items["fileName"] = "install.lua"
                s= str.split(fileName, ".")
                suffix = s[len(s)-1]
                if suffix == "deb":
                    items["fileData"] = '''os.execute("dpkg -i "..userPath().."/res/'''+fileName+'''")'''
                else:
                    return "不支持的文件格式"

                status = cls.TSAPI(items)
                if status =="启动成功":
                    return "安装成功"
                else:
                    return "安装失败 err:"+status
            else:
                return status
        elif order == Order.ORDER_GETLOG:  # 安装DEB插件
            url = url + "getFile"
            fname = "脚本日志.log".encode("utf8")
            headers = {'root': 'log', 'path': '/', 'file': fname}
            try:
                res = session.get(url,  headers=headers, timeout=(5,9))
            except:
                return "掉线"
            if res.status_code == 200:
                return res.text
            else:
                return "无法打开日志文件"
        elif order == Order.ORDER_UNINSTALLDEB:
            items["order"] = Order.ORDER_RUNLUA
            items["fileName"] = "uninstalldeb.lua"
            items["fileData"] = '''os.execute("dpkg -r ''' + fileName + '''")'''
            status = cls.TSAPI(items)
            if status == "启动成功":
                return "卸载Deb成功"
            else:
                return "卸载Deb失败 err:" + status

        elif order == Order.ORDER_UNINSTALLAPP:
            items["order"] = Order.ORDER_RUNLUA
            items["fileName"] = "uninstallapp.lua"
            items["fileData"] = '''uninstallApp("''' + fileName + '''")'''
            status = cls.TSAPI(items)
            if status == "启动成功":
                return "卸载App成功"
            else:
                return "卸载App成功 err:" + status
        elif order == Order.ORDER_ORDER_DELALLLUA:
            items["order"] = Order.ORDER_RUNLUA
            items["fileName"] = "delAll.lua"
            items["fileData"] = '''os.execute("rm -rf "..userPath().."/lua/*")'''
            status = cls.TSAPI(items)
            if status == "启动成功":
                return "删除所有脚本成功"
            else:
                return "删除所有脚本失败"
        elif order == Order.ORDER_ORDER_DELFILE:
            print("删除文件")
            url = url + "rmFile"
            headers = {'Root': 'lua', 'Path': '/', 'File': fileName}
            try:
                res = session.get(url, headers=headers, timeout=(8, 10))
            except:
                return "掉线"
            if res.status_code == 200:
                if res.text == "ok":
                    return "删除文件"+fileName+"成功"
                else:
                    return "删除文件"+fileName+"失败"
            else:
                return "掉线"


'''
itmes ={
    "order" :10,
    "IP":"192.168.7.234",
    "fileName":"",
    "fileData":"",
}
print(Order.TSAPI(itmes))
'''

#print(Order.TSAPI("192.168.6.233", 1,"/Users/tieniu/Documents/pyqt/TSCtrol/mytool/ASO.tsp"))
#print(Order.TSAPI("192.168.7.233",1))