# -*- coding: utf-8 -*-
import os
from PyQt4 import QtCore, QtGui
import numpy
import time, datetime
# import struct
import json
import pyqtgraph, pyqtgraph.exporters

import globalConstants
import channelComponents
from FPGA import FPGA
from cnp2_gui import Ui_MainWindow
from optionswindow import OptionsWindow
from compressdata import CompressData
from loadolddata import LoadOldDataWindow
import workerobjects

QWIDGETSIZE_MAX = ((1<<24)-1)  # Windows PyQt4 comments out the definition for this in QtGui and QWidget so it cannot be resolved. Including it myself here

# pyqtgraph.setConfigOptions(useWeave = False) #To remove gcc related error
pyqtgraph.setConfigOption('background', 'w') #Set background to white
pyqtgraph.setConfigOption('foreground', 'k') #Set foreground to black

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
        # self.ADC0ModeConfig = 0
        # self.ADC1ModeConfig = 0
        # self.ADC3ModeConfig = 0
        self.rowSelect = 0
        self.columnSelect = 0
        self.ui.lineEdit_logDuration.setPlaceholderText("1")
        self.mbCommonModePotential = 0
        self.RAMMemoryUsage = 0.0
        self.livePreviewFilterBandwidth = 100e3
        self.voltageSweepIndex = 0
        self.IVCycles = 0
        self.IVFirstPoint = False
        self.IVData_voltageSweep = 0

        self.adcList = []
        for i in xrange(5):
            self.adcList.append(channelComponents.ADC())

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

        self.ui.comboBox_rowSelect.activated.connect(self.comboBox_rowSelect_activated)
        self.ui.comboBox_columnSelect.activated.connect(self.comboBox_columnSelect_activated)
        self.ui.comboBox_amplifierGainSelect.activated.connect(self.comboBox_amplifierGainSelect_activated)

        self.ui.checkBox_biasEnable.stateChanged.connect(self.checkBox_biasEnable_clicked)
        self.ui.checkBox_integratorReset.stateChanged.connect(self.checkBox_integratorReset_clicked)
        self.ui.checkBox_connectElectrode.stateChanged.connect(self.checkBox_connectElectrode_clicked)
        self.ui.checkBox_connectISRCEXT.stateChanged.connect(self.checkBox_connectISRCEXT_clicked)

        self.ui.lineEdit_amplifierRDCFB.editingFinished.connect(self.lineEdit_amplifierRDCFB_editingFinished)

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

        self.ui.pushButton_IDCSetOffset.clicked.connect(self.pushButton_IDCSetOffset_clicked)
        self.ui.checkBox_enableTriangleWave.clicked.connect(self.checkBox_enableTriangleWave_clicked)
        self.ui.checkBox_enableSquareWave.clicked.connect(self.checkBox_enableSquareWave_clicked)
        self.ui.checkBox_enableSwitchedCapClock.clicked.connect(self.checkBox_enableSwitchedCapClock_clicked)
        self.ui.action_enableIV.triggered.connect(self.action_enableIV_triggered)
        self.ui.action_enableLogging.triggered.connect(self.action_enableLogging_triggered)
        self.ui.lineEdit_livePreviewFilterBandwidth.editingFinished.connect(self.lineEdit_livePreviewFilterBandwidth_editingFinished)

        # self.ui.label_poreResistance.mouseReleaseEvent = self.label_poreResistance_clicked()

        self.ui.pushButton_MasterBiasElectrodeControlReset.clicked.connect(self.pushButton_master_bias_electrode_control_reset_clicked)
        self.ui.pushButton_resetAllAmplifiers.clicked.connect(self.pushButton_reset_all_amplifiers_clicked)
        self.ui.checkBox_rowPlotDataDisplay.clicked.connect(self.checkBox_rowPlotDataDisplay_clicked)
        self.ui.checkBox_rowPlotPlotsDisplay.clicked.connect(self.checkBox_rowPlotPlotsDisplay_clicked)

        self.ui.masterBiasElectrodeEnableCheckboxGrid = [[0 for row in xrange(5)] for column in xrange(5)]

        self.ui.masterBiasElectrodeEnableCheckboxGrid[0][0] = self.ui.checkBox_column0_row0
        self.ui.masterBiasElectrodeEnableCheckboxGrid[1][0] = self.ui.checkBox_column0_row1
        self.ui.masterBiasElectrodeEnableCheckboxGrid[2][0] = self.ui.checkBox_column0_row2
        self.ui.masterBiasElectrodeEnableCheckboxGrid[3][0] = self.ui.checkBox_column0_row3
        self.ui.masterBiasElectrodeEnableCheckboxGrid[4][0] = self.ui.checkBox_column0_row4
        self.ui.masterBiasElectrodeEnableCheckboxGrid[0][1] = self.ui.checkBox_column1_row0
        self.ui.masterBiasElectrodeEnableCheckboxGrid[1][1] = self.ui.checkBox_column1_row1
        self.ui.masterBiasElectrodeEnableCheckboxGrid[2][1] = self.ui.checkBox_column1_row2
        self.ui.masterBiasElectrodeEnableCheckboxGrid[3][1] = self.ui.checkBox_column1_row3
        self.ui.masterBiasElectrodeEnableCheckboxGrid[4][1] = self.ui.checkBox_column1_row4
        self.ui.masterBiasElectrodeEnableCheckboxGrid[0][2] = self.ui.checkBox_column2_row0
        self.ui.masterBiasElectrodeEnableCheckboxGrid[1][2] = self.ui.checkBox_column2_row1
        self.ui.masterBiasElectrodeEnableCheckboxGrid[2][2] = self.ui.checkBox_column2_row2
        self.ui.masterBiasElectrodeEnableCheckboxGrid[3][2] = self.ui.checkBox_column2_row3
        self.ui.masterBiasElectrodeEnableCheckboxGrid[4][2] = self.ui.checkBox_column2_row4
        self.ui.masterBiasElectrodeEnableCheckboxGrid[0][3] = self.ui.checkBox_column3_row0
        self.ui.masterBiasElectrodeEnableCheckboxGrid[1][3] = self.ui.checkBox_column3_row1
        self.ui.masterBiasElectrodeEnableCheckboxGrid[2][3] = self.ui.checkBox_column3_row2
        self.ui.masterBiasElectrodeEnableCheckboxGrid[3][3] = self.ui.checkBox_column3_row3
        self.ui.masterBiasElectrodeEnableCheckboxGrid[4][3] = self.ui.checkBox_column3_row4
        self.ui.masterBiasElectrodeEnableCheckboxGrid[0][4] = self.ui.checkBox_column4_row0
        self.ui.masterBiasElectrodeEnableCheckboxGrid[1][4] = self.ui.checkBox_column4_row1
        self.ui.masterBiasElectrodeEnableCheckboxGrid[2][4] = self.ui.checkBox_column4_row2
        self.ui.masterBiasElectrodeEnableCheckboxGrid[3][4] = self.ui.checkBox_column4_row3
        self.ui.masterBiasElectrodeEnableCheckboxGrid[4][4] = self.ui.checkBox_column4_row4

        self.ui.checkBox_column0_row0.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=0, column=0))
        self.ui.checkBox_column0_row1.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=1, column=0))
        self.ui.checkBox_column0_row2.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=2, column=0))
        self.ui.checkBox_column0_row3.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=3, column=0))
        self.ui.checkBox_column0_row4.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=4, column=0))
        self.ui.checkBox_column1_row0.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=0, column=1))
        self.ui.checkBox_column1_row1.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=1, column=1))
        self.ui.checkBox_column1_row2.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=2, column=1))
        self.ui.checkBox_column1_row3.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=3, column=1))
        self.ui.checkBox_column1_row4.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=4, column=1))
        self.ui.checkBox_column2_row0.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=0, column=2))
        self.ui.checkBox_column2_row1.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=1, column=2))
        self.ui.checkBox_column2_row2.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=2, column=2))
        self.ui.checkBox_column2_row3.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=3, column=2))
        self.ui.checkBox_column2_row4.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=4, column=2))
        self.ui.checkBox_column3_row0.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=0, column=3))
        self.ui.checkBox_column3_row1.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=1, column=3))
        self.ui.checkBox_column3_row2.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=2, column=3))
        self.ui.checkBox_column3_row3.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=3, column=3))
        self.ui.checkBox_column3_row4.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=4, column=3))
        self.ui.checkBox_column4_row0.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=0, column=4))
        self.ui.checkBox_column4_row1.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=1, column=4))
        self.ui.checkBox_column4_row2.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=2, column=4))
        self.ui.checkBox_column4_row3.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=3, column=4))
        self.ui.checkBox_column4_row4.clicked.connect(lambda: self.checkBox_master_bias_electrode_enable_clicked(row=4, column=4))

        self.ui.label_rowPlotIDCOffsetArray = [self.ui.label_rowPlotColumn0IDCOffset, self.ui.label_rowPlotColumn1IDCOffset, self.ui.label_rowPlotColumn2IDCOffset, self.ui.label_rowPlotColumn3IDCOffset, self.ui.label_rowPlotColumn4IDCOffset]
        self.ui.label_rowPlotIDCRelativeArray = [self.ui.label_rowPlotColumn0IDCRelative, self.ui.label_rowPlotColumn1IDCRelative, self.ui.label_rowPlotColumn2IDCRelative, self.ui.label_rowPlotColumn3IDCRelative, self.ui.label_rowPlotColumn4IDCRelative]
        self.ui.label_rowPlotIDCNetArray = [self.ui.label_rowPlotColumn0IDCNet, self.ui.label_rowPlotColumn1IDCNet, self.ui.label_rowPlotColumn2IDCNet, self.ui.label_rowPlotColumn3IDCNet, self.ui.label_rowPlotColumn4IDCNet]

        self.ui.label_rowPlot10kHzNoiseArray = [self.ui.label_rowPlotColumn010kHzNoise, self.ui.label_rowPlotColumn110kHzNoise, self.ui.label_rowPlotColumn210kHzNoise, self.ui.label_rowPlotColumn310kHzNoise, self.ui.label_rowPlotColumn410kHzNoise]
        self.ui.label_rowPlot100kHzNoiseArray = [self.ui.label_rowPlotColumn0100kHzNoise, self.ui.label_rowPlotColumn1100kHzNoise, self.ui.label_rowPlotColumn2100kHzNoise, self.ui.label_rowPlotColumn3100kHzNoise, self.ui.label_rowPlotColumn4100kHzNoise]
        self.ui.label_rowPlot1MHzNoiseArray = [self.ui.label_rowPlotColumn01MHzNoise, self.ui.label_rowPlotColumn11MHzNoise, self.ui.label_rowPlotColumn21MHzNoise, self.ui.label_rowPlotColumn31MHzNoise, self.ui.label_rowPlotColumn41MHzNoise]
        # self.ui.label_rowPlot10MHzNoiseArray = [self.ui.label_rowPlotColumn010MHzNoise, self.ui.label_rowPlotColumn110MHzNoise, self.ui.label_rowPlotColumn210MHzNoise, self.ui.label_rowPlotColumn310MHzNoise, self.ui.label_rowPlotColumn410MHzNoise]

        self.ui.pushButton_rowPlotIDCSetOffsetArray = [self.ui.pushButton_rowPlotColumn0IDCSetOffset, self.ui.pushButton_rowPlotColumn1IDCSetOffset, self.ui.pushButton_rowPlotColumn2IDCSetOffset, self.ui.pushButton_rowPlotColumn3IDCSetOffset, self.ui.pushButton_rowPlotColumn4IDCSetOffset]
        self.ui.pushButton_rowPlotColumn0IDCSetOffset.clicked.connect(lambda: self.pushButton_rowPlotIDCSetOffset_clicked(column=0))
        self.ui.pushButton_rowPlotColumn1IDCSetOffset.clicked.connect(lambda: self.pushButton_rowPlotIDCSetOffset_clicked(column=1))
        self.ui.pushButton_rowPlotColumn2IDCSetOffset.clicked.connect(lambda: self.pushButton_rowPlotIDCSetOffset_clicked(column=2))
        self.ui.pushButton_rowPlotColumn3IDCSetOffset.clicked.connect(lambda: self.pushButton_rowPlotIDCSetOffset_clicked(column=3))
        self.ui.pushButton_rowPlotColumn4IDCSetOffset.clicked.connect(lambda: self.pushButton_rowPlotIDCSetOffset_clicked(column=4))

        self.ui.pushButton_rowPlotAllAutoScale.clicked.connect(self.pushButton_rowPlotAllAutoScale_clicked)
        self.ui.pushButton_rowPlotAllIDCSetOffset.clicked.connect(self.pushButton_rowPlotAllIDCSetOffset_clicked)

        #######################################################################
        # Initializing Single Channel Plots
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
        # Initializing Multi-Column Channel Plots (Row Plot)
        #######################################################################
        self.ui.rowPlot_style = {'color': '#000', 'font-size': '9pt'}

        self.ui.rowPlot_time_columnArray = [self.ui.graphicsView_time_column0, self.ui.graphicsView_time_column1, self.ui.graphicsView_time_column2, self.ui.graphicsView_time_column3, self.ui.graphicsView_time_column4]
        self.ui.rowPlot_time_columnPlotArray = []

        for i in xrange(len(self.ui.rowPlot_time_columnArray)):
            self.ui.rowPlot_time_columnPlotArray.append(self.ui.rowPlot_time_columnArray[i].plot(numpy.linspace(0, 0.1, 100), numpy.ones(100), pen='b'))
            self.ui.rowPlot_time_columnArray[i].setClipToView(True)
            self.ui.rowPlot_time_columnArray[i].setDownsampling(auto=True, mode='peak')
            self.ui.rowPlot_time_columnArray[i].showGrid(x=True, y=True, alpha=0.7)
            self.ui.rowPlot_time_columnArray[i].setLabel(axis='bottom', text='Time', units='s', **self.ui.rowPlot_style)
            self.ui.rowPlot_time_columnArray[i].setLabel(axis='left', text='I', units='A', **self.ui.rowPlot_style)
            self.ui.rowPlot_time_columnArray[i].disableAutoRange()

        self.ui.rowPlot_frequency_columnArray = [self.ui.graphicsView_frequency_column0, self.ui.graphicsView_frequency_column1, self.ui.graphicsView_frequency_column2, self.ui.graphicsView_frequency_column3, self.ui.graphicsView_frequency_column4]
        self.ui.rowPlot_frequency_columnPlotArray = []

        for i in xrange(len(self.ui.rowPlot_frequency_columnArray)):
            self.ui.rowPlot_frequency_columnPlotArray.append(self.ui.rowPlot_frequency_columnArray[i].plot(numpy.linspace(100, 10e6, 100), numpy.ones(100), pen='b'))
            self.ui.rowPlot_frequency_columnArray[i].setLogMode(x=True, y=True)
            self.ui.rowPlot_frequency_columnArray[i].showGrid(x=True, y=True, alpha=0.7)
            self.ui.rowPlot_frequency_columnArray[i].setLabel(axis='bottom', text='Frequency', units='Hz', **self.ui.rowPlot_style)
            self.ui.rowPlot_frequency_columnArray[i].disableAutoRange()

        self.ui.rowPlot_histogram_columnArray = [self.ui.graphicsView_histogram_column0, self.ui.graphicsView_histogram_column1, self.ui.graphicsView_histogram_column2, self.ui.graphicsView_histogram_column3, self.ui.graphicsView_histogram_column4]
        self.ui.rowPlot_histogram_columnPlotArray = []

        for i in xrange(len(self.ui.rowPlot_histogram_columnArray)):
            self.ui.rowPlot_histogram_columnPlotArray.append(self.ui.rowPlot_histogram_columnArray[i].plot(numpy.linspace(0, 1, 100), numpy.zeros(100), pen='b'))
            self.ui.rowPlot_histogram_columnArray[i].showGrid(x=True, y=True, alpha=0.7)
            self.ui.rowPlot_histogram_columnArray[i].setLabel(axis='bottom', text='Count', **self.ui.rowPlot_style)
            self.ui.rowPlot_histogram_columnArray[i].setLabel(axis='left', text='I', units='A', **self.ui.rowPlot_style)
            self.ui.rowPlot_histogram_columnArray[i].disableAutoRange()

        self.ui.rowPlot_IV_columnArray = [self.ui.graphicsView_IV_column0, self.ui.graphicsView_IV_column1, self.ui.graphicsView_IV_column2, self.ui.graphicsView_IV_column3, self.ui.graphicsView_IV_column4]
        self.ui.rowPlot_IV_columnPlotArray = []

        for i in xrange(len(self.ui.rowPlot_IV_columnArray)):
            self.ui.rowPlot_IV_columnPlotArray.append(self.ui.rowPlot_IV_columnArray[i].plot(numpy.linspace(0, 0.1, 100), numpy.ones(100), pen='b'))
            self.ui.rowPlot_IV_columnArray[i].showGrid(x=True, y=True, alpha=0.7)
            self.ui.rowPlot_IV_columnArray[i].setLabel(axis='bottom', text='Voltage', units='V', **self.ui.rowPlot_style)
            self.ui.rowPlot_IV_columnArray[i].setLabel(axis='left', text='I', units='A', **self.ui.rowPlot_style)
            self.ui.rowPlot_IV_columnArray[i].disableAutoRange()


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

        self.ui.shortcut_autoRange = QtGui.QShortcut('Ctrl+A', self.ui.tabWidget_rowPlot)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_time_column0.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_time_column1.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_time_column2.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_time_column3.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_time_column4.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_frequency_column0.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_frequency_column1.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_frequency_column2.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_frequency_column3.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_frequency_column4.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_histogram_column0.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_histogram_column1.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_histogram_column2.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_histogram_column3.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_histogram_column4.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_IV_column0.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_IV_column1.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_IV_column2.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_IV_column3.autoRange)
        self.ui.shortcut_autoRange.activated.connect(self.ui.graphicsView_IV_column4.autoRange)

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
        self.IVTimer.setInterval(globalConstants.IVTIMESTEP)

        self.ui.action_reset.setChecked(1)
        time.sleep(0.01)
        self.ui.action_reset.setChecked(0)

        #######################################################################
        # Thread creation
        #######################################################################
        self.createThreads()

        #######################################################################
        # Final Initialization
        #######################################################################
        self.updateReferenceelectrodePotential(0)
        self.updateCounterelectrodePotential(0)
        self.setAllAmplifierGains(1)


    def createFPGAObjects(self):
        #######################################################################
        # Create FPGA objects
        #######################################################################
        self.FPGAMasterInstance = FPGA(globalConstants.masterSerial, 'Master')
        self.FPGASlaveInstance = FPGA(globalConstants.slaveSerial, 'Slave')
        try:
            # self.FPGAMasterInstance.initializeDevice('Bitfiles/top_40M222.bit')
            # self.FPGAMasterInstance.initializeDevice('Bitfiles/top_40M22_integratorReset1.bit')
            # self.FPGAMasterInstance.initializeDevice('Bitfiles/top_CNP2V2_master.bit')
            self.FPGAMasterInstance.initializeDevice('Bitfiles/top_CNP2V3_master.bit')
        except:
            print "Failed to program Master FPGA"
        try:
            # self.FPGASlaveInstance.initializeDevice('Bitfiles/top_slave_test.bit')
            # self.FPGASlaveInstance.initializeDevice('Bitfiles/top_CNP2V2_slave.bit')
            self.FPGASlaveInstance.initializeDevice('Bitfiles/top_CNP2V3_slave.bit')
        except:
            print "Failed to program Slave FPGA"

    def checkFPGAStatus(self):
        """Checks the status of both FPGAs. Also sets the text and icon on the GUI to reflect the configuration status of the corresponding FPGA"""
        if self.FPGAMasterInstance.configured:
            # self.ui.label_FPGAMasterStatus_text.setText('Active')
            self.ui.label_FPGAMasterStatus_icon.setPixmap(QtGui.QPixmap('./ui/Icons/icons/status.png'))
        else:
            # self.ui.label_FPGAMasterStatus_text.setText('Inactive')
            self.ui.label_FPGAMasterStatus_icon.setPixmap(QtGui.QPixmap('./ui/Icons/icons/status-busy.png'))
        if self.FPGASlaveInstance.configured:
            # self.ui.label_FPGASlaveStatus_text.setText('Active')
            self.ui.label_FPGASlaveStatus_icon.setPixmap(QtGui.QPixmap('./ui/Icons/icons/status.png'))
        else:
            # self.ui.label_FPGASlaveStatus_text.setText('Inactive')
            self.ui.label_FPGASlaveStatus_icon.setPixmap(QtGui.QPixmap('./ui/Icons/icons/status-busy.png'))

    def createThreads(self):
        #######################################################################
        # Thread instantiation
        #######################################################################
        # self.PSDThread = QtCore.QThread()
        # self.PSDWorkerInstance = workerobjects.PSDWorker(self)
        # self.PSDWorkerInstance.moveToThread(self.PSDThread)
        # # self.PSDWorkerInstance.PSDReady.connect(self.displayLivePreviewSingleChannelPlot)
        # # self.PSDWorkerInstance.PSDReady.connect(self.displayLivePreviewRowPlot)
        # self.PSDWorkerInstance.finished.connect(self.PSDThread.quit)
        # self.PSDWorkerInstance.finished.connect(self.updateNoiseLabels)
        # self.PSDWorkerInstance.finished.connect(self.updateIDCLabels)
        # self.PSDThread.started.connect(self.PSDWorkerInstance.calculatePSD)

        self.PSDMasterThread = QtCore.QThread()
        self.PSDMasterWorkerInstance = workerobjects.PSDWorker(self, self.FPGAMasterInstance.validColumns)
        self.PSDMasterWorkerInstance.moveToThread(self.PSDMasterThread)
        #self.PSDMasterWorkerInstance.PSDReady.connect(self.displayLivePreviewSingleChannelPlot)
        #self.PSDMasterWorkerInstance.PSDReady.connect(self.displayLivePreviewRowPlot)
        self.PSDMasterWorkerInstance.finished.connect(self.PSDMasterThread.quit)
        self.PSDMasterWorkerInstance.finished.connect(self.updateNoiseLabels)
        self.PSDMasterWorkerInstance.finished.connect(self.updateIDCLabels)
        self.PSDMasterThread.started.connect(self.PSDMasterWorkerInstance.calculatePSD)
        
        self.PSDSlaveThread = QtCore.QThread()
        self.PSDSlaveWorkerInstance = workerobjects.PSDWorker(self, self.FPGASlaveInstance.validColumns)
        self.PSDSlaveWorkerInstance.moveToThread(self.PSDSlaveThread)
        #self.PSDSlaveWorkerInstance.PSDReady.connect(self.displayLivePreviewSingleChannelPlot)
        #self.PSDSlaveWorkerInstance.PSDReady.connect(self.displayLivePreviewRowPlot)
        self.PSDSlaveWorkerInstance.finished.connect(self.PSDSlaveThread.quit)
        self.PSDSlaveWorkerInstance.finished.connect(self.updateNoiseLabels)
        self.PSDSlaveWorkerInstance.finished.connect(self.updateIDCLabels)
        self.PSDSlaveThread.started.connect(self.PSDSlaveWorkerInstance.calculatePSD)
        
        self.processRawDataADCMasterThread = QtCore.QThread()
        self.processRawDataADCMasterWorkerInstance = workerobjects.ProcessRawDataWorker(self, self.FPGAMasterInstance.validColumns, self.PSDMasterWorkerInstance, self.PSDMasterThread)
        self.processRawDataADCMasterWorkerInstance.moveToThread(self.processRawDataADCMasterThread)
        self.processRawDataADCMasterWorkerInstance.finished.connect(self.processRawDataADCMasterThread.quit)
        self.processRawDataADCMasterWorkerInstance.dataReady.connect(self.displayLivePreviewSingleChannelPlot)
        self.processRawDataADCMasterWorkerInstance.dataReady.connect(self.displayLivePreviewRowPlot)
        self.processRawDataADCMasterWorkerInstance.startPSDThread.connect(self.PSDMasterThread.start)
        self.processRawDataADCMasterThread.started.connect(self.processRawDataADCMasterWorkerInstance.processRawData)

        self.processRawDataADCSlaveThread = QtCore.QThread()
        self.processRawDataADCSlaveWorkerInstance = workerobjects.ProcessRawDataWorker(self, self.FPGASlaveInstance.validColumns, self.PSDSlaveWorkerInstance, self.PSDSlaveThread)
        self.processRawDataADCSlaveWorkerInstance.moveToThread(self.processRawDataADCSlaveThread)
        self.processRawDataADCSlaveWorkerInstance.finished.connect(self.processRawDataADCSlaveThread.quit)
        self.processRawDataADCSlaveWorkerInstance.dataReady.connect(self.displayLivePreviewSingleChannelPlot)
        self.processRawDataADCSlaveWorkerInstance.dataReady.connect(self.displayLivePreviewRowPlot)
        self.processRawDataADCSlaveWorkerInstance.startPSDThread.connect(self.PSDSlaveThread.start)
        self.processRawDataADCSlaveThread.started.connect(self.processRawDataADCSlaveWorkerInstance.processRawData)

        # self.processRawDataADC2Thread = QtCore.QThread()
        # self.processRawDataADC2WorkerInstance = workerobjects.ProcessRawDataWorker(self, 2)
        # self.processRawDataADC2WorkerInstance.moveToThread(self.processRawDataADC2Thread)
        # self.processRawDataADC2WorkerInstance.finished.connect(self.processRawDataADC2Thread.quit)
        # self.processRawDataADC2WorkerInstance.dataReady.connect(self.displayLivePreviewSingleChannelPlot)
        # self.processRawDataADC2WorkerInstance.dataReady.connect(self.displayLivePreviewRowPlot)
        # self.processRawDataADC2WorkerInstance.startPSDThread.connect(self.PSDThread.start)
        # self.processRawDataADC2Thread.started.connect(self.processRawDataADC2WorkerInstance.processRawData)
        #
        # self.processRawDataADC3Thread = QtCore.QThread()
        # self.processRawDataADC3WorkerInstance = workerobjects.ProcessRawDataWorker(self, 3)
        # self.processRawDataADC3WorkerInstance.moveToThread(self.processRawDataADC3Thread)
        # self.processRawDataADC3WorkerInstance.finished.connect(self.processRawDataADC3Thread.quit)
        # self.processRawDataADC3WorkerInstance.dataReady.connect(self.displayLivePreviewSingleChannelPlot)
        # self.processRawDataADC3WorkerInstance.dataReady.connect(self.displayLivePreviewRowPlot)
        # self.processRawDataADC3WorkerInstance.startPSDThread.connect(self.PSDThread.start)
        # self.processRawDataADC3Thread.started.connect(self.processRawDataADC3WorkerInstance.processRawData)
        #
        # self.processRawDataADC4Thread = QtCore.QThread()
        # self.processRawDataADC4WorkerInstance = workerobjects.ProcessRawDataWorker(self, 4)
        # self.processRawDataADC4WorkerInstance.moveToThread(self.processRawDataADC4Thread)
        # self.processRawDataADC4WorkerInstance.finished.connect(self.processRawDataADC4Thread.quit)
        # self.processRawDataADC4WorkerInstance.dataReady.connect(self.displayLivePreviewSingleChannelPlot)
        # self.processRawDataADC4WorkerInstance.dataReady.connect(self.displayLivePreviewRowPlot)
        # self.processRawDataADC4WorkerInstance.startPSDThread.connect(self.PSDThread.start)
        # self.processRawDataADC4Thread.started.connect(self.processRawDataADC4WorkerInstance.processRawData)

        self.getDataFromFPGAMasterThread = QtCore.QThread()
        self.getDataFromFPGAMasterWorkerInstance = workerobjects.GetDataFromFPGAWorker(self, self.FPGAMasterInstance)
        self.getDataFromFPGAMasterWorkerInstance.moveToThread(self.getDataFromFPGAMasterThread)
        self.getDataFromFPGAMasterWorkerInstance.finished.connect(self.getDataFromFPGAMasterThread.quit)
        self.getDataFromFPGAMasterWorkerInstance.dataReady.connect(self.kickWriteToFileThreads)
        self.getDataFromFPGAMasterThread.started.connect(self.getDataFromFPGAMasterWorkerInstance.getDataFromFPGA)

        self.getDataFromFPGASlaveThread = QtCore.QThread()
        self.getDataFromFPGASlaveWorkerInstance = workerobjects.GetDataFromFPGAWorker(self, self.FPGASlaveInstance)
        self.getDataFromFPGASlaveWorkerInstance.moveToThread(self.getDataFromFPGASlaveThread)
        self.getDataFromFPGASlaveWorkerInstance.finished.connect(self.getDataFromFPGASlaveThread.quit)
        self.getDataFromFPGASlaveWorkerInstance.dataReady.connect(self.kickWriteToFileThreads)
        self.getDataFromFPGASlaveThread.started.connect(self.getDataFromFPGASlaveWorkerInstance.getDataFromFPGA)

        self.writeToMasterLogFileThread = QtCore.QThread()
        self.writeToMasterLogFileWorkerInstance = workerobjects.WriteToLogFileWorker(self, self.FPGAMasterInstance)
        self.writeToMasterLogFileWorkerInstance.moveToThread(self.writeToMasterLogFileThread)
        self.writeToMasterLogFileWorkerInstance.finished.connect(self.writeToMasterLogFileThread.quit)
        self.writeToMasterLogFileThread.started.connect(self.writeToMasterLogFileWorkerInstance.writeToLogFile)

        self.writeToSlaveLogFileThread = QtCore.QThread()
        self.writeToSlaveLogFileWorkerInstance = workerobjects.WriteToLogFileWorker(self, self.FPGASlaveInstance)
        self.writeToSlaveLogFileWorkerInstance.moveToThread(self.writeToSlaveLogFileThread)
        self.writeToSlaveLogFileWorkerInstance.finished.connect(self.writeToSlaveLogFileThread.quit)
        self.writeToSlaveLogFileThread.started.connect(self.writeToSlaveLogFileWorkerInstance.writeToLogFile)

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
        self.processRawDataADCMasterThread.quit()
        self.processRawDataADCMasterThread.wait()
        self.processRawDataADCSlaveThread.quit()
        self.processRawDataADCSlaveThread.wait()
        self.PSDMasterThread.quit()
        self.PSDMasterThread.wait()
        self.PSDSlaveThread.quit()
        self.PSDSlaveThread.wait()
        self.writeToMasterLogFileThread.quit()
        self.writeToMasterLogFileThread.wait()
        self.writeToSlaveLogFileThread.quit()
        self.writeToSlaveLogFileThread.wait()
        event.accept()

    def action_programFPGAs_triggered(self):
        """Creates FPGA objects and the necessary threads. This function is needed only if the FPGAs were not powered on at the time of starting the GUI."""
        self.createFPGAObjects()
        self.createThreads()

    def pushButton_reset_clicked(self): # TODO This makes transactions time-out with master.
        """Checks to see if the reset button has been pressed or not. Resets both FPGAs if the button is pressed"""
        if (self.ui.action_reset.isChecked()):
            reset = 1
        else:
            reset = 0

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Master reset', 0x00, reset*self.resetMask, self.resetMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Master reset'])
        self.getDataFromFPGASlaveWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Slave reset', 0x00, reset*self.resetMask, self.resetMask])
        self.getDataFromFPGASlaveWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Slave reset'])

    def checkBox_ADCenable_clicked(self):
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

    def checkBox_ADC0enable_clicked(self):
        """Enables/Disables ADC0 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC0enable.isChecked()):
            ADC0enableBar = 0
        else:
            ADC0enableBar = 1

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Could not disable ADC 0', 0x00, ADC0enableBar*self.ADC0enableMask, self.ADC0enableMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Could not disable ADC 0'])

    def checkBox_ADC1enable_clicked(self):
        """Enables/Disables ADC1 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC1enable.isChecked()):
            ADC1enableBar = 0
        else:
            ADC1enableBar = 1

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Could not disable ADC 1', 0x00, ADC1enableBar*self.ADC1enableMask, self.ADC1enableMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Could not disable ADC 0'])

    def checkBox_ADC2enable_clicked(self):
        """Enables/Disables ADC2 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC2enable.isChecked()):
            ADC2enableBar = 0
        else:
            ADC2enableBar = 1

        self.getDataFromFPGASlaveWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Could not disable ADC 2', 0x00, ADC2enableBar*self.ADC2enableMask, self.ADC2enableMask])
        self.getDataFromFPGASlaveWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Could not disable ADC 2'])

    def checkBox_ADC3enable_clicked(self):
        """Enables/Disables ADC3 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC3enable.isChecked()):
            ADC3enableBar = 0
        else:
            ADC3enableBar = 1

        self.getDataFromFPGASlaveWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Could not disable ADC 3', 0x00, ADC3enableBar*self.ADC3enableMask, self.ADC3enableMask])
        self.getDataFromFPGASlaveWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Could not disable ADC 3'])

    def checkBox_ADC4enable_clicked(self):
        """Enables/Disables ADC4 depending on the status of its checkbox"""
        if (self.ui.checkBox_ADC4enable.isChecked()):
            ADC4enableBar = 0
        else:
            ADC4enableBar = 1

        self.getDataFromFPGASlaveWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Could not disable ADC 4', 0x00, ADC4enableBar*self.ADC4enableMask, self.ADC4enableMask])
        self.getDataFromFPGASlaveWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Could not disable ADC 4'])

    def checkBox_master_bias_electrode_enable_clicked(self, row, column):
        """Enables/Disables selected channel depending on the status of its checkbox"""
        if (self.ui.masterBiasElectrodeEnableCheckboxGrid[row][column].isChecked()):
            biasEnable = 1
            connectElectrode = 1
        else:
            biasEnable = 0
            connectElectrode = 0
            
        # Update global settings
        self.adcList[column].amplifierList[row].biasEnable = biasEnable
        self.adcList[column].amplifierList[row].connectElectrode = connectElectrode

        shiftFactor = column*5  # Shift config bits by 5x depending on the xth column selected
        amplifierGain = self.amplifierGainMask[column] & ((self.amplifierGainOptions[self.adcList[column].amplifierList[row].gainIndex]) << shiftFactor)

        # Send new bias and electrode settings to selected amplifier
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, row, self.rowSelectMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[column]*biasEnable, self.biasEnableMask[column]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectElectrodeMask[column]*connectElectrode, self.connectElectrodeMask[column]])

        # Set wires so other channel settings do not change on the selected channel
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain, self.amplifierGainMask[column]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.integratorResetMask[row]*self.adcList[column].amplifierList[row].resetIntegrator, self.integratorResetMask[row]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectISRCEXTMask[column]*self.adcList[column].amplifierList[row].connectISRCEXT, self.connectISRCEXTMask[column]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): '])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): ', 0x41, 1])

        # Reset all settings
        shiftFactor = self.columnSelect*5  # Shift config bits by 5x depending on the xth column selected
        amplifierGain = self.amplifierGainMask[self.columnSelect] & ((self.amplifierGainOptions[self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex]) << shiftFactor)

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.rowSelect, self.rowSelectMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable, self.biasEnableMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectElectrodeMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode,self.connectElectrodeMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain, self.amplifierGainMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.integratorResetMask[self.rowSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator, self.integratorResetMask[self.rowSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectISRCEXTMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT, self.connectISRCEXTMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.enableSwitchedCapClockMask*self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock, self.enableSwitchedCapClockMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x00, self.enableTriangleWaveMask*self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave, self.enableTriangleWaveMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): '])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): ', 0x41, 1])

        if ((self.columnSelect == column) and (self.rowSelect == row)):
            self.ui.checkBox_biasEnable.setChecked(biasEnable)
            self.ui.checkBox_connectElectrode.setChecked(connectElectrode) # No signals for setChecked

    def pushButton_master_bias_electrode_control_reset_clicked(self):
        for row in xrange(5):
            for column in xrange(5):
                self.ui.masterBiasElectrodeEnableCheckboxGrid[row][column].setChecked(0)
                self.checkBox_master_bias_electrode_enable_clicked(row, column)

    def pushButton_reset_all_amplifiers_clicked(self):
        for row in xrange(5):
            for column in xrange(5):
                # Reset data structure amplifier settings
                self.adcList[column].amplifierList[row].gainIndex = 1
                self.adcList[column].amplifierList[row].biasEnable = 0
                self.adcList[column].amplifierList[row].connectElectrode = 0
                self.adcList[column].amplifierList[row].enableSWCapClock = 0
                self.adcList[column].amplifierList[row].enableTriangleWave = 0
                self.adcList[column].amplifierList[row].resetIntegrator = 0
                self.adcList[column].amplifierList[row].connectISRCEXT = 0

                # Buffer commands to reset settings for a particular amplifier
                # I do it this way to improve the speed and avoid filling the queue with repeated commands when not necessary
                shiftFactor = column * 5  # Shift config bits by 5x depending on the xth column selected
                amplifierGain = self.amplifierGainMask[column] & ((self.amplifierGainOptions[self.adcList[column].amplifierList[row].gainIndex]) << shiftFactor)
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, row, self.rowSelectMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[column]*self.adcList[column].amplifierList[row].biasEnable, self.biasEnableMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectElectrodeMask[column]*self.adcList[column].amplifierList[row].connectElectrode, self.connectElectrodeMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain, self.amplifierGainMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.integratorResetMask[row]*self.adcList[column].amplifierList[row].resetIntegrator, self.integratorResetMask[row]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectISRCEXTMask[column]*self.adcList[column].amplifierList[row].connectISRCEXT, self.connectISRCEXTMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.enableSwitchedCapClockMask*self.adcList[column].amplifierList[row].enableSWCapClock, self.enableSwitchedCapClockMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x00, self.enableTriangleWaveMask*self.adcList[column].amplifierList[row].enableTriangleWave, self.enableTriangleWaveMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): '])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): ', 0x41, 1])

                # Reset master bias/electrode control checkboxes
                self.ui.masterBiasElectrodeEnableCheckboxGrid[row][column].setChecked(0)
                
            # Reset ADC Control checkboxes without triggering their handlers
            self.ui.comboBox_amplifierGainSelect.blockSignals(True)

            self.ui.comboBox_amplifierGainSelect.setCurrentIndex(self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex)
            self.ui.checkBox_biasEnable.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable)
            self.ui.checkBox_connectElectrode.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode)
            self.ui.checkBox_enableSwitchedCapClock.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock)
            self.ui.checkBox_enableTriangleWave.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave)
            self.ui.checkBox_integratorReset.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator)
            self.ui.checkBox_connectISRCEXT.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT)

            self.ui.comboBox_amplifierGainSelect.blockSignals(False)
            
            # Set current channel settings back to normal
            shiftFactor = self.columnSelect*5  # Shift config bits by 5x depending on the xth column selected
            amplifierGain = self.amplifierGainMask[self.columnSelect] & ((self.amplifierGainOptions[self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex]) << shiftFactor)

            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.rowSelect, self.rowSelectMask])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable, self.biasEnableMask[self.columnSelect]])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectElectrodeMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode,self.connectElectrodeMask[self.columnSelect]])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain, self.amplifierGainMask[self.columnSelect]])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.integratorResetMask[self.rowSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator, self.integratorResetMask[self.rowSelect]])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectISRCEXTMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT, self.connectISRCEXTMask[self.columnSelect]])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.enableSwitchedCapClockMask*self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock, self.enableSwitchedCapClockMask])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x00, self.enableTriangleWaveMask*self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave, self.enableTriangleWaveMask])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): '])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): ', 0x41, 1])

    def checkBox_rowPlotDataDisplay_clicked(self):
        #DO NOT TOUCH THESE FUNCTIONS! SUPER UNSTABLE! GOOD LUCK!
        #centralWidgetWidth = self.ui.centralwidget.width() # Saves a pre-adjustment width size
        self.setMaximumWidth(QWIDGETSIZE_MAX) # Allows the GUI to expand in all directions
        self.setMinimumWidth(0)

        if (self.ui.checkBox_rowPlotDataDisplay.isChecked()):
            self.ui.verticalWidget_rowPlotData.show()
            #while((centralWidgetWidth == self.ui.centralwidget.width) and (mainWindowWidth == self.width)):
                 #pass # Wait until the data structures in Qt update the widget size. I had no success using fixed timers and I don't want to make the application global for sendPostedEvents()
            self.ui.centralwidget.layout().setSizeConstraint(self.ui.centralwidget.layout().SetMinimumSize) # This is necessary. Sets the minimum size setting for the central widget
            self.ui.centralwidget.adjustSize()
            self.adjustSize()
        else:
            self.ui.verticalWidget_rowPlotData.hide()
            #while((centralWidgetWidth == self.ui.centralwidget.width) and (mainWindowWidth == self.width)):
                #pass # Wait until the data structures in Qt update the widget size. I had no success using fixed timers and I don't want to make the application global for sendPostedEvents()
            self.ui.centralwidget.layout().setSizeConstraint(self.ui.centralwidget.layout().SetMinimumSize)
            self.ui.centralwidget.adjustSize()
            self.adjustSize()

        if (not self.ui.verticalWidget_rowPlotPlots.isVisible()):
            self.setFixedWidth(self.width()) # If the row plot option is not visible then lock the horizontal expansion option
        else:
            self.setMinimumWidth(self.width())

    def checkBox_rowPlotPlotsDisplay_clicked(self):
        #DO NOT TOUCH THESE FUNCTIONS! SUPER UNSTABLE! GOOD LUCK!
        #centralWidgetWidth = self.ui.centralwidget.width()
        self.setMaximumWidth(QWIDGETSIZE_MAX) # Allows the GUI to expand in all directions
        self.setMinimumWidth(0)

        if (self.ui.checkBox_rowPlotPlotsDisplay.isChecked()):
            self.ui.verticalWidget_rowPlotPlots.show()
            #while((centralWidgetWidth == self.ui.centralwidget.width) and (mainWindowWidth == self.width)):
                #pass # Wait until the data structures in Qt update the widget size. I had no success using fixed timers and I don't want to make the application global for sendPostedEvents()
            self.ui.centralwidget.layout().setSizeConstraint(self.ui.centralwidget.layout().SetMinimumSize) # This is necessary. Sets the minimum size setting for the central widget
            self.ui.centralwidget.adjustSize()
            self.adjustSize()
            self.setMinimumWidth(self.width())
        else:
            self.ui.verticalWidget_rowPlotPlots.hide()
            #while((centralWidgetWidth == self.ui.centralwidget.width) and (mainWindowWidth == self.width)):
                #pass # Wait until the data structures in Qt update the widget size. I had no success using fixed timers and I don't want to make the application global for sendPostedEvents()
            self.ui.centralwidget.layout().setSizeConstraint(self.ui.centralwidget.layout().SetMinimumSize) # This is necessary. Sets the minimum size setting for the central widget
            self.ui.centralwidget.adjustSize()
            self.adjustSize()
            self.setFixedWidth(self.width())

    def comboBox_rowSelect_activated(self, index):
        """Sets the row selection for the chip (and the daughterboard)"""
        self.rowSelect = self.rowSelectOptions[index]
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.rowSelect, self.rowSelectMask])

        # Reset all settings with new row selection
        # I do it this way to reduce the number of repeated instructions fed to the command handler in the FPGA communication threads
        for column in xrange(5):
            if column != self.columnSelect:
                self.adcList[column].idcOffset = 0
                shiftFactor = column*5  # Shift config bits by 5x depending on the xth column selected
                amplifierGain = self.amplifierGainMask[column] & ((self.amplifierGainOptions[self.adcList[column].amplifierList[self.rowSelect].gainIndex]) << shiftFactor)

                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[column]*self.adcList[column].amplifierList[self.rowSelect].biasEnable, self.biasEnableMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectElectrodeMask[column]*self.adcList[column].amplifierList[self.rowSelect].connectElectrode, self.connectElectrodeMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain, self.amplifierGainMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectISRCEXTMask[column]*self.adcList[column].amplifierList[self.rowSelect].connectISRCEXT, self.connectISRCEXTMask[column]])

        # I have to queue the wire values for my selected row and column to avoid problems with sending a new message that will overwrite the intended settings.
        self.adcList[self.columnSelect].idcOffset = 0
        shiftFactor = self.columnSelect*5  # Shift config bits by 5x depending on the xth column selected
        amplifierGain = self.amplifierGainMask[self.columnSelect] & ((self.amplifierGainOptions[self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex]) << shiftFactor)

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable, self.biasEnableMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectElectrodeMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode,self.connectElectrodeMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain, self.amplifierGainMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.integratorResetMask[self.rowSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator, self.integratorResetMask[self.rowSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectISRCEXTMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT, self.connectISRCEXTMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.enableSwitchedCapClockMask*self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock, self.enableSwitchedCapClockMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x00, self.enableTriangleWaveMask*self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave, self.enableTriangleWaveMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): '])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): ', 0x41, 1])


        # Update settings with programmed settings
        self.ui.comboBox_amplifierGainSelect.blockSignals(True)
        self.ui.lineEdit_amplifierRDCFB.blockSignals(True)

        self.ui.comboBox_amplifierGainSelect.setCurrentIndex(self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex)
        self.ui.checkBox_biasEnable.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable)
        self.ui.checkBox_connectElectrode.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode)
        self.ui.checkBox_enableSwitchedCapClock.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock)
        self.ui.checkBox_enableTriangleWave.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave)
        self.ui.checkBox_integratorReset.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator)
        self.ui.checkBox_connectISRCEXT.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT)
        self.ui.lineEdit_amplifierRDCFB.setText(str(round(self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb / 1e6, 1)))

        if (4 == self.rowSelect):
            self.ui.checkBox_enableSwitchedCapClock.setEnabled(1)
        else:
            self.ui.checkBox_enableSwitchedCapClock.setEnabled(0)

        self.ui.comboBox_amplifierGainSelect.blockSignals(False)
        self.ui.lineEdit_amplifierRDCFB.blockSignals(False)

        self.updateIDCLabels()

    def comboBox_columnSelect_activated(self, index):
        """Sets the column selection for the chip. Clears out data for the other columns when a column switch is initiated"""
        self.columnSelect = index

        # Reset all settings with new column (no new row)
        # I do it this way to reduce the number of repeated instructions fed to the command handler in the FPGA communication threads
        shiftFactor = self.columnSelect*5  # Shift config bits by 5x depending on the xth column selected
        amplifierGain = self.amplifierGainMask[self.columnSelect] & ((self.amplifierGainOptions[self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex]) << shiftFactor)

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to update bias', 0x01, self.biasEnableMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable, self.biasEnableMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to update electrode status', 0x01, self.connectElectrodeMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode,self.connectElectrodeMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to update gain', 0x01, amplifierGain, self.amplifierGainMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to update integrator reset', 0x01, self.integratorResetMask[self.rowSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator, self.integratorResetMask[self.rowSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to update ISRCEXT status', 0x01, self.connectISRCEXTMask[self.columnSelect]*self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT, self.connectISRCEXTMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to update switched cap clock status', 0x02, self.enableSwitchedCapClockMask*self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock, self.enableSwitchedCapClockMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to update triangle wave status', 0x00, self.enableTriangleWaveMask*self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave, self.enableTriangleWaveMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Failed to push wire updates'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Failed to trigger wire', 0x41, 1])

        # Update settings with programmed settings
        self.ui.comboBox_amplifierGainSelect.blockSignals(True)
        self.ui.lineEdit_amplifierRDCFB.blockSignals(True)

        self.ui.comboBox_amplifierGainSelect.setCurrentIndex(self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex)
        self.ui.checkBox_biasEnable.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable)
        self.ui.checkBox_connectElectrode.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode)
        self.ui.checkBox_enableSwitchedCapClock.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock)
        self.ui.checkBox_enableTriangleWave.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave)
        self.ui.checkBox_integratorReset.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator)
        self.ui.checkBox_connectISRCEXT.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT)
        self.ui.lineEdit_amplifierRDCFB.setText(str(round(self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb / 1e6, 1)))

        self.ui.comboBox_amplifierGainSelect.blockSignals(False)
        self.ui.lineEdit_amplifierRDCFB.blockSignals(False)

    def comboBox_amplifierGainSelect_activated(self, index):
        """Sets the amplifier gain (by setting the feedback capacitor) for the selected amplifier"""
        amplifierGainSelect = index
        self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex = index
        shiftFactor = self.columnSelect*5 #Shift config bits by 5x depending on the xth column selected
        amplifierGain = self.amplifierGainMask[self.columnSelect] & ((self.amplifierGainOptions[amplifierGainSelect]) << shiftFactor)

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Changing feedback capacitance value failed', 0x01, amplifierGain, self.amplifierGainMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Changing feedback capacitance value failed'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Changing feedback capacitance value failed', 0x41, 1])


    def checkBox_biasEnable_clicked(self):
        """Determines whether the selected amplifier is enabled or not"""
        if (self.ui.checkBox_biasEnable.isChecked()):
            biasEnable = 1
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable = 1
        else:
            biasEnable = 0
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable = 0

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Enabling bias failed', 0x01, self.biasEnableMask[self.columnSelect]*biasEnable, self.biasEnableMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Enabling bias failed'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Enabling bias failed', 0x41, 1])

    def checkBox_integratorReset_clicked(self):
        """Sets the integrator reset switch (bypassing the feedback capacitor for the integrator). Use while electroplating Ag"""
        if (self.ui.checkBox_integratorReset.isChecked()):
            integratorReset = 1
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator = 1
        else:
            integratorReset = 0
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator = 0
        print "%x" %(self.integratorResetMask[self.rowSelect])

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Integrator reset failed', 0x01, self.integratorResetMask[self.rowSelect]*integratorReset, self.integratorResetMask[self.rowSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Integrator reset failed'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Integrator reset failed', 0x41, 1])

    def checkBox_connectElectrode_clicked(self):
        """Connects the electrode on the surface of the chip to the amplifier"""
        if (self.ui.checkBox_connectElectrode.isChecked()):
            connectElectrode = 1
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode = 1
        else:
            connectElectrode = 0
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode = 0

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Enabling bias failed', 0x01, self.connectElectrodeMask[self.columnSelect]*connectElectrode, self.connectElectrodeMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Enabling bias failed'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Enabling bias failed', 0x41, 1])

    def checkBox_connectISRCEXT_clicked(self):
        """Connects ISRCEXT (which is connected to a header on the daughterboard) to the amplifier"""
        if (self.ui.checkBox_connectISRCEXT.isChecked()):
            connectISRCEXT = 1
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT = 1
        else:
            connectISRCEXT = 0
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT = 0

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Connecting ISRCEXT failed', 0x01, self.connectISRCEXTMask[self.columnSelect]*connectISRCEXT, self.connectISRCEXTMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Connecting ISRCEXT failed'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Connecting ISRCEXT failed', 0x41, 1])

    def action_enableLivePreview_triggered(self):
        """This method is called whenever the corresponding checkbox is clicked. If live preview is enabled, this method creates a worker thread to get data from the FPGA assuming one doesn't exist already"""
        if (self.ui.action_enableLivePreview.isChecked()):
            self.start = time.clock()
            if not (self.getDataFromFPGAMasterThread.isRunning()):
                self.getDataFromFPGAMasterThread.start()
            if not (self.getDataFromFPGASlaveThread.isRunning()):
                self.getDataFromFPGASlaveThread.start()

    def action_enableLogging_triggered(self):
        if (self.ui.action_enableLogging.isChecked()):
            newFilePrefix = str(self.ui.lineEdit_filePrefix.text()) + "_" + str(int(float(self.ui.lineEdit_counterelectrodePotential.text()))) + "mV_" + datetime.date.today().strftime("%Y%m%d") + "_" + time.strftime("%H%M%S")
            self.writeToMasterLogFileWorkerInstance.setFileName(newFilePrefix)
            self.writeToSlaveLogFileWorkerInstance.setFileName(newFilePrefix)
            self.writeToMasterLogFileWorkerInstance.logging = True
            self.writeToSlaveLogFileWorkerInstance.logging = True

    def kickWriteToFileThreads(self, fpgaType):
        """This method is used to check if log data is enabled and when it should be disabled. Depending on the log duration, this method counts the time that has elapsed since logging was enabled and then disables logging automatically"""
        try:
            logDuration = int(float(self.ui.lineEdit_logDuration.text())*1000)
        except:
            logDuration = 1000
        if ('Master' == fpgaType):
            if (True == self.writeToMasterLogFileWorkerInstance.logging):
                self.writeToMasterLogFileWorkerInstance.frameCounter += 1
                if (self.writeToMasterLogFileWorkerInstance.rawData.qsize() >= globalConstants.REFRESHRATE): # qsize returns approximate number of items in queue
                    self.writeToMasterLogFileThread.start() # Write data to disk as soon as there is 1 second's worth to be written
                if (self.writeToMasterLogFileWorkerInstance.frameCounter == globalConstants.REFRESHRATE * logDuration / 1000):
                    self.writeToMasterLogFileWorkerInstance.frameCounter = 0
                    self.writeToMasterLogFileWorkerInstance.logging = False
                    if ((False == self.writeToMasterLogFileWorkerInstance.logging) and (False == self.writeToSlaveLogFileWorkerInstance.logging)):
                        self.ui.action_enableLogging.setChecked(False)
            else:
                # Write any leftover data in memory to disk
                if (self.writeToMasterLogFileWorkerInstance.rawData.qsize() > 0 and not self.writeToMasterLogFileThread.isRunning()):
                    self.writeToMasterLogFileThread.start()
        elif ('Slave' == fpgaType):
            if (True == self.writeToSlaveLogFileWorkerInstance.logging):
                self.writeToSlaveLogFileWorkerInstance.frameCounter += 1
                if (self.writeToSlaveLogFileWorkerInstance.rawData.qsize() >= globalConstants.REFRESHRATE): # qsize returns approximate number of items in queue
                    self.writeToSlaveLogFileThread.start() # Write data to disk as soon as there is 1 second's worth to be written
                if (self.writeToSlaveLogFileWorkerInstance.frameCounter == globalConstants.REFRESHRATE * logDuration / 1000):
                    self.writeToSlaveLogFileWorkerInstance.frameCounter = 0
                    self.writeToSlaveLogFileWorkerInstance.logging = False
                    if ((False == self.writeToMasterLogFileWorkerInstance.logging) and (False == self.writeToSlaveLogFileWorkerInstance.logging)):
                        self.ui.action_enableLogging.setChecked(False)
            else:
                # Write any leftover data in memory to disk
                if (self.writeToSlaveLogFileWorkerInstance.rawData.qsize() > 0 and not self.writeToSlaveLogFileThread.isRunning()):
                    self.writeToSlaveLogFileThread.start()

    def displayLivePreviewSingleChannelPlot(self, columnList):
        """This method plots self.dataToDisplay from the worker thread that gets data from the FPGA and processes it. The data being displayed is already a subsampled version of the full data. PyQtGraph then displays the data in the GUI."""
        self.start = time.clock()
        if self.columnSelect in columnList:
            currentIndex = self.ui.tabWidget_plot.currentIndex()
            if self.ui.action_enableLivePreview.isChecked():
                if (0 == currentIndex):
                    self.ui.graphicsView_time_plot.setData(self.adcList[self.columnSelect].xDataToDisplay, self.adcList[self.columnSelect].yDataToDisplay)
                    if (self.ui.action_addVerticalMarker.isChecked() == True):
                        self.graphicsView_time_updateMarkerText()
                elif (1 == currentIndex and 0 not in self.adcList[self.columnSelect].psd):
                    self.ui.graphicsView_frequency_plot.setData(self.adcList[self.columnSelect].f, self.adcList[self.columnSelect].psd)
                    if (self.ui.action_addVerticalMarker.isChecked() == True):
                        self.graphicsView_frequency_updateMarkerText()
                    if (self.ui.action_addNoiseFit.isChecked() == True and hasattr(self.adcList[self.columnSelect], 'psdFit')):
                        self.ui.graphicsView_frequencyFit_plot.setData(self.adcList[self.columnSelect].f, self.adcList[self.columnSelect].psdFit)
                elif (2 == currentIndex):
                    self.ui.graphicsView_histogram_plot.setData(self.adcList[self.columnSelect].histogramView, self.adcList[self.columnSelect].bins[0:len(self.adcList[self.columnSelect].bins)-1] + (self.adcList[self.columnSelect].bins[1]-self.adcList[self.columnSelect].bins[0])/2)
                elif (3 == currentIndex):
                    if self.adcList[self.columnSelect].ivData_voltage != []:
                        self.ui.graphicsView_IV_plot.setData(self.adcList[self.columnSelect].ivData_voltage, self.adcList[self.columnSelect].ivData_current)
                        self.ui.graphicsView_IV_currentPoint.setData([self.adcList[self.columnSelect].ivData_voltage[-1]], [self.adcList[self.columnSelect].ivData_current[-1]])
            self.stop = time.clock()
            # print "Main GUI thread took", self.stop-self.start, "s"

    def displayLivePreviewRowPlot(self, columnList):
        """This method plots self.dataToDisplay from the worker thread that gets data from the FPGA and processes it. The data being displayed is already a subsampled version of the full data. PyQtGraph then displays the data in the GUI."""
        self.start = time.clock()
        currentIndex = self.ui.tabWidget_rowPlot.currentIndex()
        
        for column in columnList:
            if ((self.ui.action_enableLivePreview.isChecked() and self.ui.checkBox_rowPlotPlotsDisplay.isChecked())):
                if (0 == currentIndex):
                    self.ui.rowPlot_time_columnPlotArray[column].setData(self.adcList[column].xDataToDisplay, self.adcList[column].yDataToDisplay)
                elif (1 == currentIndex and 0 not in self.adcList[column].psd):
                    self.ui.rowPlot_frequency_columnPlotArray[column].setData(self.adcList[column].f, self.adcList[column].psd)
                elif (2 == currentIndex):
                    self.ui.rowPlot_histogram_columnPlotArray[column].setData(self.adcList[column].histogramView, self.adcList[column].bins[0:len(self.adcList[column].bins)-1] + (self.adcList[column].bins[1]-self.adcList[column].bins[0])/2)
                elif (3 == currentIndex):
                    if self.adcList[column].ivData_voltage != []:
                        self.ui.rowPlot_IV_columnPlotArray[column].setData(self.adcList[column].ivData_voltage, self.adcList[column].ivData_current)
                self.stop = time.clock()
        # print "Main GUI thread took", self.stop-self.start, "s"

    def updateReferenceelectrodePotential(self, value=0.0):
        """Updates the reference electrode potential. This is called once at the start of the program to set the reference potential to 900mV and subsequently everytime the counter electrode is set to 0 relative potential."""
        newValue = value + 0.9
        newValue = max(newValue, 0) #Setting lower limit
        newValue = min(newValue, 1.8*255/256) #Setting upper limit (1.8 * 255/256)
        referenceelectrodePotential = int(round(newValue/1.8 * 256)) * 2**9 #2^9 because DAC0ConfigMask starts from bit 9

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to set reference electrode potential', 0x00, referenceelectrodePotential, self.DAC0ConfigMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Failed to set reference electrode potential'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Failed to set reference electrode potential', 0x41, 2])

        print "Set reference electrode potential to", (newValue * 1000), "mV"

    def updateCounterelectrodePotential(self, value=0.0):
        """Updates the counterelectrode potential to the new value defined by value. The counterelectrode potential is determined by a DAC whose inputs are between 0 and 255 and whose analog output can range from 0 to Vdd (1.8V)."""
        newValue = value + 0.9 - 0.00 # Subtract 0.03 V to account for offset
        newValue = max(newValue, 0) #Setting lower limit
        newValue = min(newValue, 1.8*255/256) #Setting upper limit (1.8 * 255/256)
        if (self.ui.action_enableIV.isChecked() is True):
            if (self.IVFirstPoint is True):
                self.IVFirstPoint = False
            else:
                for column in xrange(5):
                    self.adcList[column].ivData_voltage.append(self.IVData_voltageSweep[self.voltageSweepIndex-1])
                    self.adcList[column].ivData_current.append(self.adcList[column].idcRelative)
            self.voltageSweepIndex %= len(self.IVData_voltageSweep)
            newValue = self.IVData_voltageSweep[self.voltageSweepIndex] + 0.9
            self.voltageSweepIndex += 1
            if (self.voltageSweepIndex == 1):
                self.IVCycles += 1
                if (globalConstants.IVNUMBEROFCYCLES != 0):
                    if (self.IVCycles > globalConstants.IVNUMBEROFCYCLES):
                        self.ui.action_enableIV.setChecked(False)
                        self.IVCycles = 0
                else:
                    self.IVCycles = 0

        counterelectrodePotential = int(round(newValue/1.8 * 256)) * 2**17 #2^17 because DAC1ConfigMask starts from bit 17

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to set counter electrode potential', 0x00, counterelectrodePotential, self.DAC1ConfigMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Failed to set counter electrode potential'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Failed to set counter electrode potential', 0x41, 2])

        self.ui.lineEdit_counterelectrodePotential.setText(str(round((newValue - 0.9) * 1000)))

    def updateMBCommonModePotential(self):
        """Updates the motherboard common mode potential. This is called once every second or so to set the potential to the value specified in the options window but action is taken only if the value was changed."""
        if (self.mbCommonModePotential != globalConstants.MBCOMMONMODE):
            self.mbCommonModePotential = globalConstants.MBCOMMONMODE # Nominally should be 1.65 V
            mbCommonModePotential_approximate = int(round(self.mbCommonModePotential/3.3 * 256)) * 2**9 #2^9 because DAC0ConfigMask starts from bit 9

            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to set mb common mode electrode potential', 0x02, mbCommonModePotential_approximate, self.DACMBConfigMask])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Failed to set mb common mode electrode potential'])
            self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Failed to set mb common mode electrode potential', 0x41, 3])

            print "Set motherboard common mode potential to", (self.mbCommonModePotential * 1000), "mV"


    def pushButton_IDCSetOffset_clicked(self):
        """Updates the DC offset current value so that the current being viewed has no DC component left in it"""
        self.adcList[self.columnSelect].idcOffset += self.adcList[self.columnSelect].idcRelative
        #self.ui.label_IDCOffset.setText(str(self.adcList[self.columnSelect].idcOffset * 1e9))
        self.updateIDCLabels()

    def pushButton_rowPlotIDCSetOffset_clicked(self, column):
        """Updates the DC offset current value so that the current being viewed has no DC component left in it"""
        self.adcList[column].idcOffset += self.adcList[column].idcRelative
        #self.ui.label_rowPlotIDCOffsetArray[column].setText(str(self.adcList[column].idcOffset * 1e9))
        self.updateIDCLabels()

    def updateIDCLabels(self):
        """Update labels on the GUI indicating the DC offset current, DC relative current and DC net current"""
        self.ui.label_IDCOffset.setText(str(round(self.adcList[self.columnSelect].idcOffset * 1e9, 1)))
        self.ui.label_IDCRelative.setText(str(round(self.adcList[self.columnSelect].idcRelative * 1e9, 1)))
        self.ui.label_IDCNet.setText(str(round((self.adcList[self.columnSelect].idcOffset + self.adcList[self.columnSelect].idcRelative) * 1e9, 1)))

        if (hasattr(self.ui, 'verticalWidget_rowPlotData') and self.ui.checkBox_rowPlotDataDisplay.isChecked() == True):
            for column in xrange(5):
                self.ui.label_rowPlotIDCOffsetArray[column].setText(str(round(self.adcList[column].idcOffset * 1e9, 1)))
                self.ui.label_rowPlotIDCRelativeArray[column].setText(str(round(self.adcList[column].idcRelative * 1e9, 1)))
                self.ui.label_rowPlotIDCNetArray[column].setText(str(round((self.adcList[column].idcOffset + self.adcList[column].idcRelative) * 1e9, 1)))

    def updateNoiseLabels(self):
        """Update labels on the GUI indicating the integrated noise values at 100 kHz, 1 MHz and 10 MHz bandwidths"""
        self.ui.label_10kHzNoise.setText(str(self.adcList[self.columnSelect].rmsNoise_10kHz))
        self.ui.label_100kHzNoise.setText(str(self.adcList[self.columnSelect].rmsNoise_100kHz))
        self.ui.label_1MHzNoise.setText(str(self.adcList[self.columnSelect].rmsNoise_1MHz))

        if (hasattr(self.ui, 'verticalWidget_rowPlotData') and self.ui.checkBox_rowPlotDataDisplay.isChecked() == True):
            for column in xrange(5):
                self.ui.label_rowPlot10kHzNoiseArray[column].setText(str(self.adcList[column].rmsNoise_10kHz))
                self.ui.label_rowPlot100kHzNoiseArray[column].setText(str(self.adcList[column].rmsNoise_100kHz))
                self.ui.label_rowPlot1MHzNoiseArray[column].setText(str(self.adcList[column].rmsNoise_1MHz))

    def label_bufferUtilizationUpdate(self):
        """Update label on the GUI indicating RAM utilization on the FPGA that is acquiring the data currently being displayed"""
        # if self.FPGAMasterInstance.configured is True:
        #     self.ui.label_FPGAMasterBufferUtilization.setText(str(self.FPGAMasterRAMMemoryUsage)+'/128 MB')
        # if self.FPGASlaveInstance.configured is True:
        #     self.ui.label_FPGASlaveBufferUtilization.setText(str(self.FPGASlaveRAMMemoryUsage)+'/128 MB')
        pass

    def lineEdit_amplifierRDCFB_editingFinished(self):
        """Reads in the new value of RDCFB from the GUI once it has been edited"""
        oldRDCFB = self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb
        try:
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb = eval(str(self.ui.lineEdit_amplifierRDCFB.text()))*1e6
            if self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb == 0:
                self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb = oldRDCFB
        except:
            self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb = 50*1e6
        self.ui.lineEdit_amplifierRDCFB.setText(str(round(self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb/1e6, 1)))
        print self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb


    def checkBox_enableTriangleWave_clicked(self):
        """Changes the pattern on the counterelectrode potential to a triangle wave. The actual code that generates the counterelectrode potential values to create the triangle wave is on the FPGA"""
        if (self.ui.checkBox_enableTriangleWave.isChecked()):
            enableTriangleWave = 1
        else:
            enableTriangleWave = 0

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to enable triangle wave', 0x00, enableTriangleWave*self.enableTriangleWaveMask, self.enableTriangleWaveMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Failed to enable triangle wave'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Failed to enable triangle wave', 0x41, 1])

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

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to enable square wave', 0x00, enableSquareWave*self.enableSquareWaveMask, self.enableSquareWaveMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Failed to enable square wave'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Failed to enable square wave', 0x41, 1])

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
        self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock = enableSwitchedCapClock

        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): Failed to enable square wave', 0x02, enableSwitchedCapClock*self.enableSwitchedCapClockMask, self.enableSwitchedCapClockMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): Failed to enable square wave'])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): Failed to enable square wave', 0x41, 1])

    def action_enableIV_triggered(self):
        """This method activates the IV measurement setup"""
        if not (self.FPGAMasterInstance.configured is True and self.FPGASlaveInstance.configured is True):
            self.ui.action_enableIV.blockSignals(True)
            self.ui.action_enableIV.setChecked(False)
            self.ui.action_enableIV.blockSignals(False)
        if globalConstants.PRESETMODE != 1:
            self.ui.action_enableIV.blockSignals(True)
            self.ui.action_enableIV.setChecked(False)
            self.ui.action_enableIV.blockSignals(False)
        if (self.ui.action_enableIV.isChecked()):
            self.IVFirstPoint = True
            for column in xrange(5):
                self.adcList[column].ivData_voltage = []
                self.adcList[column].ivData_current = []
                self.ui.rowPlot_IV_columnArray[column].clear()
            self.voltageSweepIndex = 0
            self.ui.graphicsView_IV_plot.clear()
            forwardSweep = numpy.arange(globalConstants.IVSTARTVOLTAGE, globalConstants.IVSTOPVOLTAGE, globalConstants.IVVOLTAGESTEP/1000.)
            reverseSweep = numpy.arange(globalConstants.IVSTOPVOLTAGE, globalConstants.IVSTARTVOLTAGE, -globalConstants.IVVOLTAGESTEP/1000.)
            self.IVData_voltageSweep = numpy.hstack(numpy.asarray([forwardSweep, reverseSweep]))
            self.IVTimer.setInterval(globalConstants.IVTIMESTEP)
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
        self.processRawDataADCMasterWorkerInstance.createFilter(self.livePreviewFilterBandwidth)
        self.processRawDataADCSlaveWorkerInstance.createFilter(self.livePreviewFilterBandwidth)

    def action_saveState_triggered(self, configSaveFileSelected = None):
        """Saves a variety of options from the GUI into a cfg file for easy loading later on"""
        if (configSaveFileSelected is None):
            fileSelecter = QtGui.QFileDialog()
            configSaveFileSelected = fileSelecter.getSaveFileName(self, "Choose file", "./Config/", filter="Config files (*.cfg)", selectedFilter="*.cfg")
        try:
            f = open(configSaveFileSelected, 'w')
        except:
            return False
        print configSaveFileSelected
        stateConfig = []

        stateConfig.append({'ADC0Enable': self.ui.checkBox_ADC0enable.isChecked(),
                          'ADC1Enable'  : self.ui.checkBox_ADC1enable.isChecked(),
                          'ADC2Enable'  : self.ui.checkBox_ADC2enable.isChecked(),
                          'ADC3Enable'  : self.ui.checkBox_ADC3enable.isChecked(),
                          'ADC4Enable'  : self.ui.checkBox_ADC4enable.isChecked(),
                          'columnSelect': self.columnSelect,
                          'rowSelect'   : self.rowSelect})
        #json.dump(adcStateConfig, f, indent=0)

        for column in xrange(5):
            for row in xrange(5):
                stateConfig.append({'row': row,
                               'column': column,
                               'amplifierGainSelect': self.adcList[column].amplifierList[row].gainIndex,
                               'biasEnable': self.adcList[column].amplifierList[row].biasEnable,
                               'integratorReset': self.adcList[column].amplifierList[row].resetIntegrator,
                               'connectElectrode': self.adcList[column].amplifierList[row].connectElectrode,
                               'connectISRCEXT': self.adcList[column].amplifierList[row].connectISRCEXT,
                               'enableSWCapClock': self.adcList[column].amplifierList[row].enableSWCapClock,
                               'enableTriangleWave': self.adcList[column].amplifierList[row].enableTriangleWave,
                               'IDCOffset': self.adcList[column].idcOffset,
                               'RDCFB': self.adcList[column].amplifierList[row].rdcfb})

        json.dump(stateConfig, f, indent=0)
        f.close()
        print "Saving state!"

    def action_loadState_triggered(self):
        """Loads a previously saved state (cfg file)"""
        fileSelecter = QtGui.QFileDialog()
        configLoadFileSelected = fileSelecter.getOpenFileName(self, "Choose file", "./Config/", filter="Config files (*.cfg)", selectedFilter="*.cfg")
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

        for i in xrange(len(stateConfig)):
            adc0Enable = stateConfig[i].pop('ADC0Enable', None)
            adc1Enable = stateConfig[i].pop('ADC1Enable', None)
            adc2Enable = stateConfig[i].pop('ADC2Enable', None)
            adc3Enable = stateConfig[i].pop('ADC3Enable', None)
            adc4Enable = stateConfig[i].pop('ADC4Enable', None)
            columnSelect = stateConfig[i].pop('columnSelect', None)
            rowSelect = stateConfig[i].pop('rowSelect', None)

            if (None != adc0Enable):
                self.ui.checkBox_ADC0enable.setChecked(adc0Enable)
                self.ui.checkBox_ADC0enable.click()
            if (None != adc1Enable):
                self.ui.checkBox_ADC1enable.setChecked(adc1Enable)
                self.ui.checkBox_ADC1enable.click()
            if (None != adc2Enable):
                self.ui.checkBox_ADC2enable.setChecked(adc2Enable)
                self.ui.checkBox_ADC2enable.click()
            if (None != adc3Enable):
                self.ui.checkBox_ADC3enable.setChecked(adc3Enable)
                self.ui.checkBox_ADC3enable.click()
            if (None != adc4Enable):
                self.ui.checkBox_ADC4enable.setChecked(adc4Enable)
                self.ui.checkBox_ADC4enable.click()
            if (None != columnSelect):
                self.columnSelect = columnSelect
            if (None != rowSelect):
                self.rowSelect = rowSelect

            # Load column and row information first for indexing the rest
            column = stateConfig[i].pop('column', None)
            row = stateConfig[i].pop('row', None)
            # If the global configuration stateConfig entry is not present the single channel data will be loaded.
            # Otherwise, the columnSelect and rowSelect will be used but eventually overwritten.
            # Works for now

            if ((None != column) and (None != row)):
                self.adcList[column].amplifierList[row].biasEnable = stateConfig[i].pop('biasEnable', 0)
                self.adcList[column].amplifierList[row].connectElectrode = stateConfig[i].pop('connectElectrode', 0)
                self.adcList[column].amplifierList[row].gainIndex = stateConfig[i].pop('amplifierGainSelect', 1)
                self.adcList[column].amplifierList[row].resetIntegrator = stateConfig[i].pop('integratorReset', 0)
                self.adcList[column].amplifierList[row].connectISRCEXT = stateConfig[i].pop('connectISRCEXT', 0)
                self.adcList[column].amplifierList[row].enableSWCapClock = stateConfig[i].pop('enableSWCapClock', 0)
                self.adcList[column].amplifierList[row].enableTriangleWave = stateConfig[i].pop('enableTriangleWave', 0)
                self.adcList[column].idcOffset = stateConfig[i].pop('IDCOffset', 0) # TODO This is being overwritten over and over again. Leave until we implement all 25 channels
                self.adcList[column].amplifierList[row].rdcfb = stateConfig[i].pop('RDCFB', 50*1e6)

                shiftFactor = column * 5  # Shift config bits by 5x depending on the xth column selected
                amplifierGain = self.amplifierGainMask[column] & ((self.amplifierGainOptions[self.adcList[column].amplifierList[row].gainIndex]) << shiftFactor)
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, row, self.rowSelectMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[column] * self.adcList[column].amplifierList[row].biasEnable, self.biasEnableMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectElectrodeMask[column] * self.adcList[column].amplifierList[row].connectElectrode, self.connectElectrodeMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain, self.amplifierGainMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.integratorResetMask[row] * self.adcList[column].amplifierList[row].resetIntegrator, self.integratorResetMask[row]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.connectISRCEXTMask[column] * self.adcList[column].amplifierList[row].connectISRCEXT, self.connectISRCEXTMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.enableSwitchedCapClockMask * self.adcList[column].amplifierList[row].enableSWCapClock, self.enableSwitchedCapClockMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x00, self.enableTriangleWaveMask * self.adcList[column].amplifierList[row].enableTriangleWave, self.enableTriangleWaveMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): '])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): ', 0x41, 1])

        # I have to queue the wire values for my selected row and column to avoid problems with sending a new message that will overwrite the intended settings.
        shiftFactor = self.columnSelect * 5  # Shift config bits by 5x depending on the xth column selected
        amplifierGain = self.amplifierGainMask[self.columnSelect] & ((self.amplifierGainOptions[self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex]) << shiftFactor)
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, self.rowSelect, self.rowSelectMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[self.columnSelect] * self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable, self.biasEnableMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01,self.connectElectrodeMask[self.columnSelect] * self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode, self.connectElectrodeMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain,self.amplifierGainMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01,self.integratorResetMask[self.rowSelect] * self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator, self.integratorResetMask[self.rowSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01,self.connectISRCEXTMask[self.columnSelect] * self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT, self.connectISRCEXTMask[self.columnSelect]])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02,self.enableSwitchedCapClockMask * self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock, self.enableSwitchedCapClockMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x00,self.enableTriangleWaveMask * self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave, self.enableTriangleWaveMask])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): '])
        self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): ', 0x41, 1])

        # Update settings with programmed settings
        self.ui.comboBox_amplifierGainSelect.blockSignals(True)
        self.ui.lineEdit_amplifierRDCFB.blockSignals(True)

        self.ui.comboBox_amplifierGainSelect.setCurrentIndex(self.adcList[self.columnSelect].amplifierList[self.rowSelect].gainIndex)
        self.ui.checkBox_biasEnable.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].biasEnable)
        self.ui.checkBox_connectElectrode.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectElectrode)
        self.ui.checkBox_enableSwitchedCapClock.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableSWCapClock)
        self.ui.checkBox_enableTriangleWave.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].enableTriangleWave)
        self.ui.checkBox_integratorReset.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].resetIntegrator)
        self.ui.checkBox_connectISRCEXT.setChecked(self.adcList[self.columnSelect].amplifierList[self.rowSelect].connectISRCEXT)
        self.ui.lineEdit_amplifierRDCFB.setText(str(round(self.adcList[self.columnSelect].amplifierList[self.rowSelect].rdcfb / 1e6, 1)))

        self.ui.comboBox_amplifierGainSelect.blockSignals(False)
        self.ui.lineEdit_amplifierRDCFB.blockSignals(False)

    def action_compressData_triggered(self):
        self.compressDataWindow0 = CompressData()
        self.compressDataWindow0.show()

    def action_options_triggered(self):
        """Creates an options window"""
        self.optionsWindow0 = OptionsWindow()
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
           In the time view, label indicate the amplitude and time value at the marker.
           In the frequency view, label indicate the integrated noise and frequency value at the marker"""
        if (self.ui.action_addVerticalMarker.isChecked()):
            self.ui.graphicsView_time.marker = pyqtgraph.InfiniteLine(0, angle=90, movable=True, pen='r')
            self.ui.graphicsView_time.marker.x = 0
            self.ui.graphicsView_time.marker.sigPositionChanged.connect(self.graphicsView_time_updateMarkerText)
            self.ui.graphicsView_time.markerValue = pyqtgraph.TextItem('X=0\nY=0', anchor = (0,0), color='r')
            self.ui.graphicsView_time.markerValue.setPos(self.ui.graphicsView_time.marker.x, numpy.max(self.adcList[self.columnSelect].yDataToDisplay))
            self.ui.graphicsView_time.addItem(self.ui.graphicsView_time.marker)
            self.ui.graphicsView_time.addItem(self.ui.graphicsView_time.markerValue)

            self.ui.graphicsView_frequency.marker = pyqtgraph.InfiniteLine(3, angle=90, movable=True, pen='r')
            self.ui.graphicsView_frequency.marker.x = 3
            self.ui.graphicsView_frequency.marker.sigPositionChanged.connect(self.graphicsView_frequency_updateMarkerText)
            self.ui.graphicsView_frequency.markerValue = pyqtgraph.TextItem('X=100\nY=0', anchor = (0,0), color='r')
            self.ui.graphicsView_frequency.markerValue.setPos(self.ui.graphicsView_frequency.marker.x, numpy.log10(numpy.max(self.adcList[self.columnSelect].psd)))
            self.ui.graphicsView_frequency.addItem(self.ui.graphicsView_frequency.marker)
            self.ui.graphicsView_frequency.addItem(self.ui.graphicsView_frequency.markerValue)
        else:
            self.ui.graphicsView_time.removeItem(self.ui.graphicsView_time.marker)
            self.ui.graphicsView_time.removeItem(self.ui.graphicsView_time.markerValue)
            self.ui.graphicsView_frequency.removeItem(self.ui.graphicsView_frequency.marker)
            self.ui.graphicsView_frequency.removeItem(self.ui.graphicsView_frequency.markerValue)

    def graphicsView_time_updateMarkerText(self):
        """Updates the labels whenever the marker is moved in the time view"""
        self.ui.graphicsView_time.marker.x = float(self.ui.graphicsView_time.marker.value())
        try:
            self.ui.graphicsView_time.marker.y = self.adcList[self.columnSelect].yDataToDisplay[int(self.ui.graphicsView_time.marker.x/globalConstants.SUBSAMPLINGFACTOR*globalConstants.ADCSAMPLINGRATE)] # TODO I think this is already subsampled
        except:
            self.ui.graphicsView_time.marker.y = 0
        self.ui.graphicsView_time.markerValue.setPlainText('X=' + '%.3E s' % self.ui.graphicsView_time.marker.x + '\nY=%.3E A' % self.ui.graphicsView_time.marker.y)
        ymax = self.ui.graphicsView_time.getViewBox().viewRange()[1][1]
        ymin = self.ui.graphicsView_time.getViewBox().viewRange()[1][0]
        yMarkerText = (ymax-ymin)*0.95+ymin
        self.ui.graphicsView_time.markerValue.setPos(self.ui.graphicsView_time.marker.x, yMarkerText) # Some percentage to the top of the screen without causing resizing issues
        #self.ui.graphicsView_time.markerValue.setPos(self.ui.graphicsView_time.getViewBox().viewRange()[0][1], self.ui.graphicsView_time.getViewBox().viewRange()[1][1])
        # print self.ui.graphicsView_time.marker.value()

    def graphicsView_frequency_updateMarkerText(self):
        """Updates the labels whenever the marker is moved in the frequency view"""
        self.ui.graphicsView_frequency.marker.x = 10**float(self.ui.graphicsView_frequency.marker.value())
        try:
            self.ui.graphicsView_frequency.marker.y = self.adcList[self.columnSelect].rmsNoise[numpy.abs(self.adcList[self.columnSelect].f-self.ui.graphicsView_frequency.marker.x).argmin()]
        except:
            self.ui.graphicsView_frequency.marker.y = 0
        self.ui.graphicsView_frequency.markerValue.setPlainText('X=' + '%.3E Hz' % self.ui.graphicsView_frequency.marker.x + u'\n√(∫Y∆X)=%.3E Arms' % self.ui.graphicsView_frequency.marker.y)
        ymax = self.ui.graphicsView_frequency.getViewBox().viewRange()[1][1]
        ymin = self.ui.graphicsView_frequency.getViewBox().viewRange()[1][0]
        yMarkerText = ((ymax-ymin)*0.90+ymin)
        self.ui.graphicsView_frequency.markerValue.setPos(self.ui.graphicsView_frequency.marker.value(), yMarkerText)
        #self.ui.graphicsView_frequency.markerValue.setPos(self.ui.graphicsView_frequency.marker.x, yMarkerText)
        # print self.ui.graphicsView_time.marker.value()

    def addNoiseFit_triggered(self):
        """Adds a fit to the noise PSD. The data is fit to a*f^-1 + b + c*f + d*f^2"""
        if (self.ui.action_addNoiseFit.isChecked() == True):
            self.ui.graphicsView_frequencyFit_plot = self.ui.graphicsView_frequency.plot(numpy.linspace(100, 10e6, 100), numpy.ones(100), pen='k', width=2)
            self.displayLivePreviewSingleChannelPlot([self.columnSelect])
        else:
            self.ui.graphicsView_frequency.removeItem(self.ui.graphicsView_frequencyFit_plot)

    # def label_poreResistance_clicked(self):
        # self.temp = ~self.temp
        # if (True == self.temp):
            # self.ui.label_poreResistance.setText(u"MΩ")
        # else:
            # self.ui.label_poreResistance.setText("nS")

    def setAllAmplifierGains(self, gainIndex):
        for row in xrange(5):
            for column in xrange(5):
                # Reset data structure amplifier settings
                self.adcList[column].amplifierList[row].gainIndex = gainIndex

                # Buffer commands to setup amplifier with new gain
                # I do it this way to improve the speed and avoid filling the queue with repeated commands when not necessary
                shiftFactor = column * 5  # Shift config bits by 5x depending on the xth column selected
                amplifierGain = self.amplifierGainMask[column] & ((self.amplifierGainOptions[self.adcList[column].amplifierList[row].gainIndex]) << shiftFactor)

                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02, row, self.rowSelectMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, self.biasEnableMask[column]*self.adcList[column].amplifierList[row].biasEnable, self.biasEnableMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01,self.connectElectrodeMask[column]*self.adcList[column].amplifierList[row].connectElectrode, self.connectElectrodeMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01, amplifierGain, self.amplifierGainMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01,self.integratorResetMask[row]*self.adcList[column].amplifierList[row].resetIntegrator, self.integratorResetMask[row]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x01,self.connectISRCEXTMask[column]*self.adcList[column].amplifierList[row].connectISRCEXT, self.connectISRCEXTMask[column]])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x02,self.enableSwitchedCapClockMask*self.adcList[column].amplifierList[row].enableSWCapClock, self.enableSwitchedCapClockMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDQUEUEWIRE, 'Error (CMDQUEUEWIRE): ', 0x00,self.enableTriangleWaveMask*self.adcList[column].amplifierList[row].enableTriangleWave, self.enableTriangleWaveMask])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDUPDATEWIRE, 'Error (CMDUPDATEWIRE): '])
                self.getDataFromFPGAMasterWorkerInstance.commandQueue.put([globalConstants.CMDTRIGGERWIRE, 'Error (CMDTRIGGERWIRE): ', 0x41, 1])

                # Set gain index combobox without triggering new message
                self.ui.comboBox_amplifierGainSelect.blockSignals(True)
                self.ui.comboBox_amplifierGainSelect.setCurrentIndex(gainIndex)
                self.ui.comboBox_amplifierGainSelect.blockSignals(False)

    def pushButton_rowPlotAllAutoScale_clicked(self):
        currentIndex = self.ui.tabWidget_rowPlot.currentIndex()

        for column in xrange(5):
            if ((self.ui.action_enableLivePreview.isChecked() and self.ui.checkBox_rowPlotPlotsDisplay.isChecked())):
                if (0 == currentIndex):
                    self.ui.rowPlot_time_columnArray[column].getPlotItem().autoBtnClicked()
                elif (1 == currentIndex and 0 not in self.adcList[column].psd):
                    self.ui.rowPlot_frequency_columnArray[column].getPlotItem().autoBtnClicked()
                elif (2 == currentIndex):
                    self.ui.rowPlot_histogram_columnArray[column].getPlotItem().autoBtnClicked()
                elif (3 == currentIndex and self.adcList[column].ivData_voltage != []):
                    self.ui.rowPlot_IV_columnArray[column].getPlotItem().autoBtnClicked()

    def pushButton_rowPlotAllIDCSetOffset_clicked(self):
        """Updates the DC offset current value so that the current being viewed has no DC component left in it"""
        for column in xrange(5):
            self.adcList[column].idcOffset += self.adcList[column].idcRelative
            #self.ui.label_rowPlotIDCOffsetArray[column].setText(str(self.adcList[column].idcOffset * 1e9))
        self.updateIDCLabels()