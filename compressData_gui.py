# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\compressData.ui'
#
# Created: Sun Jan 24 16:02:50 2016
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(276, 102)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lineEdit_getDataFileSelect = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit_getDataFileSelect.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_getDataFileSelect.setReadOnly(True)
        self.lineEdit_getDataFileSelect.setObjectName(_fromUtf8("lineEdit_getDataFileSelect"))
        self.horizontalLayout_2.addWidget(self.lineEdit_getDataFileSelect)
        self.pushButton_getDataFileSelect = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_getDataFileSelect.sizePolicy().hasHeightForWidth())
        self.pushButton_getDataFileSelect.setSizePolicy(sizePolicy)
        self.pushButton_getDataFileSelect.setMaximumSize(QtCore.QSize(30, 16777215))
        self.pushButton_getDataFileSelect.setObjectName(_fromUtf8("pushButton_getDataFileSelect"))
        self.horizontalLayout_2.addWidget(self.pushButton_getDataFileSelect)
        self.horizontalLayout_2.setStretch(0, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.checkBox_autoDetectColumnSelect = QtGui.QCheckBox(self.centralwidget)
        self.checkBox_autoDetectColumnSelect.setChecked(True)
        self.checkBox_autoDetectColumnSelect.setObjectName(_fromUtf8("checkBox_autoDetectColumnSelect"))
        self.horizontalLayout.addWidget(self.checkBox_autoDetectColumnSelect)
        self.comboBox_columnSelect = QtGui.QComboBox(self.centralwidget)
        self.comboBox_columnSelect.setEnabled(False)
        self.comboBox_columnSelect.setEditable(False)
        self.comboBox_columnSelect.setObjectName(_fromUtf8("comboBox_columnSelect"))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.comboBox_columnSelect.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.comboBox_columnSelect)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Compress data", None))
        self.pushButton_getDataFileSelect.setText(_translate("MainWindow", "...", None))
        self.checkBox_autoDetectColumnSelect.setText(_translate("MainWindow", "Autodetect column", None))
        self.comboBox_columnSelect.setItemText(0, _translate("MainWindow", "Column 0", None))
        self.comboBox_columnSelect.setItemText(1, _translate("MainWindow", "Column 1", None))
        self.comboBox_columnSelect.setItemText(2, _translate("MainWindow", "Column 2", None))
        self.comboBox_columnSelect.setItemText(3, _translate("MainWindow", "Column 3", None))
        self.comboBox_columnSelect.setItemText(4, _translate("MainWindow", "Column 4", None))

