# -*- coding: utf-8 -*-
import os
from PyQt4 import QtCore
import numpy, scipy.signal, scipy.optimize
import time, datetime
import copy
import pywt, pyqtgraph
import Queue
import numba

class PSDWorker(QtCore.QObject):
    # finished = QtCore.pyqtSignal(numpy.float64, numpy.float64)
    finished = QtCore.pyqtSignal()
    # PSDReady = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    PSDReady = QtCore.pyqtSignal()
    histogramReady = QtCore.pyqtSignal()
    #Signal for progress bar
    progress = QtCore.pyqtSignal(int, str)

    def __init__(self, parentWindow, dictOfConstants):
        super(PSDWorker, self).__init__()
        # self.ADCData = numpy.zeros(dictOfConstants['FRAMELENGTH']/4)
        self.parentWindow = parentWindow
        self.dictOfConstants = dictOfConstants
        self.needsScaling = False

    @numba.jit
    def numba_scale(self, array, bits=12):
        for i in xrange(len(array)):
            if array[i] >= 2**(bits-1):
                array[i] -= 2**bits
            array[i] /= 2**(bits-1)

    def calculatePSD(self):
        self.start = time.clock()
        # self.ADCData = window.ADCData
        if (self.needsScaling):
            self.numba_scale(self.ADCData, self.dictOfConstants['ADCBITS'])
            # self.ADCData[self.ADCData >= 2**(self.dictOfConstants['ADCBITS']-1)] -= 2**(self.dictOfConstants['ADCBITS'])
            # self.ADCData /= 2**(self.dictOfConstants['ADCBITS']-1)
            self.ADCData -= numpy.mean(self.ADCData)
        # if (True == self.parentWindow.ui.checkBox_enableSquareWave.isChecked()):
            # self.calculateDCResistance()
        # if (window.columnSelect in [0, 3]):
            # self.ADCData *= 16.0/5
        self.parentWindow.histogramView, self.parentWindow.bins = numpy.histogram(self.ADCData, bins=64)
        self.parentWindow.bins /= (self.dictOfConstants['AAFILTERGAIN']*self.parentWindow.RDCFB)
        self.parentWindow.bins -= self.parentWindow.IDCOffset
        self.histogramReady.emit()
        self.progress.emit(2, 'Calculating PSD')
        #### Begin PSD calculation
        # f, Pxx = scipy.signal.periodogram(self.ADCData, dictOfConstants['ADCSAMPLINGRATE'], nfft=2**19)
        f, Pxx = scipy.signal.welch(self.ADCData, self.dictOfConstants['ADCSAMPLINGRATE'], nperseg=2**13)
        #### End PSD calculation

        #### Begin FFT calculation
        # NFFT = 2**19
        # ADCSAMPLINGRATE = self.dictOfConstants['ADCSAMPLINGRATE']
        # ADCDataFFT = numpy.fft.fft(self.ADCData, NFFT)
        # ADCDataFFT = ADCDataFFT[1:NFFT/2]
        # f = ADCSAMPLINGRATE/2*numpy.linspace(0, 1, NFFT/2)
        # f = f[1:len(f)]
        # Pxx = 2.0/(ADCSAMPLINGRATE*NFFT)*numpy.abs(numpy.square(ADCDataFFT))
        #### End FFT calculation

        # f_100Hz = numpy.argmin(numpy.abs(f - 1e2))
        Pxx = Pxx[f > 1e2]
        f = f[f>1e2]
        # PxxFitCoefficients = numpy.polynomial.polynomial.polyfit(f[f<6e6], Pxx[f<6e6]*f[f<6e6], 3)
        # f, Pxx = f[f_100Hz:len(f)], Pxx[f_100Hz:len(Pxx)]
        self.progress.emit(2, 'Preparing PSD data for plotting')
        f_100kHz = numpy.where(f > 1e5)[0][0]
        f_1MHz = numpy.where(f > 1e6)[0][0]
        # f_10MHz = numpy.where(f > 10e6)[0][0]
        f_10MHz = 0
        if (self.needsScaling == False and self.parentWindow.ui.checkBox_enableLivePreviewFilter.isChecked() == True):
            f_PSDStopFrequency = numpy.where(f > self.parentWindow.livePreviewFilterBandwidth)[0][0]
        else:
            # f_PSDStopFrequency = numpy.where(f > 10e6)[0][0]
            f_PSDStopFrequency = numpy.where(f > 1e6)[0][0]
        logIndices = numpy.unique(numpy.asarray(numpy.logspace(0, numpy.log10(f_PSDStopFrequency), f_PSDStopFrequency/self.dictOfConstants['SUBSAMPLINGFACTOR']), dtype=numpy.int32))
        self.parentWindow.f = f[logIndices-1]
        if (hasattr(self.parentWindow.ui, 'checkBox_frequencyResponse') and self.parentWindow.ui.checkBox_frequencyResponse.isChecked() == True):
            self.parentWindow.PSD = numpy.divide(Pxx[logIndices-1], f[logIndices-1]**2)
        else:
            self.parentWindow.PSD = Pxx[logIndices-1]
        if (self.parentWindow.ui.action_addNoiseFit.isChecked() == True):
            self.parentWindow.PSDFit = self.createFit(self.parentWindow.f, self.parentWindow.PSD, 1e6)
        # self.PSDReady.emit(fToDisplay, PxxToDisplay)
        self.PSDReady.emit()
        self.progress.emit(1, 'Finishing up')

        self.RMSNoise = numpy.sqrt(scipy.integrate.cumtrapz(Pxx, f, initial=0))/self.dictOfConstants['AAFILTERGAIN']/self.parentWindow.RDCFB
        self.parentWindow.RMSNoise = self.RMSNoise[logIndices-1]

        self.parentWindow.RMSNoise_100kHz = numpy.round(self.RMSNoise[f_100kHz] * 10**12, 1)
        self.parentWindow.RMSNoise_1MHz = numpy.round(self.RMSNoise[f_1MHz] * 10**12, 1)
        self.parentWindow.RMSNoise_10MHz = numpy.round(self.RMSNoise[f_10MHz-1] * 10**12, 1)
        self.stop = time.clock()
        # print "Calculate PSD thread took", self.stop-self.start, "s"
        # self.finished.emit(numpy.round(RMSNoise_100kHz * 10**12, 1), numpy.round(RMSNoise_1MHz * 10**12, 1))
        self.finished.emit()

    def calculateDCResistance(self):
        self.ADCDataRMS = numpy.sqrt(numpy.mean(numpy.power(self.ADCData, 2)))
        self.poreResistance = self.dictOfConstants['SQUAREWAVEAMPLITUDE']/self.ADCDataRMS*self.dictOfConstants['AAFILTERGAIN']*self.parentWindow.RDCFB
        self.parentWindow.ui.label_poreResistance.setText(str(numpy.round(self.poreResistance/1e6, 1)) + u"MΩ")

    def createFit(self, fFit, PSDFit, maxFitFrequency = 6e6):
        fFitNew = fFit[fFit < maxFitFrequency]
        PSDFitNew = PSDFit[fFit < maxFitFrequency]
        fitCoefficients = numpy.polynomial.polynomial.polyfit(fFitNew, PSDFitNew * fFitNew, 3, w = 1/(fFitNew * PSDFitNew)) #Fit PSD*f to 3rd order and then divide by f to get the 1/f term also
        print numpy.sqrt(fitCoefficients[3])/(2*3.14*3.15e-9*self.parentWindow.RDCFB*self.dictOfConstants['AAFILTERGAIN'])
        return numpy.divide(numpy.polynomial.polynomial.polyval(fFit, fitCoefficients), fFit)


