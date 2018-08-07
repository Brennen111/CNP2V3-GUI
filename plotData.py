import sys
from PyQt4 import QtGui
import time
import numpy

import random

from plotWindow import Ui_MainWindow
from optionsWindow import optionsWindow

class Constants(object):
    def __init__(self, value):
        self.__value = value

    def getValue(self):
        return self.__value

    def setValue(self, value):
        self.__value = value

ADCBITS = Constants(12)
SUBSAMPLINGFACTOR = Constants(10)
# REFRESHRATE = 10 # in frames per second
REFRESHRATE = Constants(10)
AAFILTERGAIN = Constants((51+620)/620*1.8*.51)
# ADCSAMPLINGRATE = 156250000/4 # in samples per second
ADCSAMPLINGRATE = Constants(4000000)
FRAMEDURATION = Constants(1000/REFRESHRATE.getValue())
# FRAMELENGTH = (((ADCSAMPLINGRATE*FRAMEDURATION/1000)*4)/4000000 + 1)*4000000 # Multiplied by 4 because of the specific FPGA data packing implementation
FRAMELENGTH = Constants((((ADCSAMPLINGRATE.getValue()*FRAMEDURATION.getValue()/1000)*4)/4000000 + 0)*4000000)
# BLOCKLENGTH = 1024 # While transferring data from the FPGA, the transaction is broken up into blocks of this length (in bytes)
BLOCKLENGTH = Constants(256)
PRESETMODE = Constants(0)
SQUAREWAVEAMPLITUDE = Constants(0.9)

dictOfConstants = {'ADCBITS':ADCBITS, 'SUBSAMPLINGFACTOR': SUBSAMPLINGFACTOR, 'REFRESHRATE': REFRESHRATE, 'AAFILTERGAIN': AAFILTERGAIN, 'ADCSAMPLINGRATE': ADCSAMPLINGRATE, 'FRAMEDURATION': FRAMEDURATION, 'FRAMELENGTH': FRAMELENGTH, 'BLOCKLENGTH': BLOCKLENGTH, 'SQUAREWAVEAMPLITUDE': SQUAREWAVEAMPLITUDE, 'PRESETMODE': PRESETMODE}

class PlotWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_loadData.clicked.connect(self.pushButton_loadData_clicked)
        self.ui.comboBox_columnSelect.activated.connect(self.unpackData)
        
        self.f = None

        self.ui.action_options.triggered.connect(self.action_options_triggered)
        self.ui.action_quit.triggered.connect(self.close)
        # self.figure = Figure(figsize=(1000,800), dpi=100)
        # self.canvas = FigureCanvas(self.figure)
        # self.toolbar = NavigationToolbar(self.ui.matplotlibPlot, self)
        # self.plotButton = QtGui.QPushButton('Plot')
        # self.plotButton.clicked.connect(self.ui.graphicsView.compute_initial_figure)
        # #
        # layout = QtGui.QVBoxLayout()
        # layout.addWidget(self.toolbar)
        # layout.addWidget(self.canvas)
        # layout.addWidget(self.ui.graphicsView)
        # layout.addWidget(self.plotButton)
        # self.setLayout(layout)
        
    def pushButton_loadData_clicked(self):
        fileSelecter = QtGui.QFileDialog()
        configLoadFileSelected = fileSelecter.getOpenFileName(self, "Choose file", "./", filter="Hex files (*.hex)", selectedFilter="*.hex")
        try:
            self.f = open(configLoadFileSelected, 'r')
        except:
            pass
        self.unpackData(self.ui.comboBox_columnSelect.currentIndex())
        
    def unpackData(self, index):
        if (None == self.f):
            print "Please pick a file to open first"
            return False
        if (index in self.FPGAMasterInstance.validColumns):
            self.rawDataUnpacked = numpy.fromfile(self.f, dtype='uint32')
            if (0 == index):
                self.ADCData = numpy.bitwise_and(self.rawDataUnpacked, 0xfff)
            elif (1 == index):
                self.ADCData = numpy.bitwise_and(self.rawDataUnpacked, 0xfff000) >> 12
        elif (index in self.FPGASlaveInstance.validColumns):
            self.rawDataUnpacked = numpy.fromfile(self.f, dtype='uint64')
            if (2 == index):
                ADCDataCompressed = numpy.bitwise_and(self.rawData64Bit[0::2], 0xfffffffff)
                self.ADCData = numpy.zeros((3*numpy.size(ADCDataCompressed),))
                self.ADCData[0::3] = numpy.bitwise_and(ADCDataCompressed, 0xfff)
                self.ADCData[1::3] = numpy.bitwise_and(ADCDataCompressed, 0xfff000) >> 12
                self.ADCData[2::3] = numpy.bitwise_and(ADCDataCompressed, 0xfff000000) >> 24
            elif (3 == index):
                ADCDataCompressed = numpy.bitwise_and(self.rawData64Bit[0::2], 0xfffffff000000000) >> 36
                ADCDataCompressedMSB = numpy.bitwise_and(self.rawData64Bit[1::2], 0xff)
                self.ADCData = numpy.zeros((3*numpy.size(ADCDataCompressed),))
                self.ADCData[0::3] = numpy.bitwise_and(ADCDataCompressed, 0xfff)
                self.ADCData[1::3] = numpy.bitwise_and(ADCDataCompressed, 0xfff000) >> 12
                self.ADCData[2::3] = (numpy.bitwise_and(ADCDataCompressed, 0xf000000) >> 24) + ADCDataCompressedMSB*16
            elif (4 == index):
                ADCDataCompressed = numpy.bitwise_and(self.rawData64Bit[1::2], 0x00000fffffffff00) >> 8
                self.ADCData = numpy.zeros((3*numpy.size(ADCDataCompressed),))
                self.ADCData[0::3] = numpy.bitwise_and(ADCDataCompressed, 0xfff)
                self.ADCData[1::3] = numpy.bitwise_and(ADCDataCompressed, 0xfff000) >> 12
                self.ADCData[2::3] = numpy.bitwise_and(ADCDataCompressed, 0xfff000000) >> 24
        self.dataToDisplay = (self.ADCData)[0::dictOfConstants['SUBSAMPLINGFACTOR'].getValue()]*1.0
        self.dataToDisplay[self.dataToDisplay >= 2**(dictOfConstants['ADCBITS'].getValue()-1)] -= 2**(dictOfConstants['ADCBITS'].getValue())
        self.dataToDisplay -= numpy.mean(self.dataToDisplay)
        self.dataToDisplay *= 1.0/2**(dictOfConstants['ADCBITS'].getValue()-1)
        dictOfConstants['FRAMEDURATION'].setValue(len(self.dataToDisplay)*1.0/dictOfConstants['ADCSAMPLINGRATE'].getValue())
        self.displayData()
        
    def displayData(self):
        self.ui.graphicsView_time.clear()
        # print dictOfConstants['FRAMELENGTH'].getValue()
        self.ui.graphicsView_time.plot(numpy.linspace(0, dictOfConstants['FRAMEDURATION'].getValue()*1.0/1000, len(self.dataToDisplay)), self.dataToDisplay, pen='b')
        # self.ui.graphicsView_time.setDownsampling(5, mode='subsample')
        self.ui.graphicsView_time.showGrid(x=True, y=True, alpha=0.7)
        self.ui.graphicsView_time.setLabel(axis='bottom', text='Time (s)')
        self.ui.graphicsView_time.setLabel(axis='left', text='I (nA)')
        self.ui.graphicsView_time.disableAutoRange()

    def action_options_triggered(self):
        self.optionsWindow0 = optionsWindow(dictOfConstants)
        self.optionsWindow0.show()