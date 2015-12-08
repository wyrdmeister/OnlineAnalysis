# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/media/Home/Documents/SoftProjects/LDM/OAGui/src/Control/Ui/OAMultiplot.ui'
#
# Created: Tue Apr 16 14:32:36 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_OAMultiplot(object):
    def setupUi(self, OAMultiplot):
        OAMultiplot.setObjectName(_fromUtf8("OAMultiplot"))
        OAMultiplot.resize(773, 489)
        OAMultiplot.setMinimumSize(QtCore.QSize(731, 489))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/Images/oa_editor.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        OAMultiplot.setWindowIcon(icon)
        self.plot_area = QtGui.QWidget(OAMultiplot)
        self.plot_area.setGeometry(QtCore.QRect(10, 10, 591, 431))
        self.plot_area.setObjectName(_fromUtf8("plot_area"))
        self.close_button = QtGui.QPushButton(OAMultiplot)
        self.close_button.setGeometry(QtCore.QRect(660, 450, 98, 27))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.control_frame = QtGui.QFrame(OAMultiplot)
        self.control_frame.setGeometry(QtCore.QRect(610, 10, 151, 381))
        self.control_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.control_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.control_frame.setObjectName(_fromUtf8("control_frame"))
        self.plot_selector = QtGui.QComboBox(self.control_frame)
        self.plot_selector.setGeometry(QtCore.QRect(10, 10, 131, 27))
        self.plot_selector.setObjectName(_fromUtf8("plot_selector"))
        self.plot_scatter = QtGui.QPushButton(self.control_frame)
        self.plot_scatter.setGeometry(QtCore.QRect(10, 90, 131, 27))
        self.plot_scatter.setObjectName(_fromUtf8("plot_scatter"))
        self.plot_hist2d = QtGui.QPushButton(self.control_frame)
        self.plot_hist2d.setGeometry(QtCore.QRect(10, 130, 131, 27))
        self.plot_hist2d.setObjectName(_fromUtf8("plot_hist2d"))
        self.zmin_slider = QtGui.QSlider(self.control_frame)
        self.zmin_slider.setGeometry(QtCore.QRect(10, 270, 131, 29))
        self.zmin_slider.setOrientation(QtCore.Qt.Horizontal)
        self.zmin_slider.setObjectName(_fromUtf8("zmin_slider"))
        self.zmax_slider = QtGui.QSlider(self.control_frame)
        self.zmax_slider.setGeometry(QtCore.QRect(10, 320, 131, 29))
        self.zmax_slider.setProperty("value", 99)
        self.zmax_slider.setOrientation(QtCore.Qt.Horizontal)
        self.zmax_slider.setObjectName(_fromUtf8("zmax_slider"))
        self.en_xautoscale = QtGui.QCheckBox(self.control_frame)
        self.en_xautoscale.setGeometry(QtCore.QRect(10, 200, 121, 22))
        self.en_xautoscale.setObjectName(_fromUtf8("en_xautoscale"))
        self.label = QtGui.QLabel(self.control_frame)
        self.label.setGeometry(QtCore.QRect(10, 300, 41, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.control_frame)
        self.label_2.setGeometry(QtCore.QRect(10, 350, 41, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.zmin_value = QtGui.QLabel(self.control_frame)
        self.zmin_value.setGeometry(QtCore.QRect(70, 300, 66, 17))
        self.zmin_value.setObjectName(_fromUtf8("zmin_value"))
        self.zmax_value = QtGui.QLabel(self.control_frame)
        self.zmax_value.setGeometry(QtCore.QRect(70, 350, 66, 17))
        self.zmax_value.setObjectName(_fromUtf8("zmax_value"))
        self.en_yautoscale = QtGui.QCheckBox(self.control_frame)
        self.en_yautoscale.setGeometry(QtCore.QRect(10, 220, 121, 22))
        self.en_yautoscale.setObjectName(_fromUtf8("en_yautoscale"))
        self.en_zautoscale = QtGui.QCheckBox(self.control_frame)
        self.en_zautoscale.setGeometry(QtCore.QRect(10, 240, 121, 22))
        self.en_zautoscale.setObjectName(_fromUtf8("en_zautoscale"))
        self.plot_reset = QtGui.QPushButton(self.control_frame)
        self.plot_reset.setGeometry(QtCore.QRect(10, 50, 131, 27))
        self.plot_reset.setObjectName(_fromUtf8("plot_reset"))
        self.hist_xbin = QtGui.QSpinBox(self.control_frame)
        self.hist_xbin.setGeometry(QtCore.QRect(10, 160, 60, 27))
        self.hist_xbin.setMaximum(1000)
        self.hist_xbin.setObjectName(_fromUtf8("hist_xbin"))
        self.hist_ybin = QtGui.QSpinBox(self.control_frame)
        self.hist_ybin.setGeometry(QtCore.QRect(80, 160, 60, 27))
        self.hist_ybin.setMaximum(1000)
        self.hist_ybin.setObjectName(_fromUtf8("hist_ybin"))

        self.retranslateUi(OAMultiplot)
        QtCore.QMetaObject.connectSlotsByName(OAMultiplot)

    def retranslateUi(self, OAMultiplot):
        OAMultiplot.setWindowTitle(QtGui.QApplication.translate("OAMultiplot", "OA Data Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.close_button.setText(QtGui.QApplication.translate("OAMultiplot", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.plot_scatter.setText(QtGui.QApplication.translate("OAMultiplot", "Scatter", None, QtGui.QApplication.UnicodeUTF8))
        self.plot_hist2d.setText(QtGui.QApplication.translate("OAMultiplot", "2D histogram", None, QtGui.QApplication.UnicodeUTF8))
        self.en_xautoscale.setText(QtGui.QApplication.translate("OAMultiplot", "X Autoscale", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("OAMultiplot", "Zmin", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("OAMultiplot", "Zmax", None, QtGui.QApplication.UnicodeUTF8))
        self.zmin_value.setText(QtGui.QApplication.translate("OAMultiplot", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.zmax_value.setText(QtGui.QApplication.translate("OAMultiplot", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.en_yautoscale.setText(QtGui.QApplication.translate("OAMultiplot", "Y Autoscale", None, QtGui.QApplication.UnicodeUTF8))
        self.en_zautoscale.setText(QtGui.QApplication.translate("OAMultiplot", "Z Autoscale", None, QtGui.QApplication.UnicodeUTF8))
        self.plot_reset.setText(QtGui.QApplication.translate("OAMultiplot", "Reset plot", None, QtGui.QApplication.UnicodeUTF8))

import OAControl_rc
