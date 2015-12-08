# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/media/Home/Documents/SoftProjects/LDM/OAGui/src/Offline/Ui/OAProgress.ui'
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

class Ui_OAProgress(object):
    def setupUi(self, OAProgress):
        OAProgress.setObjectName(_fromUtf8("OAProgress"))
        OAProgress.resize(341, 191)
        OAProgress.setMinimumSize(QtCore.QSize(341, 171))
        OAProgress.setMaximumSize(QtCore.QSize(341, 191))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/mainIcon")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        OAProgress.setWindowIcon(icon)
        self.progress = QtGui.QProgressBar(OAProgress)
        self.progress.setGeometry(QtCore.QRect(40, 60, 271, 23))
        self.progress.setProperty("value", 24)
        self.progress.setObjectName(_fromUtf8("progress"))
        self.label = QtGui.QLabel(OAProgress)
        self.label.setGeometry(QtCore.QRect(10, 100, 71, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.filename = QtGui.QLabel(OAProgress)
        self.filename.setGeometry(QtCore.QRect(90, 100, 231, 17))
        self.filename.setObjectName(_fromUtf8("filename"))
        self.widget = QtGui.QWidget(OAProgress)
        self.widget.setGeometry(QtCore.QRect(90, 20, 181, 21))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.total_num = QtGui.QLabel(self.widget)
        self.total_num.setGeometry(QtCore.QRect(140, 0, 31, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.total_num.setFont(font)
        self.total_num.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.total_num.setObjectName(_fromUtf8("total_num"))
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setGeometry(QtCore.QRect(10, 0, 61, 17))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.current_num = QtGui.QLabel(self.widget)
        self.current_num.setGeometry(QtCore.QRect(80, 0, 31, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.current_num.setFont(font)
        self.current_num.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.current_num.setObjectName(_fromUtf8("current_num"))
        self.label_6 = QtGui.QLabel(self.widget)
        self.label_6.setGeometry(QtCore.QRect(120, 0, 16, 17))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.abort_button = QtGui.QPushButton(OAProgress)
        self.abort_button.setGeometry(QtCore.QRect(230, 150, 98, 27))
        self.abort_button.setObjectName(_fromUtf8("abort_button"))
        self.label_2 = QtGui.QLabel(OAProgress)
        self.label_2.setGeometry(QtCore.QRect(10, 120, 71, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.time_left = QtGui.QLabel(OAProgress)
        self.time_left.setGeometry(QtCore.QRect(90, 120, 231, 17))
        self.time_left.setObjectName(_fromUtf8("time_left"))

        self.retranslateUi(OAProgress)
        QtCore.QMetaObject.connectSlotsByName(OAProgress)

    def retranslateUi(self, OAProgress):
        OAProgress.setWindowTitle(QtGui.QApplication.translate("OAProgress", "Processing...", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("OAProgress", "Last file:", None, QtGui.QApplication.UnicodeUTF8))
        self.filename.setText(QtGui.QApplication.translate("OAProgress", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.total_num.setText(QtGui.QApplication.translate("OAProgress", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("OAProgress", "Done file ", None, QtGui.QApplication.UnicodeUTF8))
        self.current_num.setText(QtGui.QApplication.translate("OAProgress", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("OAProgress", "of", None, QtGui.QApplication.UnicodeUTF8))
        self.abort_button.setText(QtGui.QApplication.translate("OAProgress", "Abort", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("OAProgress", "Time left:", None, QtGui.QApplication.UnicodeUTF8))
        self.time_left.setText(QtGui.QApplication.translate("OAProgress", "...", None, QtGui.QApplication.UnicodeUTF8))

import OAOffline_rc
