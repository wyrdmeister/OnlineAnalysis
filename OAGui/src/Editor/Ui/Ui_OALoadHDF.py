# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/media/Home/Documents/SoftProjects/LDM/OAGui/src/Editor/Ui/OALoadHDF.ui'
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

class Ui_OALoadHDF(object):
    def setupUi(self, OALoadHDF):
        OALoadHDF.setObjectName(_fromUtf8("OALoadHDF"))
        OALoadHDF.resize(871, 491)
        OALoadHDF.setMinimumSize(QtCore.QSize(871, 491))
        OALoadHDF.setMaximumSize(QtCore.QSize(871, 491))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/mainIcon")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        OALoadHDF.setWindowIcon(icon)
        OALoadHDF.setModal(True)
        self.dataset_list = QtGui.QTableView(OALoadHDF)
        self.dataset_list.setGeometry(QtCore.QRect(30, 160, 811, 251))
        self.dataset_list.setObjectName(_fromUtf8("dataset_list"))
        self.cancel = QtGui.QPushButton(OALoadHDF)
        self.cancel.setGeometry(QtCore.QRect(500, 430, 98, 27))
        self.cancel.setObjectName(_fromUtf8("cancel"))
        self.replace = QtGui.QPushButton(OALoadHDF)
        self.replace.setGeometry(QtCore.QRect(620, 430, 98, 27))
        self.replace.setObjectName(_fromUtf8("replace"))
        self.append = QtGui.QPushButton(OALoadHDF)
        self.append.setGeometry(QtCore.QRect(740, 430, 98, 27))
        self.append.setObjectName(_fromUtf8("append"))
        self.label = QtGui.QLabel(OALoadHDF)
        self.label.setGeometry(QtCore.QRect(30, 10, 811, 131))
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(OALoadHDF)
        QtCore.QMetaObject.connectSlotsByName(OALoadHDF)

    def retranslateUi(self, OALoadHDF):
        OALoadHDF.setWindowTitle(QtGui.QApplication.translate("OALoadHDF", "Load from HDF5", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("OALoadHDF", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.replace.setText(QtGui.QApplication.translate("OALoadHDF", "Replace", None, QtGui.QApplication.UnicodeUTF8))
        self.append.setText(QtGui.QApplication.translate("OALoadHDF", "Append", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("OALoadHDF", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Load from HDF5</span></p><p>Select the datasets you want and the press <span style=\" font-weight:600;\">Replace</span> to replace the existing configuration with the new one. Instead press <span style=\" font-weight:600;\">Append</span> to append the selected datasets to the present configuration. Press <span style=\" font-weight:600;\">Cancel</span> to abort.</p><p>It\'s possible to rename a dataset directly in this window. The HDF5 file path instead cannot be changed.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import OAEditor_rc