class GetDataFromFPGAWorker(QtCore.QObject):
    """Worker module that inherits from QObject. Eventually, this gets moved on to a thread that inherits from QThread."""
    finished = QtCore.pyqtSignal()
    dataReady = QtCore.pyqtSignal()

    def __init__(self, parentWindow, dictOfConstants, FPGAInstance):
        super(GetDataFromFPGAWorker, self).__init__()
        self.parentWindow = parentWindow
        self.FPGAInstance = FPGAInstance
        if self.FPGAInstance is not None:
            self.FPGAType = self.FPGAInstance.type
            self.validColumns = self.FPGAInstance.validColumns
            self.processRawDataThreadOptions = {'Master': [self.parentWindow.processRawDataADC0Thread, self.parentWindow.processRawDataADC1Thread], 'Slave': [self.parentWindow.processRawDataADC2Thread, self.parentWindow.processRawDataADC3Thread, self.parentWindow.processRawDataADC4Thread]}
            self.processRawDataThreadArray = self.processRawDataThreadOptions[self.FPGAType]
            self.processRawDataADCWorkerInstanceOptions = {'Master': [self.parentWindow.processRawDataADC0WorkerInstance, self.parentWindow.processRawDataADC1WorkerInstance], 'Slave': [self.parentWindow.processRawDataADC2WorkerInstance, self.parentWindow.processRawDataADC3WorkerInstance, self.parentWindow.processRawDataADC4WorkerInstance]}
            self.processRawDataADCWorkerInstanceArray = self.processRawDataADCWorkerInstanceOptions[self.FPGAType]
        self.dictOfConstants = dictOfConstants

    def getDataFromFPGA(self):
        """Gets data from the FPGA and logs it if the corresponding option has been enabled. Calls processRawData once a chunk of data has been obtained. Loops infinitely."""
        while (self.FPGAInstance.configured):
            if self.FPGAInstance.UpdateWire is True:
                self.FPGAInstance.UpdateWire = False
                self.FPGAInstance.xem.UpdateWireIns()
            if self.FPGAInstance.ActivateTrigger is True:
                self.FPGAInstance.ActivateTrigger = False
                self.FPGAInstance.xem.ActivateTriggerIn(self.FPGAInstance.TriggerEndpoint, self.FPGAInstance.TriggerBitmask)
            if ('Master' == self.FPGAType):
                rawData = bytearray(self.dictOfConstants['FRAMELENGTH_MASTER'])
            elif ('Slave' == self.FPGAType):
                rawData = bytearray(self.dictOfConstants['FRAMELENGTH_SLAVE'])
            self.start = time.clock()
            errorReturn = self.FPGAInstance.xem.ReadFromBlockPipeOut(0xA0, self.dictOfConstants['BLOCKLENGTH'], rawData)
            if (self.FPGAInstance.xem.Timeout == errorReturn):
                print "Transaction timed out on", self.FPGAType, "FPGA"
            if (self.FPGAInstance.xem.Failed == errorReturn):
                print "Transaction failed on", self.FPGAType, "FPGA"
                self.FPGAInstance.powered = False #Change power status to off if code breaks out of the while loop
                self.FPGAInstance.configured = False #Change configuration status to unconfigured if code breaks out of the while loop
            if (self.parentWindow.columnSelect in self.validColumns):
                if (self.parentWindow.ui.action_enableLogging.isChecked()):
                    self.parentWindow.writeToLogFileWorkerInstance.rawData.put(rawData)
                    # self.parentWindow.writeToLogFileThread.start()
            self.dataReady.emit()

            for i in xrange(len(self.processRawDataThreadArray)):
                if not self.processRawDataThreadArray[i].isRunning():
                    self.processRawDataADCWorkerInstanceArray[i].rawData = rawData
                    self.processRawDataThreadArray[i].start()
                else:
                    pass

            self.updateWireOuts()
            self.stop = time.clock()
            # if ('Slave' == self.FPGAType):
                # print "Get data from FPGA thread took", self.stop-self.start, "s"
            # self.processRawData(rawDataUnpacked)
        self.finished.emit()

    def updateWireOuts(self):
        self.FPGAInstance.xem.UpdateWireOuts()
        RAMMemoryUsage = self.FPGAInstance.xem.GetWireOutValue(0x20)
        RAMMemoryUsage = numpy.round(RAMMemoryUsage*1.0/2**20, 1)
        if 'Master' == self.FPGAType:
            self.parentWindow.FPGAMasterRAMMemoryUsage = RAMMemoryUsage
        elif 'Slave' == self.FPGAType:
            self.parentWindow.FPGASlaveRAMMemoryUsage = RAMMemoryUsage
        return

class ProcessRawDataWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    # dataReady = QtCore.pyqtSignal(numpy.ndarray)
    dataReady = QtCore.pyqtSignal(int)
    startPSDThread = QtCore.pyqtSignal()
    #Signals for the progress bar
    progress = QtCore.pyqtSignal(int, str)

    def __init__(self, parentWindow, dictOfConstants, validColumn):
        super(ProcessRawDataWorker, self).__init__()
        self.dictOfConstants = dictOfConstants
        self.skipPoints = 0
        self.createFilter(100e3)
        self.parentWindow = parentWindow
        self.validColumn = validColumn
        # self.rawData = bytearray(self.dictOfConstants['FRAMELENGTH'])
        self.rawDataUnpacked = 0
        self.compressedData = False
        self.numbaTotal = 0
        self.numbaCount = 0
        self.unpackTotal = 0
        self.unpackCount = 0
        self.filterTotal = 0
        self.filterCount = 0
        self.printTotal = 0
        self.printCount = 0
        self.processTimeTotal = 0
        self.processTimeCount = 0
        self.time01Total = 0
        self.time12Total = 0
        self.time23Total = 0
        self.time34Total = 0
        self.time45Total = 0
        self.time56Total = 0
        self.time67Total = 0
        self.time78Total = 0
        self.time89Total = 0
        self.time910Total = 0
        self.time1011Total = 0
        self.time01Count = 0
        self.time12Count = 0
        self.time23Count = 0
        self.time34Count = 0
        self.time45Count = 0
        self.time56Count = 0
        self.time67Count = 0
        self.time78Count = 0
        self.time89Count = 0
        self.time910Count = 0
        self.time1011Count = 0

    @numba.jit(parallel=True, fastmath=True)
    def numba_scale(self, array, bits=12):
        for i in xrange(len(array)):
            if array[i] >= 2**(bits-1):
                array[i] -= 2**bits
            array[i] /= 2**(bits-1)

    @numba.jit
    def numba_garrote(self, array, threshold):
        for i in xrange(len(array)):
            if numpy.abs(array[i]) < threshold:
                array[i] = 0
            else:
                array[i] -= threshold**2/array[i]

    def processRawData(self):
        """Processes the raw data. The raw data is a 32 bit number that contains {8'h00, 12'hADC1Data, 12'hADC0DATA}. This method unpacks the data and then subsamples it and corrects for the boosting and anti-aliasing filter gain and DC offset."""
        #self.start = time.clock()
        # self.rawDataUnpacked = numpy.frombuffer(self.rawData, dtype='uint32')
        # ADCData = {0: numpy.bitwise_and(self.rawDataUnpacked, 0xfff),\
                # 1: (numpy.bitwise_and(self.rawDataUnpacked, 0xfff000))>>12,\
                # 3: numpy.bitwise_and(self.rawDataUnpacked, 0xfff)}
        # Switched from dictionary to if else implementation because of timing issues while displaying data
        time0 = time.clock()
        if self.compressedData == False:
            #preUnpackData = time.clock()
            ADCData = self.unpackData().astype(numpy.float32)
            #postUnpackData = time.clock()
            #self.unpackTotal += postUnpackData-preUnpackData
            #self.unpackCount += 1
            #if (0 == self.validColumn):
                #print "Debug master unpack average: time = ", self.unpackTotal/self.unpackCount

        else:
            ADCData = numpy.frombuffer(self.rawData, dtype='int16').astype(numpy.float32)
        time1 = time.clock()
        self.numba_scale(ADCData, self.dictOfConstants['ADCBITS'])

        if (self.parentWindow.ui.checkBox_enableLivePreviewFilter.isChecked()):
            # ADCData2[ADCData2 >= 2**(self.dictOfConstants['ADCBITS']-1)] -= 2**(self.dictOfConstants['ADCBITS'])
            # ADCData2 /= 2**(self.dictOfConstants['ADCBITS']-1)

            #preNumba = time.clock()
            time2 = time.clock()
            #postNumba = time.clock()
            ADCData = scipy.signal.lfilter(self.b, self.a, ADCData)
            time3 = time.clock()
            #postFilter = time.clock()
            #self.filterTotal += postFilter-postNumba
            #self.filterCount += 1
            #self.numbaTotal += postNumba-preNumba
            #self.numbaCount += 1

            #if (0 == self.validColumn):
                #print "Debug master numba_scale average: time = ", self.numbaTotal/self.numbaCount
                #print "Debug master filter average: time = ", self.filterTotal/self.filterCount

            #ADCData2[:-1] += numpy.diff(ADCData2)/(2*numpy.pi*2.5e6/self.dictOfConstants['ADCSAMPLINGRATE'])

            # if (self.parentWindow.ui.checkBox_enableWaveletDenoising.isChecked()):
            #     self.motherWavelet = str(self.parentWindow.ui.lineEdit_motherWavelet.text())
            #     maxLength = int(2**(numpy.floor(numpy.log2(len(ADCData)))))
            #     ADCData = ADCData2[:maxLength]
            #     waveletCoefficients = pywt.swt(ADCData, self.motherWavelet, level=7)# level=int(numpy.floor(numpy.log2(len(ADCData)))))
            #     waveletCoefficients = map(list, waveletCoefficients)
            #     for i in range(len(waveletCoefficients)):
            #         detail = waveletCoefficients[i][1]
            #         sigma = numpy.median(numpy.abs(detail))/0.6745
            #         threshold = sigma*numpy.sqrt(2*numpy.log10(len(detail)))/numpy.log10(7 - i + 1)
            #         self.numba_garrote(waveletCoefficients[i][1], threshold)
            #     ADCData = pywt.iswt(waveletCoefficients, self.motherWavelet)
            # totalNoise = numpy.std(ADCData2[len(ADCData2)/2:])
            # print totalNoise/self.parentWindow.RDCFB/self.dictOfConstants['AAFILTERGAIN']
            # tags = ADCData < -5*totalNoise
            # print totalNoise/self.parentWindow.RDCFB, numpy.sum(numpy.bitwise_and(numpy.bitwise_and(tags[:-3], tags[1:-2]), numpy.bitwise_and(tags[2:-1], tags[3:])))

            ADCData = ADCData[self.skipPoints:]
            time4 = time.clock()
            dataToDisplay = ADCData[::self.dictOfConstants['SUBSAMPLINGFACTOR']]
            time5 = time.clock()

            if (hasattr(self.parentWindow, 'analyzeDataWorkerInstance')):
                self.parentWindow.analyzeDataWorkerInstance.rawData = ADCData[::self.skipPoints/4]/self.parentWindow.RDCFB/self.dictOfConstants['AAFILTERGAIN'] - self.parentWindow.IDCOffset
                self.parentWindow.analyzeDataWorkerInstance.effectiveSamplingRate = self.dictOfConstants['ADCSAMPLINGRATE']/self.skipPoints*4
            time6 = time.clock()

        else:
            #ADCData[:-1] += numpy.diff(ADCData)/(2*numpy.pi*2.5e6/self.dictOfConstants['ADCSAMPLINGRATE'])
            # if (self.parentWindow.ui.checkBox_enableWaveletDenoising.isChecked()):
            #     self.motherWavelet = str(self.parentWindow.ui.lineEdit_motherWavelet.text())
            #     level = 8
            #     maxLength = int(numpy.floor((len(ADCData))/2**level))*2**level
            #     ADCData = ADCData[:maxLength]
            #     waveletCoefficients = pywt.swt(ADCData, self.motherWavelet, level=level)# level=int(numpy.floor(numpy.log2(len(ADCData)))))
            #     print "SWT done"
            #     waveletCoefficients = map(list, waveletCoefficients)
            #     print "Conversion to list done"
            #     for i in range(len(waveletCoefficients)):
            #         detail = waveletCoefficients[i][1]
            #         sigma = numpy.median(numpy.abs(detail))/0.6745
            #         threshold = sigma*numpy.sqrt(2*numpy.log10(len(detail)))/numpy.log10(level - i + 2)
            #         self.numba_garrote(waveletCoefficients[i][1], threshold)
            #         print "Level " + str(i+1) + " done"
            #     print "Beginning ISWT"
            #     ADCData = pywt.iswt(waveletCoefficients, self.motherWavelet)
            #     print "ISWT complete"
            #     if (hasattr(self.parentWindow, 'analyzeDataWorkerInstance')):
            #         self.parentWindow.analyzeDataWorkerInstance.rawData = ADCData[:]/self.parentWindow.RDCFB/self.dictOfConstants['AAFILTERGAIN'] - self.parentWindow.IDCOffset
            dataToDisplay = ADCData[::self.dictOfConstants['SUBSAMPLINGFACTOR']]
            # dataToDisplay[dataToDisplay >= 2**(self.dictOfConstants['ADCBITS']-1)] -= 2**(self.dictOfConstants['ADCBITS'])
            # dataToDisplay /= 2**(self.dictOfConstants['ADCBITS']-1)
            # self.numba_scale(dataToDisplay, self.dictOfConstants['ADCBITS'])

        time7 = time.clock()
        dataToDisplay *= 1.0/self.parentWindow.RDCFB/self.dictOfConstants['AAFILTERGAIN'] #Prefixes (like nano or pico) are handled automatically by PyQtGraph
        time8 = time.clock()
        self.parentWindow.IDCRelative = numpy.mean(dataToDisplay) - self.parentWindow.IDCOffset
        time9 = time.clock()
        dataToDisplay -= self.parentWindow.IDCOffset
        time10 = time.clock()
        self.parentWindow.updateIDCLabels()
        time11 = time.clock()
        self.progress.emit(1, 'Finished calculating data to display')

        if (hasattr(self.parentWindow.ui, 'action_enableLivePreview') and self.parentWindow.ui.action_enableLivePreview.isChecked() == False):
            pass
        else:
            if (self.parentWindow.columnSelect == self.validColumn):
                self.parentWindow.dataToDisplay = dataToDisplay
            self.parentWindow.adcList[self.validColumn].yDataToDisplay = dataToDisplay
            self.parentWindow.adcList[self.validColumn].xDataToDisplay = numpy.linspace(0, len(dataToDisplay) * self.dictOfConstants['SUBSAMPLINGFACTOR'] * 1.0 / self.dictOfConstants['ADCSAMPLINGRATE'], len(dataToDisplay))

        if (not self.parentWindow.PSDThread.isRunning() and (self.parentWindow.columnSelect == self.validColumn)):
            self.parentWindow.PSDWorkerInstance.ADCData = ADCData #ADCData is sent as float32
            self.parentWindow.PSDThread.start()
            self.progress.emit(1, 'Calculating histogram')

        if (-1 == self.validColumn and self.parentWindow.ui.checkBox_enableLivePreviewFilter.isChecked()):
            self.time01Total += time1 - time0
            self.time12Total += time2 - time1
            self.time23Total += time3 - time2
            self.time34Total += time4 - time3
            self.time45Total += time5 - time4
            self.time56Total += time6 - time5
            self.time67Total += time7 - time6
            self.time78Total += time8 - time7
            self.time89Total += time9 - time8
            self.time910Total += time10 - time9
            self.time1011Total += time11 - time10
            self.time01Count += 1
            self.time12Count += 1
            self.time23Count += 1
            self.time34Count += 1
            self.time45Count += 1
            self.time56Count += 1
            self.time67Count += 1
            self.time78Count += 1
            self.time89Count += 1
            self.time910Count += 1
            self.time1011Count += 1
            print "Debug 0 time0-1 average ", self.time01Total/self.time01Count
            print "Debug 0 time1-2 average ", self.time12Total/self.time12Count
            print "Debug 0 time2-3 average ", self.time23Total/self.time23Count
            print "Debug 0 time3-4 average ", self.time34Total/self.time34Count
            print "Debug 0 time4-5 average ", self.time45Total/self.time45Count
            print "Debug 0 time5-6 average ", self.time56Total/self.time56Count
            print "Debug 0 time6-7 average ", self.time67Total/self.time67Count
            print "Debug 0 time7-8 average ", self.time78Total/self.time78Count
            print "Debug 0 time8-9 average ", self.time89Total/self.time89Count
            print "Debug 0 time9-10 average ", self.time910Total/self.time910Count
            print "Debug 0 time10-11 average ", self.time1011Total/self.time1011Count

        self.stop = time.clock()
        #if (self.parentWindow.ui.checkBox_enableLivePreviewFilter.isChecked()):
            #if (0 == self.validColumn):
                #self.processTimeTotal += self.stop-self.start
                #self.processTimeCount += 1
                #print "Debug master process average: time = ", self.processTimeTotal/self.processTimeCount
        # print "Processing the data took", self.stop-self.start, "s"
        self.dataReady.emit(self.validColumn)
        self.finished.emit()

    def createFilter(self, livePreviewFilterBandwidth):
        """livePreviewFilterBandwidth is displayLivePreview used to construct an angular frequency such that Fs/2 = 1. Filter is only approximately correct when
        filtering frequency is < Fs/4"""
        self.livePreviewFilterBandwidth = livePreviewFilterBandwidth
        # Skip first few points of filtered data to avoid edge effects due to filtering
        self.skipPoints = int(numpy.ceil(self.dictOfConstants['ADCSAMPLINGRATE']/self.livePreviewFilterBandwidth))
        self.b, self.a = scipy.signal.bessel(4, self.livePreviewFilterBandwidth/self.dictOfConstants['ADCSAMPLINGRATE']*2, 'low')

    def compressData(self):
        return self.unpackData().astype(numpy.int16)

    @numba.jit
    def numba_bitwise_and(self, array, mask, shift, resulttype='uint32'):
        """Numba implementation of AND function with masking and shifting ability"""
        result = numpy.empty_like(array, dtype=resulttype)
        for i in xrange(len(array)):
            result[i] = numpy.bitwise_and(array[i], mask) >> shift
        return result

    def unpackData(self):
        """Returns unpacked ADCData for the selected column"""
        self.progress.emit(1, 'Unpacking data')

        if (0 == self.validColumn):
            self.rawDataUnpacked = numpy.frombuffer(self.rawData, dtype='uint32')
            #ADCData = numpy.empty_like(self.rawDataUnpacked, dtype='uint32')
            ADCData = self.numba_bitwise_and(self.rawDataUnpacked, numpy.uint32(0xfff), 0)

        elif (1 == self.validColumn):
            self.rawDataUnpacked = numpy.frombuffer(self.rawData, dtype='uint32')
            #ADCData = numpy.empty_like(self.rawDataUnpacked, dtype='uint32')
            ADCData = self.numba_bitwise_and(self.rawDataUnpacked, numpy.uint32(0xfff000), 12)

        elif (2 == self.validColumn):
            self.rawData64Bit = numpy.frombuffer(self.rawData, dtype='uint64')
            ADCDataCompressed = self.numba_bitwise_and(self.rawData64Bit[0::2], numpy.uint64(0xfffffffff), 0, 'uint64')
            ADCData = numpy.empty((3 * numpy.size(ADCDataCompressed),), dtype='uint32')
            ADCData[0::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff), 0)
            ADCData[1::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff000), 12)
            ADCData[2::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff000000), 24)

        elif (3 == self.validColumn):
            self.rawData64Bit = numpy.frombuffer(self.rawData, dtype='uint64')
            ADCDataCompressed = self.numba_bitwise_and(self.rawData64Bit[0::2], numpy.uint64(0xfffffff000000000), 36, 'uint64')
            ADCDataCompressedMSB = self.numba_bitwise_and(self.rawData64Bit[1::2], numpy.uint64(0xff), 0, 'uint64')
            ADCData = numpy.empty((3 * numpy.size(ADCDataCompressed),), dtype='uint32')
            ADCData[0::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff), 0)
            ADCData[1::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff000), 12)
            ADCData[2::3] = (self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xf000000), 24)) + (ADCDataCompressedMSB * 16)

        elif (4 == self.validColumn):
            self.rawData64Bit = numpy.frombuffer(self.rawData, dtype='uint64')
            ADCDataCompressed = self.numba_bitwise_and(self.rawData64Bit[1::2], numpy.uint64(0x00000fffffffff00), 8, 'uint64')
            ADCData = numpy.empty((3 * numpy.size(ADCDataCompressed),), dtype='uint32')
            ADCData[0::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff), 0)
            ADCData[1::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff000), 12)
            ADCData[2::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff000000), 24)

        else:
            pass

        self.progress.emit(1, 'Processing data for plotting')
        return ADCData

class WriteToLogFileWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, parentWindow, dictOfConstants):
        super(WriteToLogFileWorker, self).__init__()
        self.rawData = Queue.Queue()
        self.f = 0
        self.parentWindow = parentWindow
        self.dictOfConstants = dictOfConstants
        self.defaultDirectory = "./Logfiles" + "/" + datetime.date.today().strftime("%Y%m%d") + "/"

    def writeToLogFile(self):
        start = time.clock()
        if not os.path.exists(self.defaultDirectory):
            os.makedirs(self.defaultDirectory)
        self.fileName = self.defaultDirectory + self.parentWindow.dataFileSelected + "_" + str(int(float(self.parentWindow.ui.lineEdit_counterelectrodePotential.text()))) + "mV_" + datetime.date.today().strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + ".hex"
        self.f = open(self.fileName, 'a+b')
        # While logging is enabled, write in 1 second bursts. Finish writing everything that is in memory when logging is disabled
        if (self.parentWindow.ui.action_enableLogging.isChecked()):
            for i in range(self.dictOfConstants['REFRESHRATE']):
                self.f.write(self.rawData.get())
        else:
            for i in range(self.rawData.qsize()):
                self.f.write(self.rawData.get())
        self.f.close()
        self.configFileName = self.fileName[0:len(self.fileName) - 3] + "cfg"
        self.parentWindow.action_saveState_triggered(self.configFileName)
        stop = time.clock()
        print "Writing data to disk took", stop-start, "s"
        # if ((stop - start)*1000 > self.dictOfConstants['FRAMEDURATION']):
        #     print "Probably missed writing some data because it took too long to write the last frame"
        self.finished.emit()

