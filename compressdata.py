import os
import json
from PyQt4 import QtCore, QtGui
from compressData_gui import Ui_MainWindow
import workerobjects
from shutil import copy
import numpy

class CompressData(QtGui.QMainWindow):
    def __init__(self, dictOfConstants):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dictOfConstants = dictOfConstants

        self.ui.pushButton_getDataFileSelect.clicked.connect(self.pushButton_getDataFileSelect_clicked)
        self.ui.checkBox_autoDetectColumnSelect.stateChanged.connect(self.checkBox_autoDetectColumnSelect_stateChanged)
        self.ui.comboBox_columnSelect.activated.connect(self.comboBox_columnSelect_activated)

        # The method from the worker object is used directly in the main GUI thread in this window
        self.processRawDataWorkerInstance = workerobjects.ProcessRawDataWorker(self, dictOfConstants, None)

    def pushButton_getDataFileSelect_clicked(self):
        fileSelecter = QtGui.QFileDialog()
        listLoadFileSelected = fileSelecter.getOpenFileNames(self, "Choose file", "./", filter="Hex files (*.hex)", selectedFilter="*.hex")
        listLoadFileSelected = [str(x).replace('\\', '/') for x in listLoadFileSelected]
        for dataLoadFileSelected in listLoadFileSelected:
            if dataLoadFileSelected != '':
                self.currentHexFileName = str(dataLoadFileSelected.split('/')[-1])
                self.ui.lineEdit_getDataFileSelect.setText(self.currentHexFileName)
                self.currentDirectoryName = str(dataLoadFileSelected[:-len(self.currentHexFileName)])
                self.loadHexData(dataLoadFileSelected)

    def loadHexData(self, dataLoadFileSelected=""):
        self.dataInMemory = 0
        print dataLoadFileSelected
        if dataLoadFileSelected != "":
            if self.ui.checkBox_autoDetectColumnSelect.isChecked():
                configLoadFileSelected = dataLoadFileSelected[0:len(dataLoadFileSelected) - 3] + "cfg"
                try:
                    self.f = open(configLoadFileSelected, 'r')
                    stateConfig = json.load(self.f)
                    # self.loadState(stateConfig)
                    self.ui.comboBox_columnSelect.setCurrentIndex(stateConfig['columnSelect'])
                    self.comboBox_columnSelect_activated(stateConfig['columnSelect'])
                    self.f.close()
                except:
                    print "Could not find a corresponding cfg file"
            self.f = open(dataLoadFileSelected, 'rb')
            self.processRawDataWorkerInstance.rawData = self.f.read()
            self.compressedData = self.processRawDataWorkerInstance.compressData()
            # self.processRawDataWorkerInstance.rawData = self.processRawDataWorkerInstance.rawData[0:len(self.processRawDataWorkerInstance.rawData)/10]
            print len(self.processRawDataWorkerInstance.rawData)
            self.writeCompressedDataToDisk()
            # windowTitle = dataLoadFileSelected.split('/')[-2] + '/' + dataLoadFileSelected.split('/')[-1]
            # self.setWindowTitle(windowTitle)
            # self.processRawDataWorkerInstance.rawData = self.processRawDataWorkerInstance.rawData[:-1]
            self.f.close()
        else:
            pass

    def checkBox_autoDetectColumnSelect_stateChanged(self, state):
        if self.ui.checkBox_autoDetectColumnSelect.isChecked():
            self.ui.comboBox_columnSelect.setEnabled(False)
        else:
            self.ui.comboBox_columnSelect.setEnabled(True)

    def comboBox_columnSelect_activated(self, index):
        self.columnSelect = index

    def writeCompressedDataToDisk(self):
        self.defaultDirectory = self.currentDirectoryName[:-1] + '_compressed/'
        if not os.path.exists(self.defaultDirectory):
            os.makedirs(self.defaultDirectory)
        # print len(self.rawData[0])
        self.fileName = self.defaultDirectory + self.currentHexFileName
        if os.path.exists(self.fileName):
            self.f = open(self.fileName, 'w+b')
        else:
            self.f = open(self.fileName, 'a+b')
        # While logging is enabled, write in 1 second bursts. Finish writing everything that is in memory when logging is disabled
        self.f.write(self.compressedData)
        self.f.close()
        self.configFileName = self.currentDirectoryName + self.currentHexFileName[0:-3] + "cfg"
        copy(self.configFileName, self.defaultDirectory)
