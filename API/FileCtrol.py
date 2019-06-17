import os
import re
import sys

class FileTool():
    def deletFaile(self, filename):
        if not os.path.exists(filename):
            print(filename + " no existed.")
        else:
            os.remove(filename)
        return

    def createFiles(self, filename):
        if not os.path.exists(filename):
            f = open(filename, 'w')
            f.close()
            print(filename + " created.")
        else:
            print(filename + " already existed.")
        return

    def creeatFloder(self,floderName):
        if not os.path.exists(floderName):
            os.makedirs(floderName)
        else:
            print(floderName + " already existed")

    def getFileName(self, filePath):
        return os.path.split(filePath)[-1]

    def readFile(self,filePath):
        try:
            f = open(filePath, "rb+")
            data = f.read()  # 这样data是一个b开头的ASCII数字。
            f.close()
            return data
        except:
            return None

    def writeFile(self,filePath,data):
        try:
            f = open(filePath, "w")
            with f:
                f.write(data)
            f.close()
            return True
        except:
            return None

    def tmp_path(self, relative_path):
        '''返回资源绝对路径。'''
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller会创建临时文件夹temp
            # 并把路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath('.')
        return os.path.join(base_path, relative_path)


