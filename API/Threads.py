from PyQt5.Qt import *
from API.Order import Order
from PyQt5.QtCore import QRunnable, QObject, QThreadPool, QThread ,pyqtSignal

class OrderThread(QRunnable):
    def __init__(self):
        super(OrderThread, self).__init__()
        self.items = None
        self.communicate = None
    def transfer(self, items=None,communicate=None):
        self.items = items
        self.communicate = communicate

    def run(self):
        if self.items:
            print(type(self.items))
            status = Order.TSAPI(self.items)
            self.items["status"] = status
            self.communicate.emit(self.items)



class SnapThread(QThread):
    getOrderStatus = pyqtSignal(dict)

    def __init__(self, parent=None, items=None):
        super(SnapThread, self).__init__(parent)
        self.items = items

    def run(self):
        status = Order.TSAPI(self.items)
        self.items["status"] = status
        self.getOrderStatus.emit(self.items)