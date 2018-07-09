# -*- coding: utf-8 -*-
import os
from PyQt4 import QtCore, QtGui
from FPGA import FPGA
from cnp2_gui import Ui_MainWindow
from optionswindow import OptionsWindow
from compressdata import CompressData
import numpy
import time
import struct
import json
import pyqtgraph, pyqtgraph.exporters
from loadolddata import LoadOldDataWindow
import workerobjects

# pyqtgraph.setConfigOptions(useWeave = False) #To remove gcc related error
pyqtgraph.setConfigOption('background', 'w') #Set background to white
pyqtgraph.setConfigOption('foreground', 'k') #Set foreground to black

masterSerial = '1817000M4C'
slaveSerial = '1817000LYB'

ADCBITS = 12
SUBSAMPLINGFACTOR = 10
REFRESHRATE = 10 # in frames per second
AAFILTERGAIN = (51+620)/620.0*1.8*.51
ADCSAMPLINGRATE = 4000000
FRAMEDURATION = 1000/REFRESHRATE
FRAMELENGTH_MASTER = int((((ADCSAMPLINGRATE*FRAMEDURATION/1000)*4)/4000000. + 0)*4000000) # Multiplied by 4 because of the specific FPGA data packing implementation
FRAMELENGTH_SLAVE = (int((ADCSAMPLINGRATE*FRAMEDURATION/1000)*4*4.0/3)/4000000 + 1)*4000000 #Slave data is packed with 3/4 efficiency
# BLOCKLENGTH = 1024
BLOCKLENGTH = 256 # While transferring data from the FPGA, the transaction is broken up into blocks of this length (in bytes)
MBCOMMONMODE = 1.65 # Nominal common mode voltage for the motherboard is 1.65 V
PRESETMODE = 1
SQUAREWAVEAMPLITUDE = 0.9
IVSTARTVOLTAGE = -0.5
IVSTOPVOLTAGE = 0.5
IVVOLTAGESTEP = 100
IVTIMESTEP = 500
IVNUMBEROFCYCLES = 0

