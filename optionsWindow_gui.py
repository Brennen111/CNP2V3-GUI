# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\optionsWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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
        Dialog.resize(375, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(375, 300))
        Dialog.setMaximumSize(QtCore.QSize(375, 300))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(200, 260, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.tabWidget_options = QtGui.QTabWidget(Dialog)
        self.tabWidget_options.setGeometry(QtCore.QRect(9, 9, 352, 245))
        self.tabWidget_options.setObjectName(_fromUtf8("tabWidget_options"))
        self.General = QtGui.QWidget()
        self.General.setObjectName(_fromUtf8("General"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.General)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_6 = QtGui.QLabel(self.General)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout.addWidget(self.label_6)
        self.comboBox_presets = QtGui.QComboBox(self.General)
        self.comboBox_presets.setObjectName(_fromUtf8("comboBox_presets"))
        self.comboBox_presets.addItem(_fromUtf8(""))
        self.comboBox_presets.addItem(_fromUtf8(""))
        self.comboBox_presets.addItem(_fromUtf8(""))
        self.comboBox_presets.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.comboBox_presets)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.General)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit_REFRESHRATE = QtGui.QLineEdit(self.General)
        self.lineEdit_REFRESHRATE.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_REFRESHRATE.setObjectName(_fromUtf8("lineEdit_REFRESHRATE"))
        self.gridLayout.addWidget(self.lineEdit_REFRESHRATE, 2, 1, 1, 1)
        self.lineEdit_BLOCKLENGTH = QtGui.QLineEdit(self.General)
        self.lineEdit_BLOCKLENGTH.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_BLOCKLENGTH.setObjectName(_fromUtf8("lineEdit_BLOCKLENGTH"))
        self.gridLayout.addWidget(self.lineEdit_BLOCKLENGTH, 4, 1, 1, 1)
        self.lineEdit_SUBSAMPLINGFACTOR = QtGui.QLineEdit(self.General)
        self.lineEdit_SUBSAMPLINGFACTOR.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_SUBSAMPLINGFACTOR.setObjectName(_fromUtf8("lineEdit_SUBSAMPLINGFACTOR"))
        self.gridLayout.addWidget(self.lineEdit_SUBSAMPLINGFACTOR, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.General)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.lineEdit_ADCSAMPLINGRATE = QtGui.QLineEdit(self.General)
        self.lineEdit_ADCSAMPLINGRATE.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_ADCSAMPLINGRATE.setObjectName(_fromUtf8("lineEdit_ADCSAMPLINGRATE"))
        self.gridLayout.addWidget(self.lineEdit_ADCSAMPLINGRATE, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.General)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.General)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.lineEdit_ADCBITS = QtGui.QLineEdit(self.General)
        self.lineEdit_ADCBITS.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_ADCBITS.setObjectName(_fromUtf8("lineEdit_ADCBITS"))
        self.gridLayout.addWidget(self.lineEdit_ADCBITS, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.General)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.General)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 1)
        self.lineEdit_MBCOMMONMODE = QtGui.QLineEdit(self.General)
        self.lineEdit_MBCOMMONMODE.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_MBCOMMONMODE.setObjectName(_fromUtf8("lineEdit_MBCOMMONMODE"))
        self.gridLayout.addWidget(self.lineEdit_MBCOMMONMODE, 5, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.tabWidget_options.addTab(self.General, _fromUtf8(""))
        self.IV = QtGui.QWidget()
        self.IV.setObjectName(_fromUtf8("IV"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.IV)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        spacerItem4 = QtGui.QSpacerItem(20, 27, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem4)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem5)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lineEdit_numberOfCycles = QtGui.QLineEdit(self.IV)
        self.lineEdit_numberOfCycles.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_numberOfCycles.setObjectName(_fromUtf8("lineEdit_numberOfCycles"))
        self.gridLayout_3.addWidget(self.lineEdit_numberOfCycles, 4, 1, 1, 1)
        self.lineEdit_startVoltage = QtGui.QLineEdit(self.IV)
        self.lineEdit_startVoltage.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_startVoltage.setObjectName(_fromUtf8("lineEdit_startVoltage"))
        self.gridLayout_3.addWidget(self.lineEdit_startVoltage, 0, 1, 1, 1)
        self.label_14 = QtGui.QLabel(self.IV)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_3.addWidget(self.label_14, 3, 2, 1, 1)
        self.label_11 = QtGui.QLabel(self.IV)
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_3.addWidget(self.label_11, 3, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.IV)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_3.addWidget(self.label_9, 1, 0, 1, 1)
        self.lineEdit_stopVoltage = QtGui.QLineEdit(self.IV)
        self.lineEdit_stopVoltage.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_stopVoltage.setObjectName(_fromUtf8("lineEdit_stopVoltage"))
        self.gridLayout_3.addWidget(self.lineEdit_stopVoltage, 1, 1, 1, 1)
        self.label_12 = QtGui.QLabel(self.IV)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_3.addWidget(self.label_12, 0, 2, 1, 1)
        self.label_13 = QtGui.QLabel(self.IV)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_3.addWidget(self.label_13, 1, 2, 1, 1)
        self.lineEdit_timeStep = QtGui.QLineEdit(self.IV)
        self.lineEdit_timeStep.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_timeStep.setObjectName(_fromUtf8("lineEdit_timeStep"))
        self.gridLayout_3.addWidget(self.lineEdit_timeStep, 3, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.IV)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_3.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_10 = QtGui.QLabel(self.IV)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_3.addWidget(self.label_10, 4, 0, 1, 1)
        self.label_15 = QtGui.QLabel(self.IV)
        self.label_15.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_3.addWidget(self.label_15, 2, 0, 1, 1)
        self.lineEdit_voltageStep = QtGui.QLineEdit(self.IV)
        self.lineEdit_voltageStep.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit_voltageStep.setObjectName(_fromUtf8("lineEdit_voltageStep"))
        self.gridLayout_3.addWidget(self.lineEdit_voltageStep, 2, 1, 1, 1)
        self.label_16 = QtGui.QLabel(self.IV)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_3.addWidget(self.label_16, 2, 2, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_3)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        spacerItem7 = QtGui.QSpacerItem(20, 28, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem7)
        self.tabWidget_options.addTab(self.IV, _fromUtf8(""))

        self.retranslateUi(Dialog)
        self.tabWidget_options.setCurrentIndex(0)
        self.comboBox_presets.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.comboBox_presets, self.lineEdit_ADCBITS)
        Dialog.setTabOrder(self.lineEdit_ADCBITS, self.lineEdit_SUBSAMPLINGFACTOR)
        Dialog.setTabOrder(self.lineEdit_SUBSAMPLINGFACTOR, self.lineEdit_REFRESHRATE)
        Dialog.setTabOrder(self.lineEdit_REFRESHRATE, self.lineEdit_ADCSAMPLINGRATE)
        Dialog.setTabOrder(self.lineEdit_ADCSAMPLINGRATE, self.lineEdit_BLOCKLENGTH)
        Dialog.setTabOrder(self.lineEdit_BLOCKLENGTH, self.lineEdit_MBCOMMONMODE)
        Dialog.setTabOrder(self.lineEdit_MBCOMMONMODE, self.buttonBox)
        Dialog.setTabOrder(self.buttonBox, self.tabWidget_options)
        Dialog.setTabOrder(self.tabWidget_options, self.lineEdit_startVoltage)
        Dialog.setTabOrder(self.lineEdit_startVoltage, self.lineEdit_stopVoltage)
        Dialog.setTabOrder(self.lineEdit_stopVoltage, self.lineEdit_voltageStep)
        Dialog.setTabOrder(self.lineEdit_voltageStep, self.lineEdit_timeStep)
        Dialog.setTabOrder(self.lineEdit_timeStep, self.lineEdit_numberOfCycles)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Options", None))
        self.label_6.setText(_translate("Dialog", "Presets", None))
        self.comboBox_presets.setItemText(0, _translate("Dialog", "Custom", None))
        self.comboBox_presets.setItemText(1, _translate("Dialog", "Default", None))
        self.comboBox_presets.setItemText(2, _translate("Dialog", "Speed", None))
        self.comboBox_presets.setItemText(3, _translate("Dialog", "Accuracy", None))
        self.label_2.setText(_translate("Dialog", "Subsampling factor", None))
        self.lineEdit_REFRESHRATE.setText(_translate("Dialog", "10", None))
        self.lineEdit_BLOCKLENGTH.setText(_translate("Dialog", "1024", None))
        self.lineEdit_SUBSAMPLINGFACTOR.setText(_translate("Dialog", "10", None))
        self.label_3.setText(_translate("Dialog", "Refresh rate", None))
        self.lineEdit_ADCSAMPLINGRATE.setText(_translate("Dialog", "156.25e6/4", None))
        self.label_4.setText(_translate("Dialog", "ADC sampling rate", None))
        self.label_5.setText(_translate("Dialog", "Block length", None))
        self.lineEdit_ADCBITS.setText(_translate("Dialog", "12", None))
        self.label.setText(_translate("Dialog", "ADCBITS", None))
        self.label_7.setText(_translate("Dialog", "MB Common mode", None))
        self.lineEdit_MBCOMMONMODE.setText(_translate("Dialog", "1.65", None))
        self.tabWidget_options.setTabText(self.tabWidget_options.indexOf(self.General), _translate("Dialog", "General", None))
        self.lineEdit_numberOfCycles.setText(_translate("Dialog", "0", None))
        self.lineEdit_startVoltage.setText(_translate("Dialog", "-0.5", None))
        self.label_14.setText(_translate("Dialog", "ms", None))
        self.label_11.setText(_translate("Dialog", "Time step", None))
        self.label_9.setText(_translate("Dialog", "Stop voltage", None))
        self.lineEdit_stopVoltage.setText(_translate("Dialog", "0.5", None))
        self.label_12.setText(_translate("Dialog", "V", None))
        self.label_13.setText(_translate("Dialog", "V", None))
        self.lineEdit_timeStep.setText(_translate("Dialog", "500", None))
        self.label_8.setText(_translate("Dialog", "Start voltage", None))
        self.label_10.setText(_translate("Dialog", "No. of cycles", None))
        self.label_15.setText(_translate("Dialog", "Voltage step", None))
        self.lineEdit_voltageStep.setText(_translate("Dialog", "100", None))
        self.label_16.setText(_translate("Dialog", "mV", None))
        self.tabWidget_options.setTabText(self.tabWidget_options.indexOf(self.IV), _translate("Dialog", "IV", None))

