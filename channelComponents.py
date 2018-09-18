# -*- coding: utf-8 -*-

class AMPLIFIER:
    gainIndex = None
    biasEnable = None
    connectElectrode = None
    enableSWCapClock = None
    triangleWave = None
    resetIntegrator = None
    connectISRCEXT = None
    rdcfb = None

    def __init__(self):
        self.gainIndex = 0
        self.biasEnable = 0
        self.connectElectrode = 0
        self.enableSWCapClock = 0
        self.enableTriangleWave = 0
        self.resetIntegrator = 0
        self.connectISRCEXT = 0
        self.rdcfb = 50e6

class ADC:
    adcData = None
    xDataToDisplay = None
    yDataToDisplay = None
    ivData_voltage = None
    ivData_current = None
    idcOffset = None
    idcRelative = None
    poreResistance = None
    rmsNoise = None
    rmsNoise_100kHz = None
    rmsNoise_1MHz = None
    rmsNoise_10MHz = None
    f = None
    psd = None
    psdFit = None
    histogramView = None
    bins = None
    #amplifierList = [] # Using this creates a global scope list for some reason.

    def __init__(self):
        self.adcData = []
        self.xDataToDisplay = []
        self.yDataToDisplay = []
        self.ivData_voltage = []
        self.ivData_current = []
        self.idcOffset = 0
        self.idcRelative = 0
        self.poreResistance = 0
        self.rmsNoise = 0
        self.rmsNoise_100kHz = 0
        self.rmsNoise_1MHz = 0
        self.rmsNoise_10MHz = 0
        self.f = []
        self.psd = 0
        self.psdFit = 0
        self.histogramView = None
        self.bins = None
        self.amplifierList = []
        for i in xrange(5):
            self.amplifierList.append(AMPLIFIER())