class AnalyzeDataWorker(QtCore.QObject):
    """This class provides methods that can detect event edges and perform CUSUM based fitting on events"""
    progress = QtCore.pyqtSignal(int, str)
    edgeDetectionFinished = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self, parentWindow, dictOfConstants):
        super(AnalyzeDataWorker, self).__init__()
        self.parentWindow = parentWindow
        self.dictOfConstants = dictOfConstants
        self.rawData = 0

    def analyzeData(self, detectEdges=True):
        """This method determines the baseline and threshold values to be used for event detection"""
        # self.generateBaselineStartIndex = 222000e-6*self.effectiveSamplingRate
        # self.generateBaselineStopIndex = 232000e-6*self.effectiveSamplingRate
        if self.parentWindow.ui.checkBox_enableLivePreviewFilter.isChecked() is False:
            self.effectiveSamplingRate = self.dictOfConstants['ADCSAMPLINGRATE']
        self.generateBaselineStartIndex = int(238900e-6*self.effectiveSamplingRate)
        self.generateBaselineStopIndex = int(239500e-6*self.effectiveSamplingRate)
        print self.generateBaselineStartIndex, self.generateBaselineStopIndex
        if (self.parentWindow.baseline is not None):
            self.baseline = self.parentWindow.baseline
        else:
            self.baseline = numpy.mean(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex])
            self.parentWindow.baseline = self.baseline
        f, Pxx = scipy.signal.welch(self.rawData, self.dictOfConstants['ADCSAMPLINGRATE'], nperseg=2**13)
        Pxx = Pxx[f > 100]
        f = f[f > 100]
        self.parentWindow.analyzeF, self.parentWindow.analyzePxx = f, Pxx
        self.sigma = numpy.std(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex])
        print self.sigma
        self.parentWindow.sigma = self.sigma
        if (self.parentWindow.threshold is not None):
            self.threshold = self.parentWindow.threshold
        else:
            if (hasattr(self.parentWindow, 'numberOfSigmas')):
                self.numberOfSigmas = self.parentWindow.numberOfSigmas
                self.threshold = self.baseline - self.numberOfSigmas * self.sigma
            else:
                self.threshold = self.baseline - 5*self.sigma
            print numpy.std(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex])
            self.parentWindow.threshold = self.threshold
        try:
            self.minimumEventDuration = eval(str(self.parentWindow.ui.lineEdit_minimumEventDuration.text()))*1e-6
            self.minimumEventSamples = numpy.maximum(self.effectiveSamplingRate*self.minimumEventDuration, 1)
        except:
            self.minimumEventDuration = 1e-6
            self.minimumEventSamples = numpy.maximum(self.effectiveSamplingRate*self.minimumEventDuration, 1)
        try:
            self.maximumEventDuration = eval(str(self.parentWindow.ui.lineEdit_maximumEventDuration.text()))*1e-6
            self.maximumEventSamples = self.effectiveSamplingRate*self.maximumEventDuration
        except:
            self.maximumEventDuration = 1e-3
            self.maximumEventSamples = self.effectiveSamplingRate*self.maximumEventDuration
        if (detectEdges == True):
            self.detectEdges()

    def detectEdges(self):
        """This method determines event edges based on a fixed thresholding scheme"""
        self.eventIndex = (numpy.where(self.rawData < self.threshold)[0]).astype(numpy.int32)
        self.transitions = numpy.diff(self.eventIndex)
        self.edgeBeginIndex = numpy.insert(self.transitions, 0, 2)
        self.edgeEndIndex = numpy.insert(self.transitions, -1, 2)
        self.edgeBegin = self.eventIndex[numpy.where(self.edgeBeginIndex > 1)]
        self.edgeEnd = self.eventIndex[numpy.where(self.edgeEndIndex > 1)]

        self.numberOfEvents = len(self.edgeBegin)
        self.limit = self.baseline - 3*numpy.std(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex]) #Set the upper limit to 1 sigma away from the mean
        # self.limit = self.threshold + 4*self.sigma #This should put the upper limit at 1 sigma closer to baseline than the threshold
        for i in range(self.numberOfEvents):
            eb = self.edgeBegin[i]
            while self.rawData[eb] < self.limit and eb > 0:
                eb -= 1
            self.edgeBegin[i] = eb

            ee = self.edgeEnd[i]
            while self.rawData[ee] < self.limit:
                ee += 1
                if i == self.numberOfEvents - 1:
                    if ee == len(self.rawData) - 1:
                        self.edgeEnd[i] = 0
                        self.edgeBegin[i] = 0
                        ee = 0
                        break
                elif ee > self.edgeBegin[i + 1]:
                    self.edgeBegin[i+1] = 0
                    self.edgeEnd[i] = 0
                    ee = 0
                    break
            self.edgeEnd[i] = ee

        self.edgeBegin = self.edgeBegin[self.edgeBegin != 0]
        self.edgeEnd = self.edgeEnd[self.edgeEnd != 0]
        # Remove cases where there is an event begin towards the end of the data without an event ending and vice versa
        if (len(self.edgeBegin) > len(self.edgeEnd)):
            self.edgeBegin = self.edgeBegin[:-1]
        elif (len(self.edgeEnd) > len(self.edgeBegin)):
            self.edgeEnd = self.edgeEnd[1:]
        self.numberOfEvents = len(self.edgeBegin)

        # Remove events shorter than duration specified in the GUI
        for i in range(self.numberOfEvents):
            if ((self.edgeEnd[i] - self.edgeBegin[i]) < self.minimumEventSamples):
                self.edgeBegin[i] = 0
                self.edgeEnd[i] = 0
        self.edgeBegin = self.edgeBegin[self.edgeBegin != 0]
        self.edgeEnd = self.edgeEnd[self.edgeEnd != 0]
        self.numberOfEvents = len(self.edgeBegin)

        for i in range(self.numberOfEvents-1, 0, -1):
            #Remove events that are too close to each other
            if (self.edgeBegin[i] - self.edgeEnd[i-1] < 5e-6*self.effectiveSamplingRate):
                self.edgeBegin[i] = 0
                self.edgeEnd[i-1] = 0
            # elif (self.edgeBegin[i] - self.edgeEnd[i-1] < self.maximumEventSamples):
            else:
                if (not numpy.any(self.rawData[self.edgeEnd[i-1]:self.edgeBegin[i]] > self.baseline - 0.5*self.sigma)):
                    self.edgeBegin[i] = 0
                    self.edgeEnd[i-1] = 0
        self.edgeBegin = self.edgeBegin[self.edgeBegin != 0]
        self.edgeEnd = self.edgeEnd[self.edgeEnd != 0]
        self.numberOfEvents = len(self.edgeBegin)
        print self.baseline

        # Remove events shorter than duration specified in the GUI
        for i in range(self.numberOfEvents):
            if ((self.edgeEnd[i] - self.edgeBegin[i]) < self.minimumEventSamples) or ((self.edgeEnd[i] - self.edgeBegin[i]) > self.maximumEventSamples):
                self.edgeBegin[i] = 0
                self.edgeEnd[i] = 0
        self.edgeBegin = self.edgeBegin[self.edgeBegin != 0]
        self.edgeEnd = self.edgeEnd[self.edgeEnd != 0]
        self.numberOfEvents = len(self.edgeBegin)

        self.eventIndex = numpy.empty_like(self.edgeBegin, dtype='object') #Overwrites previous self.eventIndex
        self.eventIndex2 = numpy.empty_like(self.edgeBegin, dtype='object') #Overwrites previous self.eventIndex
        self.eventValue = numpy.empty_like(self.edgeBegin, dtype='object')
        self.deltaI = numpy.empty_like(self.edgeBegin, dtype='object')
        self.meanDeltaI = numpy.empty_like(self.edgeBegin, dtype=numpy.float32)
        self.dwellTime = numpy.empty_like(self.edgeBegin, dtype=numpy.float32)
        # self.meanEventValue = numpy.empty_like(self.edgeBegin, dtype='object') #Overwrites previous self.eventIndex
        # self.popt = numpy.zeros(0)

        for i in range(self.numberOfEvents):
            # self.eventIndex2[i] = numpy.arange(self.edgeBegin[i], self.edgeEnd[i]+1)
            self.eventIndex[i] = numpy.arange(self.edgeBegin[i]-100, self.edgeEnd[i]+101)
            self.eventValue[i] = self.rawData[self.eventIndex[i][100:-100]]
            self.deltaI[i] = self.baseline - self.rawData[self.eventIndex[i][100:-100]]
            self.meanDeltaI[i] = numpy.mean(self.deltaI[i], dtype=numpy.float32)
            self.dwellTime[i] = (self.edgeEnd[i] - self.edgeBegin[i]).astype(numpy.float32)/self.effectiveSamplingRate
            # popt, pconv = scipy.optimize.curve_fit(self.exponentialFunction, self.eventIndex[i][:500] - self.eventIndex[i][0], self.eventValue[i][:500])
            # self.meanEventValue[i] = self.exponentialFunction(self.eventIndex[i][:500] - self.eventIndex[i][0], *popt)
            # self.popt = numpy.append(self.popt, popt[1]/40e6)

        # print self.edgeBegin, self.edgeEnd, self.eventIndex
        self.parentWindow.edgeBegin = self.edgeBegin
        self.parentWindow.edgeEnd = self.edgeEnd
        self.parentWindow.numberOfEvents = self.numberOfEvents
        self.parentWindow.eventIndex = self.eventIndex
        self.parentWindow.eventValue = self.eventValue
        self.parentWindow.deltaI = self.deltaI
        self.parentWindow.meanDeltaI = self.meanDeltaI
        self.parentWindow.dwellTime = numpy.reshape(self.dwellTime, (len(self.dwellTime), 1))
        # self.parentWindow.PSDWorkerInstance.needsScaling = True
        # self.parentWindow.PSDWorkerInstance.ADCData = self.rawData2[self.rawData >= self.baseline - self.sigma*5]*self.parentWindow.RDCFB*self.dictOfConstants['AAFILTERGAIN']
        # self.parentWindow.PSDThread.start()

        # self.parentWindow.meanEventValue = self.meanEventValue
        # print numpy.mean(self.popt), numpy.std(self.popt)

        if self.numberOfEvents != 0 and self.parentWindow.ui.checkBox_enableCUSUM.isChecked():
            self.edgeDetectionFinished.emit()
            self.analyze_cusum_modified()
        else:
            self.finished.emit()

    def analyze_cusum_modified(self):
        """Performs CUSUM based fitting for data near event locations determined by simple thresholding. Adapted from PyPore implementation
        but only handles downward spikes"""
        #Initializations
        i = 0
        j = 0
        eventNumber = 0
        dataPoint = self.rawData[i]
        nData = len(self.rawData)
        baseline = dataPoint
        variance = numpy.var(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex])
        variance_baseline = baseline
        isEvent = False
        localEventIndex = numpy.hstack(self.eventIndex)

        maxNumberOfEvents = 1000

        self.meanEventValue = [[]]
        self.dwellTime = numpy.zeros([maxNumberOfEvents, self.maximumEventSamples], dtype='float32')
        self.eventFitColor = []

        threshold_start = 5 * numpy.sqrt(variance)
        threshold_end = 1 * numpy.sqrt(variance)

        # while j < (len(localEventIndex)):
        while j in range(numpy.shape(self.eventIndex)[0]):
            i = self.eventIndex[j][0]
            dataPoint = self.rawData[i]

            # if True:
            # done = False
            meanEstimate = dataPoint
            nLevels = 0
            sn = sp = Sn = Sp = Gn = Gp = 0
            varianceEstimate = variance
            threshold_end = 1 * numpy.sqrt(variance)

            # delta = numpy.abs(meanEstimate - baseline)/2.
            # delta = 5e-9
            delta = float(self.parentWindow.ui.lineEdit_CUSUMDelta.text())*1e-9
            minIndexP = minIndexN = i

            eventArea = dataPoint
            event_i = i
            ko = i

            levelSum = dataPoint
            levelSumMinP = dataPoint
            levelSumMinN = dataPoint
            previousLevelStart = event_i

            while event_i in self.eventIndex[j][:-1]:
                event_i += 1
                dataPoint = self.rawData[event_i]

                # if dataPoint >= baseline - threshold_end:
                    # done = True
                    # break

                newMean = meanEstimate + (dataPoint - meanEstimate)/(1 + event_i - ko)
                varianceEstimate = ((event_i - ko) * varianceEstimate + (dataPoint - meanEstimate) * (dataPoint - newMean))/(1 + event_i - ko)
                meanEstimate = newMean
                if varianceEstimate == 0:
                    varianceEstimate = variance
                if varianceEstimate > 0:
                    sp = (delta/varianceEstimate) * (dataPoint - meanEstimate - delta/2.)
                    sn = -(delta/varianceEstimate) * (dataPoint - meanEstimate + delta/2.)
                elif delta == 0:
                    sp = 0
                    sn = 0
                Sp += sp
                Sn += sn
                Gp = numpy.maximum(0., Gp + sp)
                Gn = numpy.maximum(0., Gn + sn)
                levelSum += dataPoint

                if Sp <= 0:
                    Sp = 0
                    minIndexP = event_i
                    levelSumMinP = levelSum
                if Sn <= 0:
                    Sn = 0
                    minIndexN = event_i
                    levelSumMinN = levelSum
                h = delta/numpy.sqrt(varianceEstimate)

                if Gp > h or Gn > h:
                    if Gp > h:
                        minIndex = minIndexP
                        levelSum = levelSumMinP
                    else:
                        minIndex = minIndexN
                        levelSum = levelSumMinN
                    self.dwellTime[eventNumber][nLevels] = (minIndex + 1 - ko)
                    # self.meanEventValue[eventNumber][nLevels] = levelSum/self.dwellTime[eventNumber][nLevels]
                    self.meanEventValue[eventNumber].append([levelSum*1.0/self.dwellTime[eventNumber][nLevels] for k in range(self.dwellTime[eventNumber][nLevels])])
                    nLevels += 1
                    sn = sp = Sn = Sp = Gn = Gp = 0
                    ko = event_i = minIndex + 1
                    minIndexP = minIndexN = event_i
                    previousLevelStart = event_i
                    meanEstimate = self.rawData[event_i]
                    levelSum = levelSumMinP = levelSumMinN = meanEstimate

                # event_i += 1

            # i = self.edgeEnd[eventNumber].astype(int)
            if self.edgeEnd[eventNumber] > previousLevelStart:
                self.dwellTime[eventNumber][nLevels] = (self.edgeEnd[eventNumber] - previousLevelStart)
                # self.meanEventValue[eventNumber][nLevels] = levelSum/self.dwellTime[eventNumber][nLevels]
                self.meanEventValue[eventNumber].append([levelSum*1.0/(self.dwellTime[eventNumber][nLevels]+1) for k in range(self.dwellTime[eventNumber][nLevels])])
                nLevels += 1

            if self.edgeEnd[eventNumber] - self.edgeBegin[eventNumber] > self.minimumEventSamples:
                if self.edgeEnd[eventNumber] - self.edgeBegin[eventNumber] < 0: # Limit fastest events to 80 samples long => 2 us at 40 MSPS
                    nLevels = 0
                    # self.meanEventValue[eventNumber][nLevels] = numpy.min(self.rawData[self.edgeBegin[eventNumber]:self.edgeEnd[eventNumber]+1])
                    self.dwellTime[eventNumber][nLevels] = self.edgeEnd[eventNumber]-self.edgeBegin[eventNumber]
                    self.meanEventValue[eventNumber] = [numpy.min(self.rawData[self.edgeBegin[eventNumber]:self.edgeEnd[eventNumber]+1]) for k in range(self.dwellTime[eventNumber][nLevels])]

            # self.eventValue2.append(numpy.hstack(self.meanEve.astype(int)])
            # self.eventValue2[eventNumber] = self.eventValue2[eventNumber][self.eventValue2[eventNumber] != None]
            self.meanEventValue.append([])
            self.dwellTime[eventNumber][0] = 1
            self.dwellTime[eventNumber][-1] = 1

            # Check to make sure that there aren't multiple rise and fall sequences within an event
            if numpy.sum(numpy.abs(numpy.diff(numpy.sign(numpy.diff([self.meanEventValue[eventNumber][i][0] for i in range(numpy.shape(self.meanEventValue[eventNumber])[0])]))))) == 2:
                # Check only for the levels with long enough dwells (long enough is 10 % of total dwell)
                levelIndices = numpy.where(self.dwellTime[eventNumber] > numpy.maximum(2, numpy.ceil(0.1*numpy.sum(self.dwellTime[eventNumber]))))[0]
                levelIndices = levelIndices[numpy.where(numpy.diff(levelIndices) == 1)[0]]
                if len(levelIndices) == 1:
                    # Check to make sure that the difference between the levels is not too large
                    if (numpy.abs(self.meanEventValue[eventNumber][levelIndices][0] - self.meanEventValue[eventNumber][levelIndices+1][0]) < 4e-9) and (numpy.abs(self.meanEventValue[eventNumber][levelIndices][0] - self.meanEventValue[eventNumber][levelIndices+1][0]) > self.sigma):
                        # Check to make sure that at least one of the 2 levels is below threshold
                        if (self.meanEventValue[eventNumber][levelIndices][0] < self.threshold) or (self.meanEventValue[eventNumber][levelIndices+1][0] < self.threshold):
                            self.eventFitColor.append('r')
                        else:
                            self.eventFitColor.append('k')
                    else:
                        self.eventFitColor.append('k')
                else:
                    self.eventFitColor.append('k')
            else:
                    self.eventFitColor.append('k')

            eventNumber += 1

            baseline = baseline * 0.93 + (1 - 0.93) * dataPoint #Adaptive baseline
            variance_baseline = 0.99 * variance_baseline + (1 - 0.99) * dataPoint
            variance = 0.99 * variance + (1 - 0.99) * numpy.power(dataPoint - variance_baseline, 2) #Adaptive baseline
            # j = numpy.where(localEventIndex == event_i)[0] + 1
            j += 1
            self.progress.emit(1, 'Working')
            self.dwellTime[eventNumber-1][nLevels:] = 0
            # print eventNumber, i, j, len(localEventIndex), baseline, threshold_end

        # self.eventIndex = numpy.empty_like(self.edgeBegin, dtype='object')
        # for i in range(eventNumber):
            # self.eventIndex[i] = numpy.arange(self.edgeBegin[i], self.edgeEnd[i]+1)

        print "Finishing"
        self.parentWindow.meanEventValue = numpy.asarray(self.meanEventValue, dtype='object')
        # self.parentWindow.eventValue2 = numpy.asarray(self.eventValue2, dtype='object')
        # self.parentWindow.dwellTime = self.dwellTime[:eventNumber]/self.dictOfConstants['ADCSAMPLINGRATE']
        self.parentWindow.dwellTime = self.dwellTime[:eventNumber]/self.effectiveSamplingRate
        self.parentWindow.eventFitColor = self.eventFitColor

        self.finished.emit()

    def exponentialFunction(self, x, a, b, c):
        return a*numpy.exp(-x/b) + c

    def analyze_cusum_modified2(self):
        '''This method hasn't been implemented completely and should NOT be used'''
        #Initializations
        i = 0
        j = 0
        eventNumber = 0
        dataPoint = self.rawData[i]
        nData = len(self.rawData)
        baseline = dataPoint
        variance = numpy.var(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex])
        variance_baseline = baseline
        isEvent = False
        localEventIndex = numpy.hstack(self.eventIndex)

        maxNumberOfEvents = 1000

        # self.edgeBegin = numpy.empty(maxNumberOfEvents)
        # self.edgeEnd = numpy.empty(maxNumberOfEvents)
        self.meanEventValue = [[]]
        self.dwellTime = numpy.zeros([maxNumberOfEvents, self.maximumEventSamples], dtype='float32')
        self.eventFitColor = []

        threshold_start = 5 * numpy.sqrt(variance)
        threshold_end = 5 * numpy.sqrt(variance)

        # while j < (len(localEventIndex)):
        while j in range(numpy.shape(self.eventIndex)[0]):
            i = self.eventIndex[j][0]
            while i in self.eventIndex[j]:
                dataPoint = self.rawData[i]
                threshold_start = 5 * numpy.sqrt(variance)

                if numpy.abs(dataPoint - baseline) > threshold_start:
                    isEvent = True

                if isEvent:
                    isEvent = False
                    done = False
                    meanEstimate = dataPoint
                    nLevels = 0
                    sn = sp = Sn = Sp = Gn = Gp = 0
                    varianceEstimate = variance
                    threshold_end = 5 * numpy.sqrt(variance)

                    # delta = numpy.abs(meanEstimate - baseline)/2.
                    # delta = 5e-9
                    delta = float(self.parentWindow.ui.lineEdit_CUSUMDelta.text())*1e-9
                    minIndexP = minIndexN = i

                    # eventArea = dataPoint
                    event_i = i
                    ko = i

                    levelSum = dataPoint
                    levelSumMinP = dataPoint
                    levelSumMinN = dataPoint
                    previousLevelStart = event_i

                    while not done and event_i in self.eventIndex[j][:-1]:
                        event_i += 1
                        dataPoint = self.rawData[event_i]

                        if j == 0:
                            print i, event_i, self.eventIndex[j][100], self.eventIndex[j][-101]

                        if numpy.abs(dataPoint - baseline) < threshold_end:
                            done = True
                            if j == 0:
                                print done

                        newMean = meanEstimate + (dataPoint - meanEstimate)/(1 + event_i - ko)
                        varianceEstimate = ((event_i - ko) * varianceEstimate + (dataPoint - meanEstimate) * (dataPoint - newMean))/(1 + event_i - ko)
                        meanEstimate = newMean
                        if varianceEstimate == 0:
                            varianceEstimate = variance
                        if varianceEstimate > 0:
                            sp = (delta/varianceEstimate) * (dataPoint - meanEstimate - delta/2.)
                            sn = -(delta/varianceEstimate) * (dataPoint - meanEstimate + delta/2.)
                        elif delta == 0:
                            sp = 0
                            sn = 0
                        Sp += sp
                        Sn += sn
                        Gp = numpy.maximum(0., Gp + sp)
                        Gn = numpy.maximum(0., Gn + sn)
                        levelSum += dataPoint

                        if Sp <= 0:
                            Sp = 0
                            minIndexP = event_i
                            levelSumMinP = levelSum
                        if Sn <= 0:
                            Sn = 0
                            minIndexN = event_i
                            levelSumMinN = levelSum
                        h = delta/numpy.sqrt(varianceEstimate)

                        if Gp > h or Gn > h:
                            if Gp > h:
                                minIndex = minIndexP
                                levelSum = levelSumMinP
                            else:
                                minIndex = minIndexN
                                levelSum = levelSumMinN
                            self.dwellTime[eventNumber][nLevels] = (minIndex + 1 - ko)
                            # self.meanEventValue[eventNumber][nLevels] = levelSum/self.dwellTime[eventNumber][nLevels]
                            self.meanEventValue[eventNumber].append([levelSum*1.0/self.dwellTime[eventNumber][nLevels] for k in range(self.dwellTime[eventNumber][nLevels])])
                            nLevels += 1
                            sn = sp = Sn = Sp = Gn = Gp = 0
                            ko = event_i = minIndex + 1
                            minIndexP = minIndexN = event_i
                            previousLevelStart = event_i
                            meanEstimate = self.rawData[event_i]
                            levelSum = levelSumMinP = levelSumMinN = meanEstimate

                        # event_i += 1
                    i = event_i

                    # i = self.edgeEnd[eventNumber].astype(int)
                    if self.edgeEnd[eventNumber] > previousLevelStart:
                        self.dwellTime[eventNumber][nLevels] = (self.edgeEnd[eventNumber] - previousLevelStart)
                        # self.meanEventValue[eventNumber][nLevels] = levelSum/self.dwellTime[eventNumber][nLevels]
                        self.meanEventValue[eventNumber].append([levelSum*1.0/(self.dwellTime[eventNumber][nLevels]+1) for k in range(self.dwellTime[eventNumber][nLevels])])
                        nLevels += 1

                    if self.edgeEnd[eventNumber] - self.edgeBegin[eventNumber] > self.minimumEventSamples:
                        if self.edgeEnd[eventNumber] - self.edgeBegin[eventNumber] < 0: # Limit fastest events to 80 samples long => 2 us at 40 MSPS
                            nLevels = 0
                            # self.meanEventValue[eventNumber][nLevels] = numpy.min(self.rawData[self.edgeBegin[eventNumber]:self.edgeEnd[eventNumber]+1])
                            self.dwellTime[eventNumber][nLevels] = self.edgeEnd[eventNumber]-self.edgeBegin[eventNumber]
                            self.meanEventValue[eventNumber] = [numpy.min(self.rawData[self.edgeBegin[eventNumber]:self.edgeEnd[eventNumber]+1]) for k in range(self.dwellTime[eventNumber][nLevels])]

                    # self.eventValue2.append(numpy.hstack(self.meanEve.astype(int)])
                    # self.eventValue2[eventNumber] = self.eventValue2[eventNumber][self.eventValue2[eventNumber] != None]
                    self.meanEventValue.append([])
                    self.dwellTime[eventNumber][0] = 1
                    self.dwellTime[eventNumber][-1] = 1

                    # Check to make sure that there aren't multiple rise and fall sequences within an event
                    if numpy.sum(numpy.abs(numpy.diff(numpy.sign(numpy.diff([self.meanEventValue[eventNumber][i][0] for i in range(numpy.shape(self.meanEventValue[eventNumber])[0])]))))) == 2:
                        # Check only for the levels with long enough dwells (long enough is 10 % of total dwell)
                        levelIndices = numpy.where(self.dwellTime[eventNumber] > numpy.maximum(2, numpy.ceil(0.1*numpy.sum(self.dwellTime[eventNumber]))))[0]
                        levelIndices = levelIndices[numpy.where(numpy.diff(levelIndices) == 1)[0]]
                        if len(levelIndices) == 1:
                            # Check to make sure that the difference between the levels is not too large
                            if (numpy.abs(self.meanEventValue[eventNumber][levelIndices][0] - self.meanEventValue[eventNumber][levelIndices+1][0]) < 4e-9) and (numpy.abs(self.meanEventValue[eventNumber][levelIndices][0] - self.meanEventValue[eventNumber][levelIndices+1][0]) > self.sigma):
                                # Check to make sure that at least one of the 2 levels is below threshold
                                if (self.meanEventValue[eventNumber][levelIndices][0] < self.threshold) or (self.meanEventValue[eventNumber][levelIndices+1][0] < self.threshold):
                                    self.eventFitColor.append('r')
                                else:
                                    self.eventFitColor.append('k')
                            else:
                                self.eventFitColor.append('k')
                        else:
                            self.eventFitColor.append('k')
                    else:
                            self.eventFitColor.append('k')

                    self.dwellTime[eventNumber][nLevels:] = 0
                    eventNumber += 1

                baseline = baseline * 0.93 + (1 - 0.93) * dataPoint #Adaptive baseline
                variance_baseline = 0.99 * variance_baseline + (1 - 0.99) * dataPoint
                variance = 0.99 * variance + (1 - 0.99) * numpy.power(dataPoint - variance_baseline, 2) #Adaptive baseline
            # j = numpy.where(localEventIndex == event_i)[0] + 1
                i += 1
            j += 1
            self.progress.emit(1, 'Working')
            # print eventNumber, i, j, len(localEventIndex), baseline, threshold_end

        # self.eventIndex = numpy.empty_like(self.edgeBegin, dtype='object')
        # for i in range(eventNumber):
            # self.eventIndex[i] = numpy.arange(self.edgeBegin[i], self.edgeEnd[i]+1)

        print "Finishing"
        self.parentWindow.meanEventValue = numpy.asarray(self.meanEventValue, dtype='object')
        # self.parentWindow.eventValue2 = numpy.asarray(self.eventValue2, dtype='object')
        # self.parentWindow.dwellTime = self.dwellTime[:eventNumber]/self.dictOfConstants['ADCSAMPLINGRATE']
        self.parentWindow.dwellTime = self.dwellTime[:eventNumber]/self.effectiveSamplingRate
        self.parentWindow.eventFitColor = self.eventFitColor

        self.finished.emit()
