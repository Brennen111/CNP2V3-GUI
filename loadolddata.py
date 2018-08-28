# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import time
import numpy
import pyqtgraph, pyqtgraph.exporters
import json
import os, glob

import globalConstants
import workerobjects
import channelComponents
from loadOldData_gui import Ui_MainWindow
from optionswindow import OptionsWindow
from progressbar import ProgressBarWindow

pyqtgraph.setConfigOption('background', 'w') #Set background to white
pyqtgraph.setConfigOption('foreground', 'k') #Set foreground to black

class LoadOldDataWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(LoadOldDataWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #######################################################################
        # Default initializations
        #######################################################################
        self.ui.lineEdit_RDCFB.setPlaceholderText("50")
        self.columnSelect = 0
        self.RDCFB = 50e6
        self.ui.lineEdit_livePreviewFilterBandwidth.setPlaceholderText("100")
        self.livePreviewFilterBandwidth = 100e3
        self.dataLoadFileSelected = ''
        self.masterRawData = []
        self.slaveRawData = []
        self.masterDataInMemory = 0
        self.slaveDataInMemory = 0
        self.dataInMemory = 0
        #self.IDCOffset = 0
        #self.IDCRelative = 0
        #self.f = []
        #self.PSD = []
        #self.dataToDisplay = []
        #self.RMSNoise_100kHz = 0
        #self.RMSNoise_1MHz = 0
        #self.RMSNoise_10MHz = 0
        self.threshold = None
        self.currentEvent = 1
        self.histogramModeSelect = 0
        self.thresholdType = 0

        self.adcList = []
        for i in xrange(5):
            self.adcList.append(channelComponents.ADC())

        #######################################################################
        # Connecting signals to relevant functions
        #######################################################################
        self.ui.comboBox_columnSelect.activated.connect(self.comboBox_columnSelect_activated)

        self.ui.tabWidget_plot.currentChanged.connect(self.updateDisplayData)

        self.ui.action_loadData.triggered.connect(self.action_loadData_triggered)
        self.ui.action_nextFile.triggered.connect(self.action_nextFile_triggered)
        self.ui.action_nextFile.setEnabled(False)
        self.ui.action_previousFile.triggered.connect(self.action_previousFile_triggered)
        self.ui.action_previousFile.setEnabled(False)
        self.ui.action_deleteFile.triggered.connect(self.action_deleteFile_triggered)
        self.ui.action_deleteFile.setEnabled(False)
        self.ui.action_options.triggered.connect(self.action_options_triggered)
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_capturePlot.triggered.connect(self.action_capturePlot_triggered)
        self.ui.action_addVerticalMarker.triggered.connect(self.action_addVerticalMarker_triggered)
        self.ui.action_addNoiseFit.triggered.connect(self.action_addNoiseFit_triggered)
        self.ui.action_exportAllEventsAsCSV.triggered.connect(self.action_exportAllEventsAsCSV_triggered)

        self.ui.lineEdit_RDCFB.editingFinished.connect(self.lineEdit_RDCFB_editingFinished)

        self.ui.lineEdit_livePreviewFilterBandwidth.editingFinished.connect(self.lineEdit_livePreviewFilterBandwidth_editingFinished)
        self.ui.checkBox_enableLivePreviewFilter.clicked.connect(self.lineEdit_livePreviewFilterBandwidth_editingFinished)
        self.ui.checkBox_enableWaveletDenoising.clicked.connect(self.lineEdit_livePreviewFilterBandwidth_editingFinished)
        self.ui.lineEdit_motherWavelet.editingFinished.connect(self.lineEdit_livePreviewFilterBandwidth_editingFinished)

        self.ui.pushButton_analyzeData.clicked.connect(self.pushButton_analyzeData_clicked)
        self.ui.pushButton_nextEvent.clicked.connect(lambda: self.graphicsView_eventViewer_eventChanged(relative=1))
        self.ui.pushButton_previousEvent.clicked.connect(lambda: self.graphicsView_eventViewer_eventChanged(relative=-1))
        self.ui.lineEdit_currentEvent.editingFinished.connect(lambda: self.graphicsView_eventViewer_eventChanged(absolute=int(self.ui.lineEdit_currentEvent.text())))

        self.ui.comboBox_histogramModeSelect.activated.connect(self.comboBox_histogramModeSelect_activated)
        self.ui.checkBox_enableCUSUM.clicked.connect(lambda: self.ui.lineEdit_CUSUMDelta.setEnabled(self.ui.checkBox_enableCUSUM.isChecked()))

        self.ui.comboBox_thresholdUnitsSelect.activated.connect(self.comboBox_thresholdUnitsSelect_activated)
        self.ui.lineEdit_threshold.editingFinished.connect(self.lineEdit_threshold_editingFinished)

        #######################################################################
        # Initializing plots
        #######################################################################
        self.ui.graphicsView_time_plot = self.ui.graphicsView_time.plot(numpy.linspace(0, 0.1, 100), numpy.ones(100), pen='b')
        self.ui.graphicsView_time.setClipToView(True) # Setting clipToView after downsampling significantly degrades performance
        self.ui.graphicsView_time_plot.setDownsampling(auto=True, method='peak') # Only downsample the time plot instead of the entire viewbox
        self.ui.graphicsView_time.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_time.setLabel(axis='bottom', text='Time', units='s')
        self.ui.graphicsView_time.setLabel(axis='left', text='I', units='A')
        self.ui.graphicsView_time.disableAutoRange()

        self.ui.graphicsView_frequency_plot = self.ui.graphicsView_frequency.plot(numpy.linspace(100, 10e6, 100), numpy.ones(100), pen='b')
        self.ui.graphicsView_frequency.setLogMode(x=True, y=True)
        self.ui.graphicsView_frequency.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_frequency.setLabel(axis='bottom', text='Frequency', units='Hz')
        self.ui.graphicsView_frequency.setLabel(axis='left', text='Output noise power (V<sup>2</sup>/Hz)')
        self.ui.graphicsView_frequency.disableAutoRange()

        self.ui.graphicsView_histogram_plot = self.ui.graphicsView_histogram.plot(numpy.linspace(0, 1, 100), numpy.zeros(100), pen='b')
        # self.ui.graphicsView_histogram.plot(self.bins, self.histogramView, pen='b', stepMode=True)
        self.ui.graphicsView_histogram.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_histogram.setLabel(axis='bottom', text='Dwell Time', units='s')
        self.ui.graphicsView_histogram.setLabel(axis='left', text='I', units='A')
        self.ui.graphicsView_histogram.disableAutoRange()

        self.ui.tabWidget_plot.setTabEnabled(3, False) #Disable event viewer tab on startup
        self.ui.graphicsView_eventViewer_plot = self.ui.graphicsView_eventViewer.plot(numpy.linspace(0, 1, 100), numpy.zeros(100), pen='b')
        self.ui.graphicsView_eventViewer_plotFit = self.ui.graphicsView_eventViewer.plot(numpy.empty(0), numpy.empty(0), pen='b')
        self.ui.graphicsView_eventViewer.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_eventViewer.setLabel(axis='bottom', text='Time', units='s')
        self.ui.graphicsView_eventViewer.setLabel(axis='left', text='I', units='A')
        self.ui.graphicsView_eventViewer.disableAutoRange()

        #######################################################################
        # Thread instantiation
        #######################################################################
        self.PSDThread = QtCore.QThread()
        self.PSDWorkerInstance = workerobjects.PSDWorker(self)
        self.PSDWorkerInstance.moveToThread(self.PSDThread)
        self.PSDWorkerInstance.PSDReady.connect(self.displayData)
        self.PSDWorkerInstance.finished.connect(self.PSDThread.quit)
        self.PSDWorkerInstance.finished.connect(self.updateNoiseLabels)
        self.PSDWorkerInstance.finished.connect(self.closeProgressBar)
        self.PSDWorkerInstance.progress.connect(self.updateProgressBar)
        self.PSDThread.started.connect(self.PSDWorkerInstance.calculatePSD)

        self.processRawDataThread = QtCore.QThread()
        self.processRawDataWorkerInstance = workerobjects.ProcessRawDataWorker(self, 0) # TODO
        self.processRawDataWorkerInstance.moveToThread(self.processRawDataThread)
        self.processRawDataWorkerInstance.finished.connect(self.processRawDataThread.quit)
        self.processRawDataWorkerInstance.dataReady.connect(self.displayData)
        self.processRawDataWorkerInstance.startPSDThread.connect(self.PSDThread.start)
        self.processRawDataWorkerInstance.progress.connect(self.updateProgressBar)
        self.processRawDataThread.started.connect(self.processRawDataWorkerInstance.processRawData)

        self.analyzeDataThread = QtCore.QThread()
        self.analyzeDataWorkerInstance = workerobjects.AnalyzeDataWorker(self)
        self.analyzeDataWorkerInstance.moveToThread(self.analyzeDataThread)
        self.analyzeDataWorkerInstance.finished.connect(self.analyzeDataThread.quit)
        self.analyzeDataWorkerInstance.finished.connect(self.displayAnalysis)
        self.analyzeDataWorkerInstance.finished.connect(self.closeProgressBar)
        # self.analyzeDataWorkerInstance.finished.connect(self.tempFunction)
        self.analyzeDataWorkerInstance.edgeDetectionFinished.connect(lambda: self.showProgressBar(self.numberOfEvents))
        self.analyzeDataWorkerInstance.progress.connect(self.updateProgressBar)
        self.analyzeDataThread.started.connect(self.analyzeDataWorkerInstance.analyzeData)

    # def tempFunction(self):
    #     if (self.ui.checkBox_enableIonChannelMode.isChecked() is True):
    #         self.csvFileName = self.currentHexFileName[:-4] + "_" + str(int(self.livePreviewFilterBandwidth/1000)) + ".csv"
    #         with open(self.csvFileName, 'w') as f:
    #             print self.csvFileName
    #             for i in range(len(self.edgeBegin)):
    #                 f.write(str(self.edgeBegin[i] / self.analyzeDataWorkerInstance.effectiveSamplingRate) + "," +
    #                         str(self.edgeEnd[i] / self.analyzeDataWorkerInstance.effectiveSamplingRate) + "," +
    #                         str((self.edgeEnd[i]-self.edgeBegin[i])/self.analyzeDataWorkerInstance.effectiveSamplingRate) + "\n")

    def closeEvent(self, event):
        """Close out the corresponding options dialog if open, before closing self"""
        try:
            self.optionsWindow0.close()
        except:
            pass
        self.PSDThread.quit()
        self.PSDThread.wait()
        self.processRawDataThread.quit()
        self.processRawDataThread.wait()
        self.analyzeDataThread.quit()
        self.analyzeDataThread.wait()
        event.accept()

    def comboBox_columnSelect_activated(self, index):
        """Sets the column selection for the chip. Clears out data about the DC offset current when a column switch is initiated"""
        self.columnSelect = index
        self.processRawDataWorkerInstance.validColumn = self.columnSelect
        self.PSDWorkerInstance.validColumn = self.columnSelect
        if self.dataInMemory == 1:
            self.showProgressBar(10)
            self.updateProgressBar(0, 'Reading file')
            self.processRawDataThread.start()

    def lineEdit_livePreviewFilterBandwidth_editingFinished(self):
        """Reads in the filter bandwidth that the live preview is eventually filtered down to and creates the appropriate filter in the processRawData worker"""
        try:
            self.livePreviewFilterBandwidth = eval(str(self.ui.lineEdit_livePreviewFilterBandwidth.text()))*1e3
        except:
            self.livePreviewFilterBandwidth = 100e3
        if (self.livePreviewFilterBandwidth > 10e6):
            self.livePreviewFilterBandwidth = 10e6
        self.ui.lineEdit_livePreviewFilterBandwidth.setText(str(int(self.livePreviewFilterBandwidth/1e3)))
        self.processRawDataWorkerInstance.createFilter(self.livePreviewFilterBandwidth)
        if self.dataInMemory == 1:
            self.processRawDataThread.start()

    def action_loadData_triggered(self):
        """Loads a previously saved hex file for viewing. Also searches for a similarly named cfg file to load in the experimental parameters"""
        fileSelecter = QtGui.QFileDialog()
        self.dataLoadFileSelected = fileSelecter.getOpenFileName(self, "Choose file", "./", filter="Hex files (*.hex)", selectedFilter="*.hex")
        if self.dataLoadFileSelected != '':
            self.currentHexFileName = str(self.dataLoadFileSelected.split('/')[-1])
            self.currentDirectoryName = str(self.dataLoadFileSelected[:-len(self.currentHexFileName)])
            self.ui.action_deleteFile.setEnabled(True)
            hexFileList = [os.path.split(x)[1] for x in glob.glob(self.currentDirectoryName + '*.hex')]
            currentHexFileIndex = hexFileList.index(self.currentHexFileName)
            print currentHexFileIndex
            if (currentHexFileIndex != 0):
                self.ui.action_previousFile.setEnabled(True)
            else:
                self.ui.action_previousFile.setEnabled(False)
            if (currentHexFileIndex != len(hexFileList)-1):
                self.ui.action_nextFile.setEnabled(True)
            else:
                self.ui.action_nextFile.setEnabled(False)
            self.loadHexData()

    def loadHexData(self):
        self.dataInMemory = 0
        print self.dataLoadFileSelected
        if self.dataLoadFileSelected != "":
            configLoadFileSelected = self.dataLoadFileSelected[0:len(self.dataLoadFileSelected) - 3] + "cfg"
            try:
                self.f = open(configLoadFileSelected, 'r')
                stateConfig = json.load(self.f)
                self.loadState(stateConfig)
                self.f.close()
            except:
                print "Could not find a corresponding cfg file"
            self.f = open(self.dataLoadFileSelected, 'rb')
            self.processRawDataWorkerInstance.rawData = self.f.read()
            # self.processRawDataWorkerInstance.rawData = self.processRawDataWorkerInstance.rawData[0:len(self.processRawDataWorkerInstance.rawData)/10]
            print len(self.processRawDataWorkerInstance.rawData)
            windowTitle = self.dataLoadFileSelected.split('/')[-2] + '/' + self.dataLoadFileSelected.split('/')[-1]
            self.setWindowTitle(windowTitle)
            # self.processRawDataWorkerInstance.rawData = self.processRawDataWorkerInstance.rawData[:-1]
            self.f.close()
            self.dataInMemory = 1
            self.baseline = None
            # with open(self.dataLoadFileSelected, 'rb') as self.f:
                # for line in self.f:
                    # self.rawData = line
            if (self.processRawDataThread.isRunning()):
                self.processRawDataThread.quit()
                self.processRawDataThread.wait()
                print "It's still running"
            if self.currentDirectoryName[-11:-1] == 'compressed':
                self.showProgressBar(8)
                self.processRawDataWorkerInstance.compressedData = True
            else:
                self.showProgressBar(10)
                self.processRawDataWorkerInstance.compressedData = False
            self.processRawDataThread.start()
            # self.unpackData(self.ui.comboBox_columnSelect.currentIndex())
        else:
            pass

    def action_nextFile_triggered(self):
        hexFileList = [os.path.split(x)[1] for x in glob.glob(self.currentDirectoryName + '*.hex')]
        currentHexFileIndex = hexFileList.index(self.currentHexFileName)
        nextHexFileIndex = currentHexFileIndex + 1
        if nextHexFileIndex == len(hexFileList) - 1:
            self.ui.action_nextFile.setEnabled(False)
        if nextHexFileIndex != 0:
            self.ui.action_previousFile.setEnabled(True)
        nextHexFileName = hexFileList[nextHexFileIndex]
        self.loadHexData(self.currentDirectoryName + nextHexFileName)
        self.currentHexFileName = nextHexFileName

    def action_previousFile_triggered(self):
        hexFileList = [os.path.split(x)[1] for x in glob.glob(self.currentDirectoryName + '*.hex')]
        currentHexFileIndex = hexFileList.index(self.currentHexFileName)
        previousHexFileIndex = currentHexFileIndex - 1
        if previousHexFileIndex == 0:
            self.ui.action_previousFile.setEnabled(False)
        if previousHexFileIndex != len(hexFileList) - 1:
            self.ui.action_nextFile.setEnabled(True)
        previousHexFileName = hexFileList[previousHexFileIndex]
        print self.currentDirectoryName + previousHexFileName
        self.loadHexData(self.currentDirectoryName + previousHexFileName)
        self.currentHexFileName = previousHexFileName

    def action_deleteFile_triggered(self):
        deleteMessage = 'Are you sure you want to delete ' + self.currentHexFileName + ' ?'
        response = QtGui.QMessageBox.question(self, 'Confirm deletion', deleteMessage, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if response == QtGui.QMessageBox.Yes:
            hexFileList = [os.path.split(x)[1] for x in glob.glob(self.currentDirectoryName + '*.hex')]
            currentHexFileIndex = hexFileList.index(self.currentHexFileName)
            os.remove(self.currentDirectoryName + self.currentHexFileName)
            currentCfgFileName = self.currentHexFileName[:-3] + "cfg"
            try:
                os.remove(self.currentDirectoryName + currentCfgFileName)
            except:
                pass
            if len(hexFileList) == 1:
                pass
            elif currentHexFileIndex == len(hexFileList) - 1:
                self.currentHexFileName = hexFileList[currentHexFileIndex - 1]
                self.loadHexData(self.currentDirectoryName + hexFileList[currentHexFileIndex - 1])
            else:
                self.currentHexFileName = hexFileList[currentHexFileIndex + 1]
                self.loadHexData(self.currentDirectoryName + hexFileList[currentHexFileIndex + 1])
            print "Deleted " + self.currentHexFileName
        else:
            pass

    def updateDisplayData(self):
        self.displayData(self.columnSelect)

    def displayData(self, column):
        """This method plots self.dataToDisplay from the worker thread that loads data from the file and processes it. The data being displayed is already a subsampled version of the full data. PyQtGraph then displays the data in the GUI."""
        self.start = time.clock()
        if (True):
            if (0 == self.ui.tabWidget_plot.currentIndex()):
                self.ui.graphicsView_time_plot.setData(self.adcList[column].xDataToDisplay, self.adcList[column].yDataToDisplay)
                if (self.ui.action_addVerticalMarker.isChecked() == True):
                    self.graphicsView_time_updateMarkerText()
            elif (1 == self.ui.tabWidget_plot.currentIndex() and 0 not in self.adcList[column].psd):
                self.ui.graphicsView_frequency_plot.setData(self.adcList[column].f, self.adcList[column].psd)
                if (self.ui.action_addVerticalMarker.isChecked() == True):
                    self.graphicsView_frequency_updateMarkerText()
                if (self.ui.action_addNoiseFit.isChecked() == True and hasattr(self.adcList[column], 'psdFit')):
                    self.ui.graphicsView_frequencyFit_plot.setData(self.adcList[column].f, self.adcList[column].psdFit)
            elif (2 == self.ui.tabWidget_plot.currentIndex()):
                if (hasattr(self, 'dwellTime')):
                    if (self.histogramModeSelect == 0):
                        self.ui.graphicsView_histogram_plot.setData(numpy.sum(self.dwellTime, axis=1), self.meanDeltaI, pen=None, symbol='o', symbolBrush='k', symbolSize=7)
                        if (hasattr(self, 'eventFitColor') and self.ui.checkBox_enableCUSUM.isChecked()):
                            self.ui.graphicsView_histogram_plot.setSymbolBrush(self.eventFitColor)
                        self.ui.graphicsView_histogram.setLabel(axis='bottom', text='Dwell Time', units='s')
                        self.ui.graphicsView_histogram.setLabel(axis='left', text='I', units='A')
                    elif (self.histogramModeSelect == 1):
                        self.adcList[column].histogramView, self.adcList[column].bins = numpy.histogram(numpy.hstack(self.eventValue), bins=200)
                        self.ui.graphicsView_histogram_plot.setData(self.adcList[column].histogramView, self.adcList[column].bins[0:len(self.adcList[column].bins)-1] + (self.adcList[column].bins[1]-self.adcList[column].bins[0])/2, pen='b', symbol=None)
                        self.ui.graphicsView_histogram.setLabel(axis='bottom', text='Count', units='')
                        self.ui.graphicsView_histogram.setLabel(axis='left', text='I', units='A')
                        # self.ui.graphicsView_histogram_plot.setData(self.bins, self.histogramView, stepMode=True, pen='b', symbol=None)
                elif (hasattr(self, 'histogramView')):
                    self.ui.graphicsView_histogram_plot.setData(self.adcList[column].histogramView, self.adcList[column].bins[0:len(self.adcList[column].bins)-1] + (self.adcList[column].bins[1]-self.adcList[column].bins[0])/2)
                    self.ui.graphicsView_histogram.setLabel(axis='bottom', text='Count', units='')
                    self.ui.graphicsView_histogram.setLabel(axis='left', text='I', units='A')
                else:
                    self.ui.graphicsView_histogram_plot.setData(numpy.linspace(0, 1, 100), numpy.ones(100), pen='b')
            elif (3 == self.ui.tabWidget_plot.currentIndex()):
                indexValuesToPlot = numpy.arange(self.eventIndex[self.currentEvent-1][0]-100, self.eventIndex[self.currentEvent-1][-1] + 101).astype(int)
                self.ui.graphicsView_eventViewer_plot.setData(indexValuesToPlot.astype(numpy.float)/self.analyzeDataWorkerInstance.effectiveSamplingRate, self.analyzeDataWorkerInstance.rawData[indexValuesToPlot])
                if (self.ui.checkBox_enableCUSUM.isChecked()):
                    self.ui.graphicsView_eventViewer_plotFit.setData(indexValuesToPlot[100:-101].astype(numpy.float)/self.analyzeDataWorkerInstance.effectiveSamplingRate, numpy.hstack(self.meanEventValue[self.currentEvent-1]), pen='k', width=2)
                    self.ui.graphicsView_eventViewer_plotFit.setPen(self.eventFitColor[self.currentEvent-1])
                # self.ui.graphicsView_eventViewer_plotFit.setData(indexValuesToPlot[500:1000].astype(numpy.float)/globalConstants.ADCSAMPLINGRATE, numpy.hstack(self.meanEventValue[self.currentEvent-1]), pen='k', width=2)
            self.stop = time.clock()
            # print "Main GUI thread took", self.stop-self.start, "s"

    def action_options_triggered(self):
        """Creates an options window"""
        self.optionsWindow0 = OptionsWindow()
        self.optionsWindow0.show()
        self.optionsWindow0.accepted.connect(self.displayData)

    def loadState(self, stateConfig):
        """This method handles the actual loading of the cfg file"""
        for i in xrange(len(stateConfig)):
            columnSelect = stateConfig[i].pop('columnSelect', None)
            rowSelect = stateConfig[i].pop('rowSelect', None)
            RDCFB = stateConfig[i].pop('RDCFB', None)

            if (None != columnSelect):
                self.columnSelect = columnSelect
            if (None != rowSelect):
                self.rowSelect = rowSelect
            if (None != RDCFB):
                self.RDCFB = RDCFB
                self.ui.lineEdit_RDCFB.setText(str(round(RDCFB/1e6, 1)))

            # Load column and row information first for indexing the rest
            column = stateConfig[i].pop('column', columnSelect) # default to columnSelect for backwards compatability
            row = stateConfig[i].pop('row', rowSelect) # default to rowSelect for backwards compatability
            # If the global configuration stateConfig entry is not present the single channel data will be loaded.
            # Otherwise, the columnSelect and rowSelect will be used but eventually overwritten.
            # Works for now

            if ((None != column) and (None != row)):
                self.adcList[column].amplifierList[row].biasEnable = stateConfig[i].pop('biasEnable', 0)
                self.adcList[column].amplifierList[row].connectElectrode = stateConfig[i].pop('connectElectrode', 0)
                self.adcList[column].amplifierList[row].gainIndex = stateConfig[i].pop('amplifierGainSelect', 0)
                self.adcList[column].amplifierList[row].resetIntegrator = stateConfig[i].pop('integratorReset', 0)
                self.adcList[column].amplifierList[row].connectISRCEXT = stateConfig[i].pop('connectISRCEXT', 0)
                self.adcList[column].amplifierList[row].enableSWCapClock = stateConfig[i].pop('enableSWCapClock', 0)
                self.adcList[column].amplifierList[row].enableTriangleWave = stateConfig[i].pop('enableTriangleWave', 0)
                self.adcList[column].idcOffset = stateConfig[i].pop('IDCOffset', 0) # TODO This is being overwritten over and over again but until we implement all 25 channels
                self.ui.comboBox_columnSelect.setCurrentIndex(self.columnSelect)
                self.updateIDCLabels()

    def updateIDCOffset(self, value):
        """Method created to facilitate loading in the DC offset current value in the dictionary style loading"""
        self.IDCOffset = value
        self.updateIDCLabels()

    def pushButton_IDCSetOffset_clicked(self):
        """Updates the DC offset current value so that the current being viewed has no DC component left in it"""
        self.adcList[self.columnSelect].idcOffset += self.adcList[self.columnSelect].idcRelative
        self.ui.label_IDCOffset.setText(str(self.adcList[self.columnSelect].idcOffset * 1e9))

    def updateIDCLabels(self):
        """Update labels on the GUI indicating the DC offset current, DC relative current and DC net current"""
        self.ui.label_IDCOffset.setText(str(round(self.adcList[self.columnSelect].idcOffset * 1e9, 1)))
        self.ui.label_IDCRelative.setText(str(round(self.adcList[self.columnSelect].idcRelative * 1e9, 1)))
        self.ui.label_IDCNet.setText(str(round((self.adcList[self.columnSelect].idcOffset + self.adcList[self.columnSelect].idcRelative) * 1e9, 1)))

    def updateNoiseLabels(self):
        """Update labels on the GUI indicating the integrated noise values at 100 kHz, 1 MHz and 10 MHz bandwidths"""
        self.ui.label_100kHzNoise.setText(str(self.adcList[self.columnSelect].rmsNoise_100kHz))
        self.ui.label_1MHzNoise.setText(str(self.adcList[self.columnSelect].rmsNoise_1MHz))
        self.ui.label_10MHzNoise.setText(str(self.adcList[self.columnSelect].rmsNoise_10MHz))

    def showProgressBar(self, maximum=10):
        """Creates a progress bar"""
        self.progressBar = ProgressBarWindow(maximum)
        self.progressBar.show()

    def updateProgressBar(self, value=0, text=''):
        """Updates the progress bar"""
        self.progressBar.updateValue(value, text)

    def closeProgressBar(self):
        """Closes the progress bar once it finishes"""
        self.progressBar.close()

    def lineEdit_RDCFB_editingFinished(self):
        """Reads in the new value of RDCFB from the GUI once it has been edited"""
        oldRDCFB = self.RDCFB
        try:
            self.RDCFB = eval(str(self.ui.lineEdit_RDCFB.text()))*1e6
            if self.RDCFB == 0:
                self.RDCFB = oldRDCFB
        except:
            self.RDCFB = 50*1e6
        self.ui.lineEdit_RDCFB.setText(str(round(self.RDCFB/1e6, 1)))
        self.adcList[self.columnSelect].rmsNoise_100kHz = numpy.round(self.adcList[self.columnSelect].rmsNoise_100kHz*oldRDCFB/self.RDCFB, 1)
        self.adcList[self.columnSelect].rmsNoise_1MHz = numpy.round(self.adcList[self.columnSelect].rmsNoise_1MHz*oldRDCFB/self.RDCFB, 1)
        self.adcList[self.columnSelect].rmsNoise_10MHz = numpy.round(self.adcList[self.columnSelect].rmsNoise_10MHz*oldRDCFB/self.RDCFB, 1)
        self.updateNoiseLabels()

    def action_capturePlot_triggered(self):
        """Saves the currently displayed plot data as a CSV and a PNG file"""
        if (0 == self.ui.tabWidget_plot.currentIndex()):
            self.itemToExport = self.ui.graphicsView_time
            self.ui.graphicsView_time_plot.setDownsampling(False)
            self.ui.graphicsView_time.setClipToView(False)
        elif (1 == self.ui.tabWidget_plot.currentIndex()):
            self.itemToExport = self.ui.graphicsView_frequency
        elif (3 == self.ui.tabWidget_plot.currentIndex()):
            self.action_exportAllEventsAsCSV_triggered()
            return False
        else:
            self.itemToExport = self.ui.graphicsView_frequency
        self.CSVExporter = pyqtgraph.exporters.CSVExporter(self.itemToExport.getPlotItem())
        self.PNGExporter = pyqtgraph.exporters.ImageExporter(self.itemToExport.getPlotItem())
        self.PNGExporter.parameters()['width'] = 2000
        fileSelecter = QtGui.QFileDialog()
        CSVSaveFileSelected = str(fileSelecter.getSaveFileName(self, "Choose file", "./", filter="CSV files (*.csv)", selectedFilter="*.csv"))
        PNGSaveFileSelected = CSVSaveFileSelected[:-3] + 'png'
        # print PNGSaveFileSelected
        if (CSVSaveFileSelected is not ''):
            self.CSVExporter.export(CSVSaveFileSelected)
            self.PNGExporter.export(PNGSaveFileSelected)
        else:
            return False
        self.ui.graphicsView_time.setClipToView(True) # Setting clipToView after downsampling significantly degrades performance
        self.ui.graphicsView_time_plot.setDownsampling(auto=True, method='peak') # Only downsample the time plot instead of the entire viewbox
        print "Saving CSV and PNG files!"

    def action_addVerticalMarker_triggered(self):
        """Adds a vertical marker to both the time and frequency views.
           In the time view, labels at the top right of the plot indicate the amplitude and time value at the marker.
           In the frequency view, labels at the top right of the plot indicate the integrated noise and frequency value at the marker"""
        if (self.ui.action_addVerticalMarker.isChecked()):
            self.ui.graphicsView_time.marker = pyqtgraph.InfiniteLine(0, angle=90, movable=True, pen='g')
            self.ui.graphicsView_time.marker.x = 0
            self.ui.graphicsView_time.marker.sigPositionChanged.connect(self.graphicsView_time_updateMarkerText)
            self.ui.graphicsView_time.markerValue = pyqtgraph.TextItem('X=0\nY=0', anchor = (1,0), color='g')
            self.ui.graphicsView_time.markerValue.setPos(len(self.adcList[self.columnSelect].yDataToDisplay)*globalConstants.SUBSAMPLINGFACTOR*1.0/globalConstants.ADCSAMPLINGRATE, numpy.max(self.adcList[self.columnSelect].yDataToDisplay))
            self.ui.graphicsView_time.addItem(self.ui.graphicsView_time.marker)
            self.ui.graphicsView_time.addItem(self.ui.graphicsView_time.markerValue)

            self.ui.graphicsView_frequency.marker = pyqtgraph.InfiniteLine(3, angle=90, movable=True, pen='g')
            self.ui.graphicsView_frequency.marker.x = 3
            self.ui.graphicsView_frequency.marker.sigPositionChanged.connect(self.graphicsView_frequency_updateMarkerText)
            self.ui.graphicsView_frequency.markerValue = pyqtgraph.TextItem('X=100\nY=0', anchor = (1,0), color='g')
            self.ui.graphicsView_frequency.markerValue.setPos(numpy.max(self.adcList[self.columnSelect].f), numpy.max(self.adcList[self.columnSelect].psd))
            self.ui.graphicsView_frequency.addItem(self.ui.graphicsView_frequency.marker)
            self.ui.graphicsView_frequency.addItem(self.ui.graphicsView_frequency.markerValue)
        else:
            self.ui.graphicsView_time.removeItem(self.ui.graphicsView_time.marker)
            self.ui.graphicsView_time.removeItem(self.ui.graphicsView_time.markerValue)
            self.ui.graphicsView_frequency.removeItem(self.ui.graphicsView_frequency.marker)
            self.ui.graphicsView_frequency.removeItem(self.ui.graphicsView_frequency.markerValue)

    def graphicsView_time_updateMarkerText(self):
        """Updates the labels at the top right of the plot whenever the marker is moved in the time view"""
        self.ui.graphicsView_time.marker.x = float(self.ui.graphicsView_time.marker.value())
        try:
            self.ui.graphicsView_time.marker.y = self.adcList[self.columnSelect].yDataToDisplay[int(self.ui.graphicsView_time.marker.x/globalConstants.SUBSAMPLINGFACTOR*globalConstants.ADCSAMPLINGRATE)]
        except:
            self.ui.graphicsView_time.marker.y = 0
        self.ui.graphicsView_time.markerValue.setPlainText('X=' + '%.3E s' % self.ui.graphicsView_time.marker.x + '\nY=%.3E A' % self.ui.graphicsView_time.marker.y)
        self.ui.graphicsView_time.markerValue.setPos(self.ui.graphicsView_time.getViewBox().viewRange()[0][1], self.ui.graphicsView_time.getViewBox().viewRange()[1][1])
        # print self.ui.graphicsView_time.marker.value()

    def graphicsView_frequency_updateMarkerText(self):
        """Updates the labels at the top right of the plot whenever the marker is moved in the frequency view"""
        self.ui.graphicsView_frequency.marker.x = 10**float(self.ui.graphicsView_frequency.marker.value())
        try:
            self.ui.graphicsView_frequency.marker.y = self.adcList[self.columnSelect].rmsNoise[numpy.abs(self.adcList[self.columnSelect].f-self.ui.graphicsView_frequency.marker.x).argmin()]
        except:
            self.ui.graphicsView_frequency.marker.y = 0
        self.ui.graphicsView_frequency.markerValue.setPlainText('X=' + '%.3E Hz' % self.ui.graphicsView_frequency.marker.x + u'\n√(∫Y∆X)=%.3E Arms' % self.ui.graphicsView_frequency.marker.y)
        self.ui.graphicsView_frequency.markerValue.setPos(self.ui.graphicsView_frequency.getViewBox().viewRange()[0][1], self.ui.graphicsView_frequency.getViewBox().viewRange()[1][1])
        # print self.ui.graphicsView_time.marker.value()

    def action_addNoiseFit_triggered(self):
        """Adds a fit to the noise PSD. The data is fit to a*f^-1 + b + c*f + d*f^2"""
        if (self.ui.action_addNoiseFit.isChecked() == True):
            self.ui.graphicsView_frequencyFit_plot = self.ui.graphicsView_frequency.plot(numpy.linspace(100, 10e6, 100), numpy.ones(100), pen='k', width=4)
            if (self.dataInMemory == 1):
                self.adcList[self.columnSelect].psdFit = self.PSDWorkerInstance.createFit(self.adcList[self.columnSelect].f, self.adcList[self.columnSelect].psd, 5e6)
                self.displayData(self.columnSelect)
        else:
            self.ui.graphicsView_frequency.removeItem(self.ui.graphicsView_frequencyFit_plot)

    def pushButton_analyzeData_clicked(self):
        """Starts the analyzeData thread. Also enables the event viewer tab and the widgets necessary for interacting with it"""
        self.analyzeDataThread.start()
        self.ui.tabWidget_plot.setTabEnabled(3, True)
        self.ui.lineEdit_currentEvent.setEnabled(True)
        self.ui.lineEdit_totalEvents.setEnabled(True)
        self.ui.lineEdit_totalEvents.setReadOnly(True) #Need to set readOnly again after enabling the widget to disable interaction
        self.ui.pushButton_previousEvent.setEnabled(True)
        self.ui.pushButton_nextEvent.setEnabled(True)
        self.ui.action_exportAllEventsAsCSV.setEnabled(True)

    def displayAnalysis(self):
        """Removes results of previous analysis and displays the new results on top of them. This includes creating a new baseline, a threshold line and event begin and end markers for all the detected events."""
        if (hasattr(self.ui.graphicsView_time, 'baseline')):
            self.ui.graphicsView_time.removeItem(self.ui.graphicsView_time.baseline)
        if (hasattr(self.ui.graphicsView_time, 'threshold')):
            self.ui.graphicsView_time.removeItem(self.ui.graphicsView_time.threshold)
        if (hasattr(self.ui.graphicsView_time, 'eventBeginMarker')):
            self.ui.graphicsView_time.removeItem(self.ui.graphicsView_time.eventBeginMarker)
        if (hasattr(self.ui.graphicsView_time, 'eventEndMarker')):
            self.ui.graphicsView_time.removeItem(self.ui.graphicsView_time.eventEndMarker)

        # plot = pyqtgraph.plot(self.analyzeF, self.analyzePxx, pen='b')
        # plot.setLogMode(True, True)

        self.ui.graphicsView_time.baseline = pyqtgraph.InfiniteLine(self.baseline, angle = 0, pen='g', movable = self.ui.checkBox_enableIonChannelMode.isChecked())
        self.ui.graphicsView_time.baseline.sigPositionChanged.connect(self.graphicsView_time_updateBaseline)
        self.ui.graphicsView_time.threshold = pyqtgraph.InfiniteLine(self.threshold, angle = 0, pen='r', movable=True)
        self.ui.graphicsView_time.threshold.sigPositionChanged.connect(self.graphicsView_time_updateThreshold)
        self.ui.graphicsView_time.addItem(self.ui.graphicsView_time.baseline)
        self.ui.graphicsView_time.addItem(self.ui.graphicsView_time.threshold)

        self.ui.graphicsView_time.eventBeginMarker = self.ui.graphicsView_time.plot(self.edgeBegin.astype(numpy.float)/self.analyzeDataWorkerInstance.effectiveSamplingRate, self.analyzeDataWorkerInstance.rawData[self.edgeBegin], pen=None, symbol='o', symbolBrush='g', symbolSize=7, autoDownsample=False, downsample=1)
        self.ui.graphicsView_time.eventBeginMarker.setClipToView(False) # Disable clipToView so that points don't disappear when zooming and panning
        self.ui.graphicsView_time.eventEndMarker = self.ui.graphicsView_time.plot(self.edgeEnd.astype(numpy.float)/self.analyzeDataWorkerInstance.effectiveSamplingRate, self.analyzeDataWorkerInstance.rawData[self.edgeEnd], pen=None, symbol='o', symbolBrush='r', symbolSize=7, autoDownsample=False, downsample=1)
        self.ui.graphicsView_time.eventEndMarker.setClipToView(False) # Disable clipToView so that points don't disappear when zooming and panning

        # self.ui.graphicsView_histogram_plot.clear()
        # self.ui.graphicsView_histogram.dwellTime = self.ui.graphicsView_histogram.plot(self.dwellTime, self.meanDeltaI, pen=None, symbol='o', symbolBrush='k', symbolSize=7)
        # self.ui.graphicsView_histogram.dwellTime.sigPointsClicked.connect(self.dwellTime_sigPointsClicked)
        self.ui.graphicsView_histogram_plot.setData(numpy.sum(self.dwellTime, axis=1), self.meanDeltaI, pen=None, symbol='o', symbolBrush='k', symbolSize=7)
        if (hasattr(self, 'eventFitColor') and self.ui.checkBox_enableCUSUM.isChecked()):
            self.ui.graphicsView_histogram_plot.setSymbolBrush(self.eventFitColor)
        self.ui.graphicsView_histogram_plot.sigPointsClicked.connect(self.dwellTime_sigPointsClicked)
        # self.temp = pyqtgraph.plot()
        # self.tempPlot = self.temp.plot(self.analyzeDataWorkerInstance.popt, pen=None, symbol='o')
        # self.tempPlot.sigPointsClicked.connect(self.tempPlot_sigPointsClicked)

        self.ui.lineEdit_totalEvents.setText(str(self.numberOfEvents))
        print self.numberOfEvents
        self.graphicsView_eventViewer_eventChanged(absolute=1)

    # def tempPlot_sigPointsClicked(self, item, points):
        # self.analyzeDataWorkerInstance.popt = numpy.delete(self.analyzeDataWorkerInstance.popt, points[0].pos()[0])
        # print numpy.mean(self.analyzeDataWorkerInstance.popt), numpy.std(self.analyzeDataWorkerInstance.popt)
        # self.displayAnalysis()

    def graphicsView_time_updateBaseline(self):
        """Updates the baseline once the user moves the baseline line"""
        self.baseline = float(self.ui.graphicsView_time.baseline.value())

    def graphicsView_time_updateThreshold(self):
        """Updates the threshold once the user moves the threshold line"""
        self.threshold = float(self.ui.graphicsView_time.threshold.value())
        if (self.ui.comboBox_thresholdUnitsSelect.currentIndex() == 0):
            self.ui.lineEdit_threshold.setText(str(round((self.baseline-self.threshold)/self.sigma, 2)))
        elif (self.ui.comboBox_thresholdUnitsSelect.currentIndex() == 1):
            self.ui.lineEdit_threshold.setText(str(round((self.baseline-self.threshold)*1e9, 2)))

    def graphicsView_eventViewer_eventChanged(self, relative=0, absolute=0):
        """Change the currently displayed event"""
        try:
            self.currentEvent = int(self.ui.lineEdit_currentEvent.text())
        except:
            self.currentEvent = 1
        if relative != 0:
            self.currentEvent = numpy.clip(self.currentEvent + relative, 1, self.numberOfEvents)
        elif absolute != 0:
            self.currentEvent = numpy.clip(absolute, 1, self.numberOfEvents)
        self.ui.lineEdit_currentEvent.setText(str(self.currentEvent))
        # Update event viewer tab
        if (3 == self.ui.tabWidget_plot.currentIndex()):
            self.displayData(self.columnSelect)

    def dwellTime_sigPointsClicked(self, item, points):
        """Looks up the point that was clicked in the dwell time histogram and opens it up in the event viewer tab"""
        eventSelectedIndex = numpy.where(self.meanDeltaI == points[0].pos()[1])[0]
        self.ui.tabWidget_plot.setCurrentIndex(3) # Switch to event viewer tab
        self.graphicsView_eventViewer_eventChanged(absolute = int(eventSelectedIndex + 1))

    def comboBox_histogramModeSelect_activated(self, index):
        """Changes the type of histogram showed - current blockage vs dwell time or current blockage vs count"""
        self.histogramModeSelect = index
        if (2 == self.ui.tabWidget_plot.currentIndex()):
            self.displayData(self.columnSelect)

    def comboBox_thresholdUnitsSelect_activated(self, index):
        self.thresholdType = index
        if (self.thresholdType == 0):
            if (hasattr(self.ui.graphicsView_time, 'threshold')):
                self.ui.lineEdit_threshold.setText(str(round((self.baseline - self.threshold)/self.sigma, 1)))
        elif (self.thresholdType == 1):
            if (hasattr(self.ui.graphicsView_time, 'threshold')):
                self.ui.lineEdit_threshold.setText(str(round((self.baseline - self.threshold)*1e9, 2)))

    def lineEdit_threshold_editingFinished(self):
        if (self.thresholdType == 0):
            self.numberOfSigmas = float(self.ui.lineEdit_threshold.text())
            if (hasattr(self, 'sigma') and hasattr(self, 'baseline')):
                self.threshold = self.baseline - self.sigma * self.numberOfSigmas
        elif (self.thresholdType == 1):
            if (hasattr(self, 'baseline')):
                self.threshold = self.baseline - float(self.ui.lineEdit_threshold.text())*1e-9
            else:
                self.threshold = float(self.ui.lineEdit_threshold.text())*1e-9

    def action_exportAllEventsAsCSV_triggered(self):
        currentCSVFileName = self.currentHexFileName[:-4]
        if self.livePreviewFilterBandwidth >= 1e6:
            livePreviewFilterBandwidth = str(round(self.livePreviewFilterBandwidth/1e6, 2)) + 'MHz'
        else:
            livePreviewFilterBandwidth = str(round(self.livePreviewFilterBandwidth/1e3, 2)) + 'kHz'
        currentCSVFileName += '_' + livePreviewFilterBandwidth
        if (self.ui.comboBox_thresholdUnitsSelect.currentIndex() == 0):
            threshold = str(self.ui.lineEdit_threshold.text()) + 'sigma'
        elif (self.ui.comboBox_thresholdUnitsSelect.currentIndex() == 1):
            threshold = str(self.ui.lineEdit_threshold.text()) + 'nA'
        currentCSVFileName += '_' + threshold + '.csv'
        with open(self.currentDirectoryName + currentCSVFileName, 'w') as f:
            for i in range(numpy.shape(self.eventIndex)[0]):
                f.write('# Event started at %f s\n' %((self.eventIndex[i][0] - 100.)/self.analyzeDataWorkerInstance.effectiveSamplingRate))
                for j in numpy.arange(self.eventIndex[i][0]-100, self.eventIndex[i][-1]+101):
                    # t = (j - self.eventIndex[i][0] + 100.)/self.analyzeDataWorkerInstance.effectiveSamplingRate
                    t = j*1./self.analyzeDataWorkerInstance.effectiveSamplingRate
                    f.write(str(t) + ',' + str(self.analyzeDataWorkerInstance.rawData[j]) + '\n')
