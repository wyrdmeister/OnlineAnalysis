# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/media/Home/Documents/SoftProjects/LDM/OAGui/src/Offline/Ui/OAOffline.ui'
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

class Ui_OAOffline(object):
    def setupUi(self, OAOffline):
        OAOffline.setObjectName(_fromUtf8("OAOffline"))
        OAOffline.resize(851, 761)
        OAOffline.setMinimumSize(QtCore.QSize(851, 761))
        OAOffline.setMaximumSize(QtCore.QSize(851, 761))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/mainIcon")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        OAOffline.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(OAOffline)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.result_list = QtGui.QTableView(self.centralwidget)
        self.result_list.setGeometry(QtCore.QRect(30, 110, 791, 351))
        self.result_list.setObjectName(_fromUtf8("result_list"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 90, 61, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(35, 20, 101, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.config_file = QtGui.QLineEdit(self.centralwidget)
        self.config_file.setGeometry(QtCore.QRect(150, 16, 461, 27))
        self.config_file.setObjectName(_fromUtf8("config_file"))
        self.config_browse = QtGui.QPushButton(self.centralwidget)
        self.config_browse.setGeometry(QtCore.QRect(620, 16, 81, 27))
        self.config_browse.setObjectName(_fromUtf8("config_browse"))
        self.horizontalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 470, 501, 41))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.plot_selection = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.plot_selection.setObjectName(_fromUtf8("plot_selection"))
        self.horizontalLayout.addWidget(self.plot_selection)
        self.save_selection = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.save_selection.setObjectName(_fromUtf8("save_selection"))
        self.horizontalLayout.addWidget(self.save_selection)
        self.saveall_button = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.saveall_button.setObjectName(_fromUtf8("saveall_button"))
        self.horizontalLayout.addWidget(self.saveall_button)
        self.clear_button = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.clear_button.setObjectName(_fromUtf8("clear_button"))
        self.horizontalLayout.addWidget(self.clear_button)
        self.exit_button = QtGui.QPushButton(self.centralwidget)
        self.exit_button.setGeometry(QtCore.QRect(710, 477, 113, 27))
        self.exit_button.setObjectName(_fromUtf8("exit_button"))
        self.label_8 = QtGui.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(30, 530, 131, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.error_log = QtGui.QListWidget(self.centralwidget)
        self.error_log.setGeometry(QtCore.QRect(30, 550, 791, 191))
        self.error_log.setObjectName(_fromUtf8("error_log"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(35, 54, 101, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.inpath_browse = QtGui.QPushButton(self.centralwidget)
        self.inpath_browse.setGeometry(QtCore.QRect(620, 50, 81, 27))
        self.inpath_browse.setObjectName(_fromUtf8("inpath_browse"))
        self.start_button = QtGui.QPushButton(self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(710, 16, 111, 61))
        self.start_button.setObjectName(_fromUtf8("start_button"))
        self.inpath = QtGui.QComboBox(self.centralwidget)
        self.inpath.setGeometry(QtCore.QRect(150, 50, 461, 27))
        self.inpath.setEditable(True)
        self.inpath.setObjectName(_fromUtf8("inpath"))
        self.inpath.addItem(_fromUtf8(""))
        OAOffline.setCentralWidget(self.centralwidget)
        self.action_exit = QtGui.QAction(OAOffline)
        self.action_exit.setObjectName(_fromUtf8("action_exit"))
        self.action_reload = QtGui.QAction(OAOffline)
        self.action_reload.setObjectName(_fromUtf8("action_reload"))

        self.retranslateUi(OAOffline)
        QtCore.QMetaObject.connectSlotsByName(OAOffline)
        OAOffline.setTabOrder(self.config_file, self.config_browse)
        OAOffline.setTabOrder(self.config_browse, self.result_list)
        OAOffline.setTabOrder(self.result_list, self.plot_selection)
        OAOffline.setTabOrder(self.plot_selection, self.save_selection)
        OAOffline.setTabOrder(self.save_selection, self.saveall_button)
        OAOffline.setTabOrder(self.saveall_button, self.clear_button)

    def retranslateUi(self, OAOffline):
        OAOffline.setWindowTitle(QtGui.QApplication.translate("OAOffline", "Offline OA Control", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("OAOffline", "Results", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("OAOffline", "Configuration:", None, QtGui.QApplication.UnicodeUTF8))
        self.config_file.setText(QtGui.QApplication.translate("OAOffline", "../oa-config.xml", None, QtGui.QApplication.UnicodeUTF8))
        self.config_browse.setText(QtGui.QApplication.translate("OAOffline", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.plot_selection.setText(QtGui.QApplication.translate("OAOffline", "Plot selection", None, QtGui.QApplication.UnicodeUTF8))
        self.save_selection.setText(QtGui.QApplication.translate("OAOffline", "Save selection", None, QtGui.QApplication.UnicodeUTF8))
        self.saveall_button.setText(QtGui.QApplication.translate("OAOffline", "Save all", None, QtGui.QApplication.UnicodeUTF8))
        self.clear_button.setText(QtGui.QApplication.translate("OAOffline", "Clear all", None, QtGui.QApplication.UnicodeUTF8))
        self.exit_button.setText(QtGui.QApplication.translate("OAOffline", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("OAOffline", "Error log", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("OAOffline", "Path:", None, QtGui.QApplication.UnicodeUTF8))
        self.inpath_browse.setText(QtGui.QApplication.translate("OAOffline", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.start_button.setText(QtGui.QApplication.translate("OAOffline", "Start\n"
"processing", None, QtGui.QApplication.UnicodeUTF8))
        self.inpath.setItemText(0, QtGui.QApplication.translate("OAOffline", "/home/ldm/.gvfs/store on online4ldm.esce/investigations/20124027/Xe_effusive/Xe_002", None, QtGui.QApplication.UnicodeUTF8))
        self.action_exit.setText(QtGui.QApplication.translate("OAOffline", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.action_reload.setText(QtGui.QApplication.translate("OAOffline", "Reload configuration", None, QtGui.QApplication.UnicodeUTF8))

import OAOffline_rc