dictOfConstants = {'ADCBITS':ADCBITS, 'SUBSAMPLINGFACTOR': SUBSAMPLINGFACTOR, 'REFRESHRATE': REFRESHRATE, 'AAFILTERGAIN': AAFILTERGAIN, 'ADCSAMPLINGRATE': ADCSAMPLINGRATE, 'FRAMEDURATION': FRAMEDURATION, 'FRAMELENGTH_MASTER': FRAMELENGTH_MASTER, 'FRAMELENGTH_SLAVE': FRAMELENGTH_SLAVE, 'BLOCKLENGTH': BLOCKLENGTH, 'MBCOMMONMODE': MBCOMMONMODE, 'SQUAREWAVEAMPLITUDE': SQUAREWAVEAMPLITUDE, 'PRESETMODE': PRESETMODE, 'IVSTARTVOLTAGE': IVSTARTVOLTAGE, 'IVSTOPVOLTAGE': IVSTOPVOLTAGE, 'IVVOLTAGESTEP': IVVOLTAGESTEP, 'IVTIMESTEP': IVTIMESTEP, 'IVNUMBEROFCYCLES': IVNUMBEROFCYCLES}

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        """Initializes the main GUI window. Also contains mask and config settings for the different programmables on the 2 boards.
        This method sets up the UI as defined in cnp2_gui.py (which is generated using pyuic4 on a QTDesigner based UI)."""
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        bitmask0 = 0x00000001
        bitmask1 = 0x00000002
        bitmask2 = 0x00000004
        bitmask3 = 0x00000008
        bitmask4 = 0x00000010
        bitmask5 = 0x00000020
        bitmask6 = 0x00000040
        bitmask7 = 0x00000080
        bitmask8 = 0x00000100
        bitmask9 = 0x00000200
        bitmask10 = 0x00000400
        bitmask11 = 0x00000800
        bitmask12 = 0x00001000
        bitmask13 = 0x00002000
        bitmask14 = 0x00004000
        bitmask15 = 0x00008000
        bitmask16 = 0x00010000
        bitmask17 = 0x00020000
        bitmask18 = 0x00040000
        bitmask19 = 0x00080000
        bitmask20 = 0x00100000
        bitmask21 = 0x00200000
        bitmask22 = 0x00400000
        bitmask23 = 0x00800000
        bitmask24 = 0x01000000
        bitmask25 = 0x02000000
        bitmask26 = 0x04000000
        bitmask27 = 0x08000000
        bitmask28 = 0x10000000
        bitmask29 = 0x20000000
        bitmask30 = 0x40000000
        bitmask31 = 0x80000000

        #######################################################################
        # Mask and config options
        #######################################################################
        self.resetMask = bitmask0
        # self.ADC0ModeMask = bitmask1 + bitmask2 + bitmask3 + bitmask4 #Bits 1-4
        # self.ADC0ModeConfigOptions = {0: 0x00, 1: 0x02, 2: 0x04, 3: 0x08, 4: 0x10}
        # self.ADC1ModeMask = bitmask5 + bitmask6 + bitmask7 + bitmask8 #Bits 5-8
        # self.ADC1ModeConfigOptions = {0: 0x00, 1: 0x20, 2: 0x40, 3: 0x80, 4: 0x100}
        # self.ADC2ModeMask = bitmask1 + bitmask2 + bitmask3 + bitmask4 #Bits 1-4
        # self.ADC2ModeConfigOptions = {0: 0x00, 1: 0x02, 2: 0x04, 3: 0x08, 4: 0x10}
        # self.ADC3ModeMask = bitmask5 + bitmask6 + bitmask7 + bitmask8 #Bits 5-8
        # self.ADC3ModeConfigOptions = {0: 0x00, 1: 0x20, 2: 0x40, 3: 0x80, 4: 0x100}
        # self.ADC4ModeMask = bitmask9 + bitmask10 + bitmask11 + bitmask12 #Bits 9-12
        # self.ADC4ModeConfigOptions = {0: 0x00, 1: 0x200, 2: 0x400, 3: 0x800, 4: 0x1000}
        # self.ADCChooserMask = bitmask13
        self.ADC0enableMask = bitmask1
        self.ADC1enableMask = bitmask2
        self.ADC2enableMask = bitmask1
        self.ADC3enableMask = bitmask2
        self.ADC4enableMask = bitmask3
        self.rowSelectMask = bitmask0 + bitmask1 + bitmask2 #Bits 0-2
        self.rowSelectOptions = {0: 0x00, 1: 0x01, 2: 0x02, 3: 0x03, 4: 0x04}
        self.amplifierGainMask = {0: bitmask1 + bitmask2, 1: bitmask6 + bitmask7, 2: bitmask11 + bitmask12, 3: bitmask16 + bitmask17, 4: bitmask21 + bitmask22}
        self.amplifierGainOptions = {0: 0b000, 1: 0b010, 2:0b100, 3:0b110}
        self.biasEnableMask = {0: bitmask3, 1: bitmask8, 2: bitmask13, 3: bitmask18, 4: bitmask23}
        self.integratorResetMask = {0: bitmask25, 1: bitmask26, 2: bitmask27, 3: bitmask28, 4: bitmask29}
        self.connectElectrodeMask = {0: bitmask4, 1: bitmask9, 2: bitmask14, 3: bitmask19, 4: bitmask24}
        self.connectISRCEXTMask = {0: bitmask0, 1: bitmask5, 2: bitmask10, 3: bitmask15, 4: bitmask20}
        self.DAC0ConfigMask = bitmask9 + bitmask10 + bitmask11 + bitmask12 + bitmask13 + bitmask14 + bitmask15 + bitmask16
        self.DAC1ConfigMask = bitmask17 + bitmask18 + bitmask19 + bitmask20 + bitmask21 + bitmask22 + bitmask23 + bitmask24
        self.DACMBConfigMask = bitmask9 + bitmask10 + bitmask11 + bitmask12 + bitmask13 + bitmask14 + bitmask15 + bitmask16
        self.enableTriangleWaveMask = bitmask26
        self.enableSquareWaveMask = bitmask27
        self.enableSwitchedCapClockMask = bitmask3
        #######################################################################

        #######################################################################
        # Default initializations
        #######################################################################
        self.createFPGAObjects()
        self.frameCounter = 0
        # self.ADC0ModeConfig = 0
        # self.ADC1ModeConfig = 0
        # self.ADC3ModeConfig = 0
        self.rowSelect = 0
        self.columnSelect = 0
        # self.ui.lineEdit_getDataSize.setPlaceholderText("Size of data (20e6)")
        self.ui.lineEdit_getDataFileSelect.setPlaceholderText("test")
        self.dataSize = 20000000
        self.dataFileSelected = "./test.hex"
        # self.structInstance = struct.Struct('i' * (dictOfConstants['FRAMELENGTH']/4))
        self.ui.lineEdit_logDuration.setPlaceholderText("1")
        self.ui.lineEdit_RDCFB.setPlaceholderText("50")
        self.updateReferenceelectrodePotential(0)
        self.updateCounterelectrodePotential(0)
        self.MBCommonModePotential = 0
        self.RDCFB = 50e6
        self.f = [0]
        self.PSD = [0]
        self.RMSNoise_100kHz = 0
        self.RMSNoise_1MHz = 0
        self.RAMMemoryUsage = 0.0
        self.ui.lineEdit_livePreviewFilterBandwidth.setPlaceholderText("100")
        self.livePreviewFilterBandwidth = 100e3
        self.IDCOffset = 0
        self.IVData_voltage = []
        self.IVData_current = []
        self.voltageSweepIndex = 0
        self.IVCycles = 0
        #######################################################################

        #######################################################################
        # Connecting signals to relevant functions
        #######################################################################
        self.ui.checkBox_ADC0enable.stateChanged.connect(self.checkBox_ADC0enable_clicked)
        self.ui.checkBox_ADC1enable.stateChanged.connect(self.checkBox_ADC1enable_clicked)
        self.ui.checkBox_ADC2enable.stateChanged.connect(self.checkBox_ADC2enable_clicked)
        self.ui.checkBox_ADC3enable.stateChanged.connect(self.checkBox_ADC3enable_clicked)
        self.ui.checkBox_ADC4enable.stateChanged.connect(self.checkBox_ADC4enable_clicked)
        self.ui.checkBox_ADCenable.stateChanged.connect(self.checkBox_ADCenable_clicked)

        self.ui.lineEdit_getDataFileSelect.editingFinished.connect(self.lineEdit_getDataFileSelect_editingFinished)
        self.ui.pushButton_getDataFileSelect.clicked.connect(self.pushButton_getDataFileSelect_clicked)

        self.ui.comboBox_rowSelect.activated.connect(self.comboBox_rowSelect_activated)
        self.ui.comboBox_columnSelect.activated.connect(self.comboBox_columnSelect_activated)
        self.ui.comboBox_amplifierGainSelect.activated.connect(self.comboBox_amplifierGainSelect_activated)

        self.ui.checkBox_biasEnable.stateChanged.connect(self.checkBox_biasEnable_clicked)
        self.ui.checkBox_integratorReset.stateChanged.connect(self.checkBox_integratorReset_clicked)
        self.ui.checkBox_connectElectrode.stateChanged.connect(self.checkBox_connectElectrode_clicked)
        self.ui.checkBox_connectISRCEXT.stateChanged.connect(self.checkBox_connectISRCEXT_clicked)
        self.ui.pushButton_programChip.clicked.connect(self.pushButton_programChip_clicked)

        self.ui.action_enableLivePreview.triggered.connect(self.action_enableLivePreview_triggered)
        self.ui.action_reset.triggered.connect(self.pushButton_reset_clicked)
        self.ui.action_programFPGAs.triggered.connect(self.action_programFPGAs_triggered)
        self.ui.action_loadData.triggered.connect(self.openLoadOldDataWindow)
        self.ui.action_capturePlot.triggered.connect(self.capturePlot_triggered)
        self.ui.action_addVerticalMarker.triggered.connect(self.addVerticalMarker_triggered)
        self.ui.action_addNoiseFit.triggered.connect(self.addNoiseFit_triggered)

        self.ui.pushButton_counterelectrodePotentialPlus900_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(0.9))
        self.ui.pushButton_counterelectrodePotentialMinus900_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(-0.9))
        self.ui.pushButton_counterelectrodePotentialPlus500_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(0.5))
        self.ui.pushButton_counterelectrodePotentialMinus500_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(-0.5))
        self.ui.pushButton_counterelectrodePotentialPlus400_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(0.4))
        self.ui.pushButton_counterelectrodePotentialMinus400_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(-0.4))
        self.ui.pushButton_counterelectrodePotentialPlus300_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(0.3))
        self.ui.pushButton_counterelectrodePotentialMinus300_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(-0.3))
        self.ui.pushButton_counterelectrodePotentialPlus200_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(0.2))
        self.ui.pushButton_counterelectrodePotentialMinus200_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(-0.2))
        self.ui.pushButton_counterelectrodePotentialPlus100_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(0.1))
        self.ui.pushButton_counterelectrodePotentialMinus100_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(-0.1))
        self.ui.pushButton_counterelectrodePotentialPlus50_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(0.05))
        self.ui.pushButton_counterelectrodePotentialMinus50_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(-0.05))
        self.ui.pushButton_counterelectrodePotentialZero_absolute.clicked.connect(lambda: self.updateCounterelectrodePotential(0))
        self.ui.pushButton_counterelectrodePotentialZero_absolute.clicked.connect(lambda: self.updateReferenceelectrodePotential(0))
        self.ui.pushButton_counterelectrodePotentialPlus100_relative.clicked.connect(lambda: self.updateCounterelectrodePotential(float(self.ui.lineEdit_counterelectrodePotential.text())/1000 + 0.1))
        self.ui.pushButton_counterelectrodePotentialMinus100_relative.clicked.connect(lambda: self.updateCounterelectrodePotential(float(self.ui.lineEdit_counterelectrodePotential.text())/1000 - 0.1))
        self.ui.pushButton_counterelectrodePotentialPlus50_relative.clicked.connect(lambda: self.updateCounterelectrodePotential(float(self.ui.lineEdit_counterelectrodePotential.text())/1000 + 0.05))
        self.ui.pushButton_counterelectrodePotentialMinus50_relative.clicked.connect(lambda: self.updateCounterelectrodePotential(float(self.ui.lineEdit_counterelectrodePotential.text())/1000 - 0.05))
        self.ui.pushButton_counterelectrodePotentialPlus10_relative.clicked.connect(lambda: self.updateCounterelectrodePotential(float(self.ui.lineEdit_counterelectrodePotential.text())/1000 + 0.01))
        self.ui.pushButton_counterelectrodePotentialMinus10_relative.clicked.connect(lambda: self.updateCounterelectrodePotential(float(self.ui.lineEdit_counterelectrodePotential.text())/1000 - 0.01))

        self.ui.lineEdit_RDCFB.editingFinished.connect(self.lineEdit_RDCFB_editingFinished)

        self.ui.pushButton_IDCSetOffset.clicked.connect(self.pushButton_IDCSetOffset_clicked)

        self.ui.checkBox_enableTriangleWave.clicked.connect(self.checkBox_enableTriangleWave_clicked)
        self.ui.checkBox_enableSquareWave.clicked.connect(self.checkBox_enableSquareWave_clicked)
        self.ui.checkBox_enableSwitchedCapClock.clicked.connect(self.checkBox_enableSwitchedCapClock_clicked)
        self.ui.action_enableIV.triggered.connect(self.action_enableIV_triggered)

        self.ui.lineEdit_livePreviewFilterBandwidth.editingFinished.connect(self.lineEdit_livePreviewFilterBandwidth_editingFinished)

        # self.ui.label_poreResistance.mouseReleaseEvent = self.label_poreResistance_clicked()

        #######################################################################
        # Initializing plots
        #######################################################################
        self.ui.graphicsView_time_plot = self.ui.graphicsView_time.plot(numpy.linspace(0, 0.1, 100), numpy.ones(100), pen='b')
        self.ui.graphicsView_time.setClipToView(True)
        self.ui.graphicsView_time.setDownsampling(auto=True, mode='peak')
        self.ui.graphicsView_time.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_time.setLabel(axis='bottom', text='Time', units='s')
        self.ui.graphicsView_time.setLabel(axis='left', text='I', units='A')
        self.ui.graphicsView_time.disableAutoRange()

        self.ui.graphicsView_frequency_plot = self.ui.graphicsView_frequency.plot(numpy.linspace(100, 10e6, 100), numpy.ones(100), pen='b')
        # self.ui.graphicsView_frequencyFit_plot = self.ui.graphicsView_frequency.plot(numpy.linspace(100, 10e6, 100), numpy.ones(100), pen='k', width=2)
        self.ui.graphicsView_frequency.setLogMode(x=True, y=True)
        self.ui.graphicsView_frequency.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_frequency.setLabel(axis='bottom', text='Frequency', units='Hz')
        self.ui.graphicsView_frequency.setLabel(axis='left', text='Output noise power (V<sup>2</sup>/Hz)')
        self.ui.graphicsView_frequency.disableAutoRange()

        self.ui.graphicsView_histogram_plot = self.ui.graphicsView_histogram.plot(numpy.linspace(0, 1, 100), numpy.zeros(100), pen='b')
        # self.ui.graphicsView_histogram.plot(self.bins, self.histogramView, pen='b', stepMode=True)
        self.ui.graphicsView_histogram.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_histogram.setLabel(axis='bottom', text='Count')
        self.ui.graphicsView_histogram.setLabel(axis='left', text='I', units='A')
        self.ui.graphicsView_histogram.disableAutoRange()

        self.ui.graphicsView_IV_plot = self.ui.graphicsView_IV.plot(numpy.linspace(0, 0.1, 100), numpy.ones(100), pen='b')
        # Commented out clipToView because it seemed to not display all the points
        # self.ui.graphicsView_IV.setClipToView(True) # Setting clipToView after downsampling significantly degrades performance
        # self.ui.graphicsView_IV_plot.setDownsampling(auto=True, method='peak') # Only downsample the time plot instead of the entire viewbox
        self.ui.graphicsView_IV.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_IV.setLabel(axis='bottom', text='Voltage', units='V')
        self.ui.graphicsView_IV.setLabel(axis='left', text='I', units='A')
        self.ui.graphicsView_IV.disableAutoRange()
        self.ui.graphicsView_IV_currentPoint = self.ui.graphicsView_IV.plot([0], [0], symbol='o', symbolBrush='k', symbolSize=7)

        #######################################################################
        # Assigning menu items to functions
        #######################################################################
        # self.ui.action_saveState.setShortcut('Ctrl+S')
        self.ui.action_saveState.triggered.connect(lambda: self.action_saveState_triggered(None))
        # self.ui.action_loadState.setShortcut('Ctrl+L')
        self.ui.action_loadState.triggered.connect(self.action_loadState_triggered)
        self.ui.action_compressData.triggered.connect(self.action_compressData_triggered)
        # self.ui.action_exit.setShortcut('Ctrl+Q')
        self.ui.action_exit.triggered.connect(self.close)
        # self.ui.action_options.setShortcut('Ctrl+P')
        self.ui.action_options.triggered.connect(self.action_options_triggered)
        # self.ui.shortcut_openLoadOldDataWindow = QtGui.QShortcut('Ctrl+M', self)
        # self.ui.shortcut_openLoadOldDataWindow.activated.connect(self.openLoadOldDataWindow)

        #######################################################################
        # Miscellaneous shortcuts
        #######################################################################
        self.ui.shortcut_autoRange = QtGui.QShortcut('Ctrl+A', self.ui.tabWidget_plot)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_time.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_frequency.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_histogram.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_IV.autoRange)

        #######################################################################
        # Timer creation
        #######################################################################
        self.livePreviewTimer = QtCore.QTimer(self)
        # self.livePreviewTimer.timeout.connect(self.checkBox_enableLivePreview_clicked)
        # self.livePreviewTimer.timeout.connect(self.checkBox_enableLogging_clicked)
        # self.livePreviewTimer.timeout.connect(self.displayLivePreview)
        self.livePreviewTimer.timeout.connect(self.label_bufferUtilizationUpdate)
        self.livePreviewTimer.timeout.connect(self.checkFPGAStatus)
        self.livePreviewTimer.timeout.connect(self.updateMBCommonModePotential)
        self.livePreviewTimer.start(1000)

        self.IVTimer = QtCore.QTimer(self)
        self.IVTimer.timeout.connect(self.updateCounterelectrodePotential)
        self.IVTimer.setInterval(dictOfConstants['IVTIMESTEP'])

        self.ui.action_reset.setChecked(1)
        time.sleep(0.01)
        self.ui.action_reset.setChecked(0)

    def createFPGAObjects(self):
        #######################################################################
        # Create FPGA objects
        #######################################################################
        self.FPGAMasterInstance = FPGA(masterSerial, 'Master')
        self.FPGASlaveInstance = FPGA(slaveSerial, 'Slave')
        try:
            # self.FPGAMasterInstance.initializeDevice('Bitfiles/top_40M222.bit')
            # self.FPGAMasterInstance.initializeDevice('Bitfiles/top_40M22_integratorReset1.bit')
            self.FPGAMasterInstance.initializeDevice('Bitfiles/top_CNP2V3_master.bit')
        except:
            print "Failed to program Master FPGA"
        try:
            # self.FPGASlaveInstance.initializeDevice('Bitfiles/top_slave_test.bit')
            self.FPGASlaveInstance.initializeDevice('Bitfiles/top_CNP2V3_slave.bit')
        except:
            print "Failed to program Slave FPGA"

    def checkFPGAStatus(self):
        """Checks the status of both FPGAs. Also sets the text and icon on the GUI to reflect the configuration status of the corresponding FPGA"""
        if self.FPGAMasterInstance.configured:
            # self.ui.label_FPGAMasterStatus_text.setText('Active')
            self.ui.label_FPGAMasterStatus_icon.setPixmap(QtGui.QPixmap('./Icons/icons/status.png'))
        else:
            # self.ui.label_FPGAMasterStatus_text.setText('Inactive')
            self.ui.label_FPGAMasterStatus_icon.setPixmap(QtGui.QPixmap('./Icons/icons/status-busy.png'))
        if self.FPGASlaveInstance.configured:
            # self.ui.label_FPGASlaveStatus_text.setText('Active')
            self.ui.label_FPGASlaveStatus_icon.setPixmap(QtGui.QPixmap('./Icons/icons/status.png'))
        else:
            # self.ui.label_FPGASlaveStatus_text.setText('Inactive')
            self.ui.label_FPGASlaveStatus_icon.setPixmap(QtGui.QPixmap('./Icons/icons/status-busy.png'))

    def createThreads(self):
        #######################################################################
        # Thread instantiation
        #######################################################################
        self.PSDThread = QtCore.QThread()
        self.PSDWorkerInstance = workerobjects.PSDWorker(self, dictOfConstants)
        self.PSDWorkerInstance.moveToThread(self.PSDThread)
        self.PSDWorkerInstance.finished.connect(self.PSDThread.quit)
        self.PSDWorkerInstance.finished.connect(self.updateNoiseLabels)
        self.PSDThread.started.connect(self.PSDWorkerInstance.calculatePSD)

        self.processRawDataMasterThread = QtCore.QThread()
        self.processRawDataMasterWorkerInstance = workerobjects.ProcessRawDataWorker(self, dictOfConstants, self.FPGAMasterInstance)
        self.processRawDataMasterWorkerInstance.moveToThread(self.processRawDataMasterThread)
        #self.processRawDataMasterWorkerInstance.pycharm.connect(self.processRawDataMasterThread.quit)
        self.processRawDataMasterWorkerInstance.finished.connect(self.processRawDataMasterThread.quit)
        self.processRawDataMasterWorkerInstance.dataReady.connect(self.displayLivePreview)
        self.processRawDataMasterWorkerInstance.startPSDThread.connect(self.PSDThread.start)
        self.processRawDataMasterThread.started.connect(self.processRawDataMasterWorkerInstance.processRawData)

        self.processRawDataSlaveThread = QtCore.QThread()
        self.processRawDataSlaveWorkerInstance = workerobjects.ProcessRawDataWorker(self, dictOfConstants, self.FPGASlaveInstance)
        self.processRawDataSlaveWorkerInstance.moveToThread(self.processRawDataSlaveThread)
        self.processRawDataSlaveWorkerInstance.finished.connect(self.processRawDataSlaveThread.quit)
        self.processRawDataSlaveWorkerInstance.dataReady.connect(self.displayLivePreview)
        self.processRawDataSlaveWorkerInstance.startPSDThread.connect(self.PSDThread.start)
        self.processRawDataSlaveThread.started.connect(self.processRawDataSlaveWorkerInstance.processRawData)

        self.getDataFromFPGAMasterThread = QtCore.QThread()
        self.getDataFromFPGAMasterWorkerInstance = workerobjects.GetDataFromFPGAWorker(self, dictOfConstants, self.FPGAMasterInstance)
        self.getDataFromFPGAMasterWorkerInstance.moveToThread(self.getDataFromFPGAMasterThread)
        self.getDataFromFPGAMasterWorkerInstance.finished.connect(self.getDataFromFPGAMasterThread.quit)
        self.getDataFromFPGAMasterWorkerInstance.dataReady.connect(self.action_enableLogging_triggered)
        # self.getDataFromFPGAMasterWorkerInstance.dataReady.connect(self.checkBox_enableLogging_clicked)
        self.getDataFromFPGAMasterThread.started.connect(self.getDataFromFPGAMasterWorkerInstance.getDataFromFPGA)

        self.getDataFromFPGASlaveThread = QtCore.QThread()
        self.getDataFromFPGASlaveWorkerInstance = workerobjects.GetDataFromFPGAWorker(self, dictOfConstants, self.FPGASlaveInstance)
        self.getDataFromFPGASlaveWorkerInstance.moveToThread(self.getDataFromFPGASlaveThread)
        self.getDataFromFPGASlaveWorkerInstance.finished.connect(self.getDataFromFPGASlaveThread.quit)
        # self.getDataFromFPGASlaveWorkerInstance.dataReady.connect(self.checkBox_enableLogging_clicked)
        self.getDataFromFPGASlaveThread.started.connect(self.getDataFromFPGASlaveWorkerInstance.getDataFromFPGA)

        self.writeToLogFileThread = QtCore.QThread()
        self.writeToLogFileWorkerInstance = workerobjects.WriteToLogFileWorker(self, dictOfConstants)
        self.writeToLogFileWorkerInstance.moveToThread(self.writeToLogFileThread)
        self.writeToLogFileWorkerInstance.finished.connect(self.writeToLogFileThread.quit)
        # self.writeToLogFileWorkerInstance.finished.connect(self.action_enableLogging_triggered)
        self.writeToLogFileThread.started.connect(self.writeToLogFileWorkerInstance.writeToLogFile)

        self.getDataFromFPGAMasterThread.start(5)
        self.getDataFromFPGASlaveThread.start(5)


    def closeEvent(self, event):
        """Close out all child windows if open and existing threads if running, before closing self"""
        # Try closing any windows that might be open
        try:
            self.optionsWindow0.close()
        except:
            pass
        try:
            self.loadOldDataWindow0.close()
        except:
            pass
        try:
            self.compressDataWindow0.close()
        except:
            pass
        # Let all threads quit before exiting program
        self.FPGAMasterInstance.configured = False
        self.FPGASlaveInstance.configured = False
        self.getDataFromFPGAMasterThread.quit()
        self.getDataFromFPGAMasterThread.wait()
        self.getDataFromFPGASlaveThread.quit()
        self.getDataFromFPGASlaveThread.wait()
        self.processRawDataMasterThread.quit()
        self.processRawDataMasterThread.wait()
        self.processRawDataSlaveThread.quit()
        self.processRawDataSlaveThread.wait()
        self.PSDThread.quit()
        self.PSDThread.wait()
        self.writeToLogFileThread.quit()
        self.writeToLogFileThread.wait()
        event.accept()

    def action_programFPGAs_triggered(self):
        """Creates FPGA objects and the necessary threads. This function is needed only if the FPGAs were not powered on at the time of starting the GUI."""
        self.createFPGAObjects()
        self.createThreads()

    def pushButton_reset_clicked(self):
        """Checks to see if the reset button has been pressed or not. Resets both FPGAs if the button is pressed"""
        if (self.ui.pushButton_reset.isChecked() or self.ui.action_reset.isChecked()):
            reset = 1
        else:
            reset = 0
        self.FPGAMasterInstance.xem.SetWireInValue(0x00, reset*self.resetMask, self.resetMask)
        self.FPGAMasterInstance.UpdateWire = True
        self.FPGASlaveInstance.xem.SetWireInValue(0x00, reset*self.resetMask, self.resetMask)
        self.FPGASlaveInstance.UpdateWire = True

    def checkBox_ADCenable_clicked(self, state):
        """Enables/Disables ADCs depending on the status of the enable all ADCs checkbox"""
        if (self.ui.checkBox_ADCenable.isChecked()):
            enableADC = 1
        else:
            enableADC = 0
        if (enableADC == 1):
            self.ui.checkBox_ADC0enable.setChecked(1)
            self.ui.checkBox_ADC1enable.setChecked(1)
            self.ui.checkBox_ADC2enable.setChecked(1)
            self.ui.checkBox_ADC3enable.setChecked(1)
            self.ui.checkBox_ADC4enable.setChecked(1)
        else:
            self.ui.checkBox_ADC0enable.setChecked(0)
            self.ui.checkBox_ADC1enable.setChecked(0)
            self.ui.checkBox_ADC2enable.setChecked(0)
            self.ui.checkBox_ADC3enable.setChecked(0)
            self.ui.checkBox_ADC4enable.setChecked(0)

    def checkBox_ADC0enable_clicked(self, state):
        """Enables/Disables ADC0 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC0enable.isChecked()):
            ADC0enableBar = 0
        else:
            ADC0enableBar = 1
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x00, ADC0enableBar*self.ADC0enableMask, self.ADC0enableMask)
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Could not disable ADC 0"
        self.FPGAMasterInstance.UpdateWire = True

    def checkBox_ADC1enable_clicked(self, state):
        """Enables/Disables ADC1 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC1enable.isChecked()):
            ADC1enableBar = 0
        else:
            ADC1enableBar = 1
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x00, ADC1enableBar*self.ADC1enableMask, self.ADC1enableMask)
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Could not disable ADC 1"
        self.FPGAMasterInstance.UpdateWire = True

    def checkBox_ADC2enable_clicked(self, state):
        """Enables/Disables ADC2 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC2enable.isChecked()):
            ADC2enableBar = 0
        else:
            ADC2enableBar = 1
        errorReturn = self.FPGASlaveInstance.xem.SetWireInValue(0x00, ADC2enableBar*self.ADC2enableMask, self.ADC2enableMask)
        if (self.FPGASlaveInstance.xem.NoError != errorReturn):
            print "Could not disable ADC 2"
        self.FPGASlaveInstance.UpdateWire = True

    def checkBox_ADC3enable_clicked(self, state):
        """Enables/Disables ADC3 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC3enable.isChecked()):
            ADC3enableBar = 0
        else:
            ADC3enableBar = 1
        errorReturn = self.FPGASlaveInstance.xem.SetWireInValue(0x00, ADC3enableBar*self.ADC3enableMask, self.ADC3enableMask)
        if (self.FPGASlaveInstance.xem.NoError != errorReturn):
            print "Could not disable ADC 3"
        self.FPGASlaveInstance.UpdateWire = True

    def checkBox_ADC4enable_clicked(self, state):
        """Enables/Disables ADC4 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC4enable.isChecked()):
            ADC4enableBar = 0
        else:
            ADC4enableBar = 1
        errorReturn = self.FPGASlaveInstance.xem.SetWireInValue(0x00, ADC4enableBar*self.ADC4enableMask, self.ADC4enableMask)
        if (self.FPGASlaveInstance.xem.NoError != errorReturn):
            print "Could not disable ADC 4"
        self.FPGASlaveInstance.UpdateWire = True

    def lineEdit_getDataSize_editingFinished(self):
        """This method gets the data size to be saved from the text box called lineEdit_getDataSize once it is done being edited"""
        try:
            self.dataSize = int(eval(str(self.ui.lineEdit_getDataSize.displayText())))
        except TypeError:
            print "Enter the size of the data to be transferred in scientific notation"
        # self.structInstance = struct.Struct('i' * (self.dataSize / 4))
        print self.ui.lineEdit_getDataSize.displayText()

    def lineEdit_getDataFileSelect_editingFinished(self):
        """Displays the selected file in the lineEdit_getDataFileSelect box"""
        # print self.ui.lineEdit_getDataFileSelect.displayText()
        self.dataFileSelected = str(self.ui.lineEdit_getDataFileSelect.displayText())
        # print self.dataFileSelected[-4:]
        if (".hex" == self.dataFileSelected[-4:]):
            self.dataFileSelected = self.dataFileSelected[0:len(self.dataFileSelected)-4]
        print self.dataFileSelected

    def pushButton_getDataFileSelect_clicked(self):
        """This method handles the behaviour of the GUI when the browse button corresponding to the data file to be saved is clicked.
        Opens a file dialog for picking the file and then updates the corresponding text box to reflect the selection"""
        if not os.path.exists("./Logfiles"):
            os.makedirs("./Logfiles")
        folderSelecter = QtGui.QFileDialog()
        self.dataFolderSelected = folderSelecter.getExistingDirectory(self, "Select Folder", "./Logfiles")#, "./", filter="Hex files (*.hex)", selectedFilter="*.hex")
        self.ui.lineEdit_getDataFileSelect.setText(self.dataFolderSelected)

    def pushButton_getData_clicked(self):
        """Activates the file transfer. The length of the data is defined by the specified duration"""
        self.ui.lineEdit_logDuration.setText(str(round(self.dataSize/dictOfConstants['FRAMELENGTH_MASTER']*dictOfConstants['FRAMEDURATION']/1000.0, 1)))
        self.ui.action_enableLogging.setChecked(1)

    def comboBox_rowSelect_activated(self, index):
        """Sets the row selection for the chip (and the daughterboard)"""
        self.rowSelect = self.rowSelectOptions[index]
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x02, self.rowSelect, self.rowSelectMask)
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Selecting new row failed"
        self.FPGAMasterInstance.UpdateWire = True
        if (4 == self.rowSelect):
            self.ui.checkBox_enableSwitchedCapClock.setEnabled(1)
        else:
            self.ui.checkBox_enableSwitchedCapClock.setChecked(0)
            self.ui.checkBox_enableSwitchedCapClock.setEnabled(0)

    def comboBox_columnSelect_activated(self, index):
        """Sets the column selection for the chip. Clears out data for the other columns when a column switch is initiated"""
        self.columnSelect = index
        self.ui.checkBox_biasEnable.setChecked(0) #Clear all config data when changing amplifiers
        self.ui.checkBox_integratorReset.setChecked(0)
        self.ui.checkBox_connectElectrode.setChecked(0)
        self.ui.checkBox_connectISRCEXT.setChecked(0)
        self.IDCOffset = 0 # Clear out the offset current when column is changed
        # Need to try because signal may not be connected at start of program
        try:
            self.getDataFromFPGAMasterWorkerInstance.dataReady.disconnect(self.action_enableLogging_triggered)
        except:
            pass
        try:
            self.getDataFromFPGASlaveWorkerInstance.dataReady.disconnect(self.action_enableLogging_triggered)
        except:
            pass
        if (self.columnSelect in self.FPGAMasterInstance.validColumns):
            self.getDataFromFPGAMasterWorkerInstance.dataReady.connect(self.action_enableLogging_triggered)
        elif (self.columnSelect in self.FPGASlaveInstance.validColumns):
            self.getDataFromFPGASlaveWorkerInstance.dataReady.connect(self.action_enableLogging_triggered)

    def comboBox_amplifierGainSelect_activated(self, index):
        """Sets the amplifier gain (by setting the feedback capacitor) for the selected amplifier"""
        amplifierGainSelect = index
        shiftFactor = self.columnSelect*5 #Shift config bits by 5x depending on the xth column selected
        self.amplifierGain = self.amplifierGainMask[self.columnSelect] & ((self.amplifierGainOptions[amplifierGainSelect]) << shiftFactor)
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x01, self.amplifierGain, self.amplifierGainMask[self.columnSelect])
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Changing feedback capacitance value failed"
        self.FPGAMasterInstance.UpdateWire = True

    def checkBox_biasEnable_clicked(self, state):
        """Determines whether the selected amplifier is enabled or not"""
        if (self.ui.checkBox_biasEnable.isChecked()):
            biasEnable = 1
        else:
            biasEnable = 0
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x01, self.biasEnableMask[self.columnSelect]*biasEnable, self.biasEnableMask[self.columnSelect])
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Enabling bias failed"
        self.FPGAMasterInstance.UpdateWire = True

    def checkBox_integratorReset_clicked(self, state):
        """Sets the integrator reset switch (bypassing the feedback capacitor for the integrator). Use while electroplating Ag"""
        if (self.ui.checkBox_integratorReset.isChecked()):
            integratorReset = 1
        else:
            integratorReset = 0
        print "%x" %(self.integratorResetMask[self.rowSelect])
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x01, self.integratorResetMask[self.rowSelect]*integratorReset, self.integratorResetMask[self.rowSelect])
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Integrator reset failed"
        self.FPGAMasterInstance.UpdateWire = True

    def checkBox_connectElectrode_clicked(self, state):
        """Connects the electrode on the surface of the chip to the amplifier"""
        if (self.ui.checkBox_connectElectrode.isChecked()):
            connectElectrode = 1
        else:
            connectElectrode = 0
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x01, self.connectElectrodeMask[self.columnSelect]*connectElectrode, self.connectElectrodeMask[self.columnSelect])
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Enabling bias failed"
        self.FPGAMasterInstance.UpdateWire = True

    def checkBox_connectISRCEXT_clicked(self, state):
        """Connects ISRCEXT (which is connected to a header on the daughterboard) to the amplifier"""
        if (self.ui.checkBox_connectISRCEXT.isChecked()):
            connectISRCEXT = 1
        else:
            connectISRCEXT = 0
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x01, self.connectISRCEXTMask[self.columnSelect]*connectISRCEXT, self.connectISRCEXTMask[self.columnSelect])
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Connecting ISRCEXT failed"
        self.FPGAMasterInstance.UpdateWire = True

    def pushButton_programChip_clicked(self):
        """Programs the chip with the current settings determined by the GUI. The chip won't update its settings if this isn't pressed!"""
        self.FPGAMasterInstance.ActivateTrigger = True
        self.FPGAMasterInstance.TriggerEndpoint = 0x41
        self.FPGAMasterInstance.TriggerBitmask = 1

    def action_enableLivePreview_triggered(self):
        """This method is called whenever the corresponding checkbox is clicked. If live preview is enabled, this method creates a worker thread to get data from the FPGA assuming one doesn't exist already"""
        if (self.ui.action_enableLivePreview.isChecked()):
            # print dictOfConstants['FRAMELENGTH']
            self.start = time.clock()
            # print self.start
            if not (self.getDataFromFPGAMasterThread.isRunning()):
                self.getDataFromFPGAMasterThread.start()
            if not (self.getDataFromFPGASlaveThread.isRunning()):
                self.getDataFromFPGASlaveThread.start()

    def action_enableLogging_triggered(self):
        """This method is used to check if log data is enabled and when it should be disabled. Depending on the log duration, this method counts the time that has elapsed since logging was enabled and then disables logging automatically"""
        try:
            logDuration = int(float(self.ui.lineEdit_logDuration.text())*1000)
        except:
            logDuration = 1000
        if (self.ui.action_enableLogging.isChecked()):
            self.frameCounter += 1
            if (self.writeToLogFileWorkerInstance.rawData.qsize() >= dictOfConstants['REFRESHRATE']):
                self.writeToLogFileThread.start() # Write data to disk as soon as there is 1 second's worth to be written
            if (self.frameCounter == dictOfConstants['REFRESHRATE'] * logDuration / 1000):
                self.ui.action_enableLogging.toggle()
                self.frameCounter = 0
        else:
            self.frameCounter = 0
            # Write any leftover data in memory to disk
            if (self.writeToLogFileWorkerInstance.rawData.qsize() > 0 and not self.writeToLogFileThread.isRunning()):
                self.writeToLogFileThread.start()

    def displayLivePreview(self):
        """This method plots self.dataToDisplay from the worker thread that gets data from the FPGA and processes it. The data being displayed is already a subsampled version of the full data. PyQtGraph then displays the data in the GUI."""
        self.start = time.clock()
        if (self.ui.action_enableLivePreview.isChecked()):
            if (0 == self.ui.tabWidget_plot.currentIndex()):
                self.ui.graphicsView_time_plot.setData(numpy.linspace(0, len(self.dataToDisplay)*dictOfConstants['SUBSAMPLINGFACTOR']*1.0/dictOfConstants['ADCSAMPLINGRATE'], len(self.dataToDisplay)), self.dataToDisplay)
                if (self.ui.action_addVerticalMarker.isChecked() == True):
                    self.graphicsView_time_updateMarkerText()
            elif (1 == self.ui.tabWidget_plot.currentIndex() and 0 not in self.PSD):
                self.ui.graphicsView_frequency_plot.setData(self.f, self.PSD)
                if (self.ui.action_addVerticalMarker.isChecked() == True):
                    self.graphicsView_frequency_updateMarkerText()
                if (self.ui.action_addNoiseFit.isChecked() == True and hasattr(self, 'PSDFit')):
                    self.ui.graphicsView_frequencyFit_plot.setData(self.f, self.PSDFit)
            elif (2 == self.ui.tabWidget_plot.currentIndex()):
                self.ui.graphicsView_histogram_plot.setData(self.histogramView, self.bins[0:len(self.bins)-1] + (self.bins[1]-self.bins[0])/2)
            elif (3 == self.ui.tabWidget_plot.currentIndex()):
                if self.IVData_voltage != []:
                    self.ui.graphicsView_IV_plot.setData(self.IVData_voltage, self.IVData_current)
                    self.ui.graphicsView_IV_currentPoint.setData([self.IVData_voltage[-1]], [self.IVData_current[-1]])
            self.stop = time.clock()
            # print "Main GUI thread took", self.stop-self.start, "s"

    def updateReferenceelectrodePotential(self, value=0):
        """Updates the reference electrode potential. This is called once at the start of the program to set the reference potential to 900mV and subsequently everytime the counter electrode is set to 0 relative potential."""
        newValue = value + 0.9
        newValue = max(newValue, 0) #Setting lower limit
        newValue = min(newValue, 1.8*255/256) #Setting upper limit (1.8 * 255/256)
        referenceelectrodePotential = int(round(newValue/1.8 * 256)) * 2**9 #2^9 because DAC0ConfigMask starts from bit 9
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x00, referenceelectrodePotential, self.DAC0ConfigMask)
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Failed to set counter electrode potential"
        self.FPGAMasterInstance.UpdateWire = True
        self.FPGAMasterInstance.ActivateTrigger = True
        self.FPGAMasterInstance.TriggerEndpoint = 0x41
        self.FPGAMasterInstance.TriggerBitmask = 2
        print "Set reference electrode potential to", (newValue * 1000), "mV"

    def updateCounterelectrodePotential(self, value=0):
        """Updates the counterelectrode potential to the new value defined by value. The counterelectrode potential is determined by a DAC whose inputs are between 0 and 255 and whose analog output can range from 0 to Vdd (1.8V)."""
        newValue = value + 0.9 - 0.00 # Subtract 0.03 V to account for offset
        newValue = max(newValue, 0) #Setting lower limit
        newValue = min(newValue, 1.8*255/256) #Setting upper limit (1.8 * 255/256)
        if (self.ui.action_enableIV.isChecked() is True):
            if (self.IVFirstPoint is True):
                self.IVFirstPoint = False
            else:
                self.IVData_voltage.append(self.IVData_voltageSweep[self.voltageSweepIndex-1])
                self.IVData_current.append(self.IDCRelative)
            self.voltageSweepIndex %= len(self.IVData_voltageSweep)
            newValue = self.IVData_voltageSweep[self.voltageSweepIndex] + 0.9
            self.voltageSweepIndex += 1
            if (self.voltageSweepIndex == 1):
                self.IVCycles += 1
                if (dictOfConstants['IVNUMBEROFCYCLES'] != 0):
                    if (self.IVCycles > dictOfConstants['IVNUMBEROFCYCLES']):
                        self.ui.action_enableIV.setChecked(False)
                        self.action_enableIV_triggered()
                        self.IVCycles = 0
                else:
                    self.IVCycles = 0
        counterelectrodePotential = int(round(newValue/1.8 * 256)) * 2**17 #2^17 because DAC1ConfigMask starts from bit 17
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x00, counterelectrodePotential, self.DAC1ConfigMask)
        if (self.FPGAMasterInstance.xem.NoError != errorReturn):
            print "Failed to set counter electrode potential"
        self.FPGAMasterInstance.UpdateWire = True
        self.FPGAMasterInstance.ActivateTrigger = True
        self.FPGAMasterInstance.TriggerEndpoint = 0x41
        self.FPGAMasterInstance.TriggerBitmask = 2
        self.ui.lineEdit_counterelectrodePotential.setText(str(round((newValue - 0.9) * 1000)))

    def updateMBCommonModePotential(self):
        """Updates the motherboard common mode potential. This is called once every second or so to set the potential to the value specified in the options window but action is taken only if the value was changed."""
        if (self.MBCommonModePotential != dictOfConstants['MBCOMMONMODE']):
            self.MBCommonModePotential = dictOfConstants['MBCOMMONMODE'] # Nominally should be 1.65 V
            self.MBCommonModePotential_approximate = int(round(self.MBCommonModePotential/3.3 * 256)) * 2**9 #2^9 because DAC0ConfigMask starts from bit 9
            errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x02, self.MBCommonModePotential_approximate, self.DACMBConfigMask)
            if (self.FPGAMasterInstance.xem.NoError != errorReturn):
                print "Failed to set counter electrode potential"
            self.FPGAMasterInstance.UpdateWire = True
            self.FPGAMasterInstance.ActivateTrigger = True
            self.FPGAMasterInstance.TriggerEndpoint = 0x41
            self.FPGAMasterInstance.TriggerBitmask = 3
            print "Set motherboard common mode potential to", (self.MBCommonModePotential * 1000), "mV"


    def pushButton_IDCSetOffset_clicked(self):
        """Updates the DC offset current value so that the current being viewed has no DC component left in it"""
        self.IDCOffset += self.IDCRelative
        self.ui.label_IDCOffset.setText(str(self.IDCOffset * 1e9))

    def updateIDCLabels(self):
        """Update labels on the GUI indicating the DC offset current, DC relative current and DC net current"""
        self.ui.label_IDCOffset.setText(str(round(self.IDCOffset * 1e9, 1)))
        self.ui.label_IDCRelative.setText(str(round(self.IDCRelative * 1e9, 1)))
        self.ui.label_IDCNet.setText(str(round((self.IDCOffset + self.IDCRelative) * 1e9, 1)))

    def updateNoiseLabels(self):
        """Update labels on the GUI indicating the integrated noise values at 100 kHz, 1 MHz and 10 MHz bandwidths"""
        self.ui.label_100kHzNoise.setText(str(self.RMSNoise_100kHz))
        self.ui.label_1MHzNoise.setText(str(self.RMSNoise_1MHz))
        self.ui.label_10MHzNoise.setText(str(self.RMSNoise_10MHz))

    def label_bufferUtilizationUpdate(self):
        """Update label on the GUI indicating RAM utilization on the FPGA that is acquiring the data currently being displayed"""
        # if self.FPGAMasterInstance.configured is True:
        #     self.ui.label_FPGAMasterBufferUtilization.setText(str(self.FPGAMasterRAMMemoryUsage)+'/128 MB')
        # if self.FPGASlaveInstance.configured is True:
        #     self.ui.label_FPGASlaveBufferUtilization.setText(str(self.FPGASlaveRAMMemoryUsage)+'/128 MB')
        pass

    def lineEdit_RDCFB_editingFinished(self):
        """Reads in the new value of RDCFB from the GUI once it has been edited"""
        self.oldRDCFB = self.RDCFB
        try:
            self.RDCFB = eval(str(self.ui.lineEdit_RDCFB.text()))*1e6
            if self.RDCFB == 0:
                self.RDCFB = self.oldRDCFB
        except:
            self.RDCFB = 50*1e6
        self.ui.lineEdit_RDCFB.setText(str(round(self.RDCFB/1e6, 1)))

    def checkBox_enableTriangleWave_clicked(self):
        """Changes the pattern on the counterelectrode potential to a triangle wave. The actual code that generates the counterelectrode potential values to create the triangle wave is on the FPGA"""
        if (self.ui.checkBox_enableTriangleWave.isChecked()):
            enableTriangleWave = 1
        else:
            enableTriangleWave = 0
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x00, enableTriangleWave*self.enableTriangleWaveMask, self.enableTriangleWaveMask)
        self.FPGAMasterInstance.UpdateWire = True
        #Reset to old value if triangle wave is turned off
        if not (self.ui.checkBox_enableTriangleWave.isChecked()):
            oldValue = float(self.ui.lineEdit_counterelectrodePotential.text())/1000
            self.updateCounterelectrodePotential(oldValue)

    def checkBox_enableSquareWave_clicked(self):
        """Creates a square wave pattern on the counterelectrode instead of a triangle wave"""
        if (self.ui.checkBox_enableSquareWave.isChecked()):
            enableSquareWave = 1
        else:
            enableSquareWave = 0
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x00, enableSquareWave*self.enableSquareWaveMask, self.enableSquareWaveMask)
        self.FPGAMasterInstance.UpdateWire = True
        #Reset to old value if square wave is turned off
        if not (self.ui.checkBox_enableSquareWave.isChecked()):
            oldValue = float(self.ui.lineEdit_counterelectrodePotential.text())/1000
            self.updateCounterelectrodePotential(oldValue)

    def checkBox_enableSwitchedCapClock_clicked(self):
        """This method is only available when row 4 is selected on the chip. Activates the switched cap clock generation on the FPGA"""
        if (self.ui.checkBox_enableSwitchedCapClock.isChecked()):
            enableSwitchedCapClock = 1
        else:
            enableSwitchedCapClock = 0
        errorReturn = self.FPGAMasterInstance.xem.SetWireInValue(0x02, enableSwitchedCapClock*self.enableSwitchedCapClockMask, self.enableSwitchedCapClockMask)
        self.FPGAMasterInstance.UpdateWire = True

    def action_enableIV_triggered(self):
        """This method activates the IV measurement setup"""
        if not (self.FPGAMasterInstance.configured is True and self.FPGASlaveInstance.configured is True):
            self.ui.action_enableIV.setChecked(False)
        if dictOfConstants['PRESETMODE'] != 1:
            self.ui.action_enableIV.setChecked(False)
        if (self.ui.action_enableIV.isChecked()):
            self.IVFirstPoint = True
            self.IVData_voltage = []
            self.IVData_current = []
            self.voltageSweepIndex = 0
            self.ui.graphicsView_IV_plot.clear()
            forwardSweep = numpy.arange(dictOfConstants['IVSTARTVOLTAGE'], dictOfConstants['IVSTOPVOLTAGE'], dictOfConstants['IVVOLTAGESTEP']/1000.)
            reverseSweep = numpy.arange(dictOfConstants['IVSTOPVOLTAGE'], dictOfConstants['IVSTARTVOLTAGE'], -dictOfConstants['IVVOLTAGESTEP']/1000.)
            self.IVData_voltageSweep = numpy.hstack(numpy.asarray([forwardSweep, reverseSweep]))
            self.IVTimer.setInterval(dictOfConstants['IVTIMESTEP'])
            self.IVTimer.start()
        else:
            self.IVTimer.stop()

    def lineEdit_livePreviewFilterBandwidth_editingFinished(self):
        """Reads in the filter bandwidth that the live preview is eventually filtered down to and creates the appropriate filter in the processRawData worker"""
        try:
            self.livePreviewFilterBandwidth = eval(str(self.ui.lineEdit_livePreviewFilterBandwidth.text()))*1e3
        except:
            self.livePreviewFilterBandwidth = 100e3
        if (self.livePreviewFilterBandwidth > 10e6):
            self.livePreviewFilterBandwidth = 10e6
        self.ui.lineEdit_livePreviewFilterBandwidth.setText(str(int(self.livePreviewFilterBandwidth/1e3)))
        self.processRawDataMasterWorkerInstance.createFilter(self.livePreviewFilterBandwidth)
        self.processRawDataSlaveWorkerInstance.createFilter(self.livePreviewFilterBandwidth)

    def action_saveState_triggered(self, configSaveFileSelected = None):
        """Saves a variety of options from the GUI into a cfg file for easy loading later on"""
        stateConfig = {'rowSelect': self.ui.comboBox_rowSelect.currentIndex(),
        'columnSelect': self.ui.comboBox_columnSelect.currentIndex(),
        'amplifierGainSelect': self.ui.comboBox_amplifierGainSelect.currentIndex(),
        'biasEnable': self.ui.checkBox_biasEnable.isChecked(),
        'integratorReset': self.ui.checkBox_integratorReset.isChecked(),
        'connectElectrode': self.ui.checkBox_connectElectrode.isChecked(),
        'connectISRCEXT': self.ui.checkBox_connectISRCEXT.isChecked(),
        'RDCFB': self.RDCFB,
        'IDCOffset': self.IDCOffset}
        print configSaveFileSelected
        if (configSaveFileSelected is None):
            fileSelecter = QtGui.QFileDialog()
            configSaveFileSelected = fileSelecter.getSaveFileName(self, "Choose file", "./", filter="Config files (*.cfg)", selectedFilter="*.cfg")
        try:
            f = open(configSaveFileSelected, 'w')
        except:
            return False
        json.dump(stateConfig, f, indent=0)
        f.close()
        print "Saving state!"

    def action_loadState_triggered(self):
        """Loads a previously saved state (cfg file)"""
        fileSelecter = QtGui.QFileDialog()
        configLoadFileSelected = fileSelecter.getOpenFileName(self, "Choose file", "./", filter="Config files (*.cfg)", selectedFilter="*.cfg")
        try:
            f = open(configLoadFileSelected, 'r')
        except:
            return False
        stateConfig = json.load(f)
        self.loadState(stateConfig)
        f.close()
        print "Loading from state!"

    def loadState(self, stateConfig):
        """This method handles the actual loading of the cfg file"""
        self.loadStateConfig = {\
            'ADC0Mode': [lambda x: self.ui.comboBox_ADC0Mode.setCurrentIndex(x),\
                        lambda x: self.comboBox_ADC0Mode_activated(x)],\
            'ADC1Mode': [lambda x: self.ui.comboBox_ADC1Mode.setCurrentIndex(x),\
                        lambda x: self.comboBox_ADC1Mode_activated(x)],\
            'ADC2Mode': [lambda x: self.ui.comboBox_ADC2Mode.setCurrentIndex(x),\
                        lambda x: self.comboBox_ADC2Mode_activated(x)],\
            'ADC3Mode': [lambda x: self.ui.comboBox_ADC3Mode.setCurrentIndex(x),\
                        lambda x: self.comboBox_ADC3Mode_activated(x)],\
            'ADC4Mode': [lambda x: self.ui.comboBox_ADC4Mode.setCurrentIndex(x),\
                        lambda x: self.comboBox_ADC4Mode_activated(x)],\
            'rowSelect': [lambda x: self.ui.comboBox_rowSelect.setCurrentIndex(x),\
                        lambda x: self.comboBox_rowSelect_activated(x)],\
            'columnSelect': [lambda x: self.ui.comboBox_columnSelect.setCurrentIndex(x),\
                        lambda x: self.comboBox_columnSelect_activated(x)],\
            'amplifierGainSelect': [lambda x: self.ui.comboBox_amplifierGainSelect.setCurrentIndex(x),\
                        lambda x: self.comboBox_amplifierGainSelect_activated(x)],\
            'biasEnable': [lambda x: self.ui.checkBox_biasEnable.setChecked(x)],\
            'integratorReset': [lambda x: self.ui.checkBox_integratorReset.setChecked(x)],\
            'connectElectrode': [lambda x: self.ui.checkBox_connectElectrode.setChecked(x)],\
            'connectISRCEXT': [lambda x: self.ui.checkBox_connectISRCEXT.setChecked(x)],\
            'RDCFB': [lambda x: self.ui.lineEdit_RDCFB.setText(str(round(x/1e6, 1))),\
                        lambda x: self.lineEdit_RDCFB_editingFinished()],\
            'IDCOffset': [lambda x: self.updateIDCOffset(x)]}

        # Load columnSelect information first so that it doesn't reset the others
        # Refer self.comboBox_columnSelect_activated for more information
        stateConfig_columnSelect = stateConfig.pop('columnSelect', None)
        for i in range(len(self.loadStateConfig['columnSelect'])):
            self.loadStateConfig['columnSelect'][i](stateConfig_columnSelect)

        # Loop over the remaining keys in the cfg file and set them accordingly
        for key in stateConfig:
            if key == 'biasEnable':
                self.ui.checkBox_biasEnable.setChecked(1)
            try:
                for i in range(len(self.loadStateConfig[key])):
                    self.loadStateConfig[key][i](stateConfig[key])
            except:
                print "Failed at ", key
        self.pushButton_programChip_clicked()

    def action_compressData_triggered(self):
        self.compressDataWindow0 = CompressData(dictOfConstants)
        self.compressDataWindow0.show()

    def updateIDCOffset(self, value):
        """Method created to facilitate loading in the DC offset current value in the dictionary style loading"""
        self.IDCOffset = value
        self.updateIDCLabels()

    def action_options_triggered(self):
        """Creates an options window"""
        self.optionsWindow0 = OptionsWindow(dictOfConstants)
        self.optionsWindow0.show()

    def openLoadOldDataWindow(self):
        """Creates the GUI for viewing previously saved hex data"""
        self.loadOldDataWindow0 = LoadOldDataWindow()
        self.loadOldDataWindow0.show()

    def capturePlot_triggered(self):
        """Saves the currently displayed plot data as a CSV and a PNG file"""
        if (0 == self.ui.tabWidget_plot.currentIndex()):
            self.itemToExport = self.ui.graphicsView_time
            self.ui.graphicsView_time_plot.setDownsampling(False)
            self.ui.graphicsView_time.setClipToView(False)
        elif (1 == self.ui.tabWidget_plot.currentIndex()):
            self.itemToExport = self.ui.graphicsView_frequency
        elif (3 == self.ui.tabWidget_plot.currentIndex()):
            self.itemToExport = self.ui.graphicsView_IV
            self.ui.graphicsView_IV.removeItem(self.ui.graphicsView_IV_currentPoint)
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
        if (3 == self.ui.tabWidget_plot.currentIndex()):
            self.ui.graphicsView_IV.addItem(self.ui.graphicsView_IV_currentPoint)
        print "Saving CSV and PNG files!"

    def addVerticalMarker_triggered(self):
        """Adds a vertical marker to both the time and frequency views.
           In the time view, labels at the top right of the plot indicate the amplitude and time value at the marker.
           In the frequency view, labels at the top right of the plot indicate the integrated noise and frequency value at the marker"""
        if (self.ui.action_addVerticalMarker.isChecked()):
            self.ui.graphicsView_time.marker = pyqtgraph.InfiniteLine(0, angle=90, movable=True, pen='g')
            self.ui.graphicsView_time.marker.x = 0
            self.ui.graphicsView_time.marker.sigPositionChanged.connect(self.graphicsView_time_updateMarkerText)
            self.ui.graphicsView_time.markerValue = pyqtgraph.TextItem('X=0\nY=0', anchor = (1,0), color='g')
            self.ui.graphicsView_time.markerValue.setPos(len(self.dataToDisplay)*dictOfConstants['SUBSAMPLINGFACTOR']*1.0/dictOfConstants['ADCSAMPLINGRATE'], numpy.max(self.dataToDisplay))
            self.ui.graphicsView_time.addItem(self.ui.graphicsView_time.marker)
            self.ui.graphicsView_time.addItem(self.ui.graphicsView_time.markerValue)

            self.ui.graphicsView_frequency.marker = pyqtgraph.InfiniteLine(3, angle=90, movable=True, pen='g')
            self.ui.graphicsView_frequency.marker.x = 3
            self.ui.graphicsView_frequency.marker.sigPositionChanged.connect(self.graphicsView_frequency_updateMarkerText)
            self.ui.graphicsView_frequency.markerValue = pyqtgraph.TextItem('X=100\nY=0', anchor = (1,0), color='g')
            self.ui.graphicsView_frequency.markerValue.setPos(numpy.max(self.f), numpy.max(self.PSD))
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
            self.ui.graphicsView_time.marker.y = self.dataToDisplay[int(self.ui.graphicsView_time.marker.x/dictOfConstants['SUBSAMPLINGFACTOR']*dictOfConstants['ADCSAMPLINGRATE'])]
        except:
            self.ui.graphicsView_time.marker.y = 0
        self.ui.graphicsView_time.markerValue.setPlainText('X=' + '%.3E s' % self.ui.graphicsView_time.marker.x + '\nY=%.3E A' % self.ui.graphicsView_time.marker.y)
        self.ui.graphicsView_time.markerValue.setPos(self.ui.graphicsView_time.getViewBox().viewRange()[0][1], self.ui.graphicsView_time.getViewBox().viewRange()[1][1])
        # print self.ui.graphicsView_time.marker.value()

    def graphicsView_frequency_updateMarkerText(self):
        """Updates the labels at the top right of the plot whenever the marker is moved in the frequency view"""
        self.ui.graphicsView_frequency.marker.x = 10**float(self.ui.graphicsView_frequency.marker.value())
        try:
            self.ui.graphicsView_frequency.marker.y = self.RMSNoise[numpy.abs(self.f-self.ui.graphicsView_frequency.marker.x).argmin()]
        except:
            self.ui.graphicsView_frequency.marker.y = 0
        self.ui.graphicsView_frequency.markerValue.setPlainText('X=' + '%.3E Hz' % self.ui.graphicsView_frequency.marker.x + u'\n√(∫Y∆X)=%.3E Arms' % self.ui.graphicsView_frequency.marker.y)
        self.ui.graphicsView_frequency.markerValue.setPos(self.ui.graphicsView_frequency.getViewBox().viewRange()[0][1], self.ui.graphicsView_frequency.getViewBox().viewRange()[1][1])
        # print self.ui.graphicsView_time.marker.value()

    def addNoiseFit_triggered(self):
        """Adds a fit to the noise PSD. The data is fit to a*f^-1 + b + c*f + d*f^2"""
        if (self.ui.action_addNoiseFit.isChecked() == True):
            self.ui.graphicsView_frequencyFit_plot = self.ui.graphicsView_frequency.plot(numpy.linspace(100, 10e6, 100), numpy.ones(100), pen='k', width=2)
            self.displayLivePreview()
        else:
            self.ui.graphicsView_frequency.removeItem(self.ui.graphicsView_frequencyFit_plot)

    # def label_poreResistance_clicked(self):
        # self.temp = ~self.temp
        # if (True == self.temp):
            # self.ui.label_poreResistance.setText(u"MΩ")
        # else:
            # self.ui.label_poreResistance.setText("nS")
