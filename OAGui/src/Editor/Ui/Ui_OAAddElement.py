# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/media/Home/Documents/SoftProjects/LDM/OAGui/src/Editor/Ui/OAAddElement.ui'
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

class Ui_OAAddElement(object):
    def setupUi(self, OAAddElement):
        OAAddElement.setObjectName(_fromUtf8("OAAddElement"))
        OAAddElement.resize(401, 241)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/mainIcon")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        OAAddElement.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(OAAddElement)
        self.buttonBox.setGeometry(QtCore.QRect(30, 190, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.name = QtGui.QLineEdit(OAAddElement)
        self.name.setGeometry(QtCore.QRect(100, 90, 231, 27))
        self.name.setObjectName(_fromUtf8("name"))
        self.type = QtGui.QComboBox(OAAddElement)
        self.type.setGeometry(QtCore.QRect(100, 130, 231, 27))
        self.type.setObjectName(_fromUtf8("type"))
        self.label = QtGui.QLabel(OAAddElement)
        self.label.setGeometry(QtCore.QRect(27, 94, 66, 17))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(OAAddElement)
        self.label_2.setGeometry(QtCore.QRect(24, 135, 66, 17))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.message = QtGui.QLabel(OAAddElement)
        self.message.setGeometry(QtCore.QRect(20, 10, 351, 61))
        self.message.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.message.setWordWrap(True)
        self.message.setObjectName(_fromUtf8("message"))

        self.retranslateUi(OAAddElement)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), OAAddElement.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OAAddElement.reject)
        QtCore.QMetaObject.connectSlotsByName(OAAddElement)

    def retranslateUi(self, OAAddElement):
        OAAddElement.setWindowTitle(QtGui.QApplication.translate("OAAddElement", "Add new %s", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("OAAddElement", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("OAAddElement", "Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.message.setText(QtGui.QApplication.translate("OAAddElement", "<html><head/><body><p>Please insert the name and select the type for the new %s. Then press <span style=\" font-weight:600;\">OK</span> to confirm or <span style=\" font-weight:600;\">Cancel</span> to abort.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import OAEditor_rc
