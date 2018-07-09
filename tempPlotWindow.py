# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\tempPlotWindow.ui'
#
# Created: Tue Feb 17 11:19:47 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(561, 485)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 35, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.tabWidget_plot = QtGui.QTabWidget(Dialog)
        self.tabWidget_plot.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget_plot.setObjectName(_fromUtf8("tabWidget_plot"))
        self.tab_time = QtGui.QWidget()
        self.tab_time.setObjectName(_fromUtf8("tab_time"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.tab_time)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.graphicsView_time = PlotWidget(self.tab_time)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView_time.sizePolicy().hasHeightForWidth())
        self.graphicsView_time.setSizePolicy(sizePolicy)
        self.graphicsView_time.setMinimumSize(QtCore.QSize(400, 300))
        self.graphicsView_time.setObjectName(_fromUtf8("graphicsView_time"))
        self.horizontalLayout_2.addWidget(self.graphicsView_time)
        self.tabWidget_plot.addTab(self.tab_time, _fromUtf8(""))
        self.tab_frequency = QtGui.QWidget()
        self.tab_frequency.setObjectName(_fromUtf8("tab_frequency"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.tab_frequency)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.graphicsView_frequency = PlotWidget(self.tab_frequency)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView_frequency.sizePolicy().hasHeightForWidth())
        self.graphicsView_frequency.setSizePolicy(sizePolicy)
        self.graphicsView_frequency.setMinimumSize(QtCore.QSize(400, 300))
        self.graphicsView_frequency.setObjectName(_fromUtf8("graphicsView_frequency"))
        self.horizontalLayout_3.addWidget(self.graphicsView_frequency)
        self.tabWidget_plot.addTab(self.tab_frequency, _fromUtf8(""))
        self.tab_histogram = QtGui.QWidget()
        self.tab_histogram.setObjectName(_fromUtf8("tab_histogram"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.tab_histogram)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.graphicsView_histogram = PlotWidget(self.tab_histogram)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView_histogram.sizePolicy().hasHeightForWidth())
        self.graphicsView_histogram.setSizePolicy(sizePolicy)
        self.graphicsView_histogram.setMinimumSize(QtCore.QSize(400, 300))
        self.graphicsView_histogram.setObjectName(_fromUtf8("graphicsView_histogram"))
        self.horizontalLayout_4.addWidget(self.graphicsView_histogram)
        self.tabWidget_plot.addTab(self.tab_histogram, _fromUtf8(""))
        self.horizontalLayout_5.addWidget(self.tabWidget_plot)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.pushButton_loadData = QtGui.QPushButton(Dialog)
        self.pushButton_loadData.setObjectName(_fromUtf8("pushButton_loadData"))
        self.horizontalLayout.addWidget(self.pushButton_loadData)
        self.comboBox_columnSelect = QtGui.QComboBox(Dialog)
        self.comboBox_columnSelect.setObjectName(_fromUtf8("comboBox_columnSelect"))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.comboBox_columnSelect)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem5 = QtGui.QSpacerItem(20, 36, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem5)

        self.retranslateUi(Dialog)
        self.tabWidget_plot.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.tabWidget_plot.setTabText(self.tabWidget_plot.indexOf(self.tab_time), _translate("Dialog", "Time", None))
        self.tabWidget_plot.setTabText(self.tabWidget_plot.indexOf(self.tab_frequency), _translate("Dialog", "Frequency", None))
        self.tabWidget_plot.setTabText(self.tabWidget_plot.indexOf(self.tab_histogram), _translate("Dialog", "Histogram", None))
        self.pushButton_loadData.setText(_translate("Dialog", "Choose file", None))
        self.comboBox_columnSelect.setItemText(0, _translate("Dialog", "Column 0", None))
        self.comboBox_columnSelect.setItemText(1, _translate("Dialog", "Column 1", None))
        self.comboBox_columnSelect.setItemText(2, _translate("Dialog", "Column 2", None))
        self.comboBox_columnSelect.setItemText(3, _translate("Dialog", "Column 3", None))
        self.comboBox_columnSelect.setItemText(4, _translate("Dialog", "Column 4", None))

from pyqtgraph import PlotWidget
