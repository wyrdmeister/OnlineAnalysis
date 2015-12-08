# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/media/Home/Documents/SoftProjects/LDM/OAGui/src/Offline/Ui/OASelect.ui'
#
# Created: Wed Apr 17 11:07:05 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_OASelect(object):
    def setupUi(self, OASelect):
        OASelect.setObjectName(_fromUtf8("OASelect"))
        OASelect.resize(541, 501)
        OASelect.setMinimumSize(QtCore.QSize(541, 501))
        OASelect.setMaximumSize(QtCore.QSize(541, 501))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/mainIcon")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        OASelect.setWindowIcon(icon)
        self.file_list = QtGui.QListWidget(OASelect)
        self.file_list.setGeometry(QtCore.QRect(30, 70, 481, 371))
        self.file_list.setObjectName(_fromUtf8("file_list"))
        self.abort_button = QtGui.QPushButton(OASelect)
        self.abort_button.setGeometry(QtCore.QRect(300, 450, 98, 27))
        self.abort_button.setObjectName(_fromUtf8("abort_button"))
        self.confirm_button = QtGui.QPushButton(OASelect)
        self.confirm_button.setGeometry(QtCore.QRect(410, 450, 98, 27))
        self.confirm_button.setObjectName(_fromUtf8("confirm_button"))
        self.label = QtGui.QLabel(OASelect)
        self.label.setGeometry(QtCore.QRect(30, 10, 481, 61))
        self.label.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.select_button = QtGui.QPushButton(OASelect)
        self.select_button.setGeometry(QtCore.QRect(30, 450, 98, 27))
        self.select_button.setObjectName(_fromUtf8("select_button"))

        self.retranslateUi(OASelect)
        QtCore.QMetaObject.connectSlotsByName(OASelect)

    def retranslateUi(self, OASelect):
        OASelect.setWindowTitle(QtGui.QApplication.translate("OASelect", "File selection", None, QtGui.QApplication.UnicodeUTF8))
        self.abort_button.setText(QtGui.QApplication.translate("OASelect", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.confirm_button.setText(QtGui.QApplication.translate("OASelect", "Confirm", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("OASelect", "Select the files you want to analyze. CTRL+click to select single files. To select a range of files select the first one and then SHIFT+click the last one.", None, QtGui.QApplication.UnicodeUTF8))
        self.select_button.setText(QtGui.QApplication.translate("OASelect", "Select all", None, QtGui.QApplication.UnicodeUTF8))

import OAOffline_rc
