# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormSnapShot.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(391, 721)
        self.labelSnapShot = QtWidgets.QLabel(Form)
        self.labelSnapShot.setGeometry(QtCore.QRect(0, 0, 389, 719))
        self.labelSnapShot.setAutoFillBackground(False)
        self.labelSnapShot.setStyleSheet("\n"
"background-color: rgb(0, 0, 0);")
        self.labelSnapShot.setObjectName("labelSnapShot")
        self.textBrowserLog = QtWidgets.QTextBrowser(Form)
        self.textBrowserLog.setGeometry(QtCore.QRect(0, 0, 391, 721))
        self.textBrowserLog.setObjectName("textBrowserLog")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "远程屏幕"))
        self.labelSnapShot.setText(_translate("Form", "TextLabel"))


