# -*- coding: utf-8 -*-
import os
from PyQt4 import QtCore
import numpy, scipy.signal, scipy.optimize
import time, datetime
import copy
import pywt, pyqtgraph
import Queue
import numba

import globalConstants

class PSDWorker(QtCore.QObject):
    # finished = QtCore.pyqtSignal(numpy.float64, numpy.float64)
    finished = QtCore.pyqtSignal()
    # PSDReady = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    PSDReady = QtCore.pyqtSignal(int)
    histogramReady = QtCore.pyqtSignal()
    #Signal for progress bar
    progress = QtCore.pyqtSignal(int, str)

    def __init__(self, parentWindow):
        super(PSDWorker, self).__init__()
        self.parentWindow = parentWindow
        self.needsScaling = False
        self.ADCData = []
        self.adcDataRMS = 0
        self.validColumn = None

    @numba.jit
    def numba_scale(self, array, bits=12):
        for i in xrange(len(array)):
            if array[i] >= 2**(bits-1):
                array[i] -= 2**bits
            array[i] /= 2**(bits-1)

    def calculatePSD(self):
        self.start = time.clock()

        if (self.needsScaling):
            self.numba_scale(self.ADCData, globalConstants.ADCBITS)
            # self.ADCData[self.ADCData >= 2**(globalConstants.ADCBITS-1)] -= 2**(globalConstants.ADCBITS)
            # self.ADCData /= 2**(globalConstants.ADCBITS-1)
            self.ADCData -= numpy.mean(self.ADCData)
        # if (True == self.parentWindow.ui.checkBox_enableSquareWave.isChecked()):
            # self.calculateDCResistance()
        # if (window.columnSelect in [0, 3]):
            # self.ADCData *= 16.0/5
        self.parentWindow.adcList[self.validColumn].histogramView, self.parentWindow.adcList[self.validColumn].bins = numpy.histogram(self.ADCData, bins=64)
        self.parentWindow.adcList[self.validColumn].bins /= (globalConstants.AAFILTERGAIN*self.parentWindow.RDCFB)
        self.parentWindow.adcList[self.validColumn].bins -= self.parentWindow.adcList[self.validColumn].idcOffset
        self.histogramReady.emit() # TODO
        self.progress.emit(2, 'Calculating PSD')
        #### Begin PSD calculation
        # f, Pxx = scipy.signal.periodogram(self.ADCData, globalConstants.ADCSAMPLINGRATE, nfft=2**19)
        f, Pxx = scipy.signal.welch(self.ADCData, globalConstants.ADCSAMPLINGRATE, nperseg=2**13)
        #### End PSD calculation

        #### Begin FFT calculation
        # NFFT = 2**19
        # ADCSAMPLINGRATE = globalConstants.ADCSAMPLINGRATE
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
        logIndices = numpy.unique(numpy.asarray(numpy.logspace(0, numpy.log10(f_PSDStopFrequency), f_PSDStopFrequency/globalConstants.SUBSAMPLINGFACTOR, dtype=numpy.int32)))
        self.parentWindow.adcList[self.validColumn].f = f[logIndices-1]
        if (hasattr(self.parentWindow.ui, 'checkBox_frequencyResponse') and self.parentWindow.ui.checkBox_frequencyResponse.isChecked() == True):
            self.parentWindow.adcList[self.validColumn].psd = numpy.divide(Pxx[logIndices-1], f[logIndices-1]**2)
        else:
            self.parentWindow.adcList[self.validColumn].psd = Pxx[logIndices-1]
        if (self.parentWindow.ui.action_addNoiseFit.isChecked() == True): # TODO
            self.parentWindow.adcList[self.validColumn].psdFit = self.createFit(self.parentWindow.adcList[self.validColumn].f, self.parentWindow.adcList[self.validColumn].psd, 1e6)
        # self.PSDReady.emit(fToDisplay, PxxToDisplay)
        self.PSDReady.emit(self.validColumn)
        self.progress.emit(1, 'Finishing up')

        rmsNoise = numpy.sqrt(scipy.integrate.cumtrapz(Pxx, f, initial=0))/globalConstants.AAFILTERGAIN/self.parentWindow.RDCFB
        self.parentWindow.adcList[self.validColumn].rmsNoise = rmsNoise[logIndices-1]

        self.parentWindow.adcList[self.validColumn].rmsNoise_100kHz = numpy.round(rmsNoise[f_100kHz] * 10**12, 1)
        self.parentWindow.adcList[self.validColumn].rmsNoise_1MHz = numpy.round(rmsNoise[f_1MHz] * 10**12, 1)
        self.parentWindow.adcList[self.validColumn].rmsNoise_10MHz = numpy.round(rmsNoise[f_10MHz-1] * 10**12, 1)
        self.stop = time.clock()
        # print "Calculate PSD thread took", self.stop-self.start, "s"
        # self.finished.emit(numpy.round(RMSNoise_100kHz * 10**12, 1), numpy.round(RMSNoise_1MHz * 10**12, 1))
        self.finished.emit()

    def calculateDCResistance(self):
        self.adcDataRMS = numpy.sqrt(numpy.mean(numpy.power(self.ADCData, 2)))
        self.adcList[self.validColumn].poreResistance = globalConstants.SQUAREWAVEAMPLITUDE/self.adcDataRMS*globalConstants.AAFILTERGAIN*self.parentWindow.adcList[self.validColumn].rdcfb
        self.parentWindow.ui.label_poreResistance.setText(str(numpy.round(self.adcList[self.validColumn].poreResistance/1e6, 1)) + u"MΩ") # TODO

    def createFit(self, fFit, PSDFit, maxFitFrequency = 6e6):
        fFitNew = fFit[fFit < maxFitFrequency]
        PSDFitNew = PSDFit[fFit < maxFitFrequency]
        fitCoefficients = numpy.polynomial.polynomial.polyfit(fFitNew, PSDFitNew * fFitNew, 3, w = 1/(fFitNew * PSDFitNew)) #Fit PSD*f to 3rd order and then divide by f to get the 1/f term also
        print numpy.sqrt(fitCoefficients[3])/(2*3.14*3.15e-9*self.parentWindow.RDCFB*globalConstants.AAFILTERGAIN)
        return numpy.divide(numpy.polynomial.polynomial.polyval(fFit, fitCoefficients), fFit)


class GetDataFromFPGAWorker(QtCore.QObject):
    """Worker module that inherits from QObject. Eventually, this gets moved on to a thread that inherits from QThread."""
    finished = QtCore.pyqtSignal()
    dataReady = QtCore.pyqtSignal(str)

    def __init__(self, parentWindow, FPGAInstance):
        super(GetDataFromFPGAWorker, self).__init__()
        self.parentWindow = parentWindow
        self.FPGAInstance = FPGAInstance
        self.commandQueue = Queue.Queue()
        self.frameCount = 0
        self.logging = False

        if self.FPGAInstance is not None:
            self.FPGAType = self.FPGAInstance.type
            self.validColumns = self.FPGAInstance.validColumns
            self.processRawDataThreadOptions = {'Master': self.parentWindow.processRawDataADC0Thread, 'Slave': self.parentWindow.processRawDataADC1Thread}
            self.processRawDataThread = self.processRawDataThreadOptions[self.FPGAType]
            self.processRawDataADCWorkerInstanceOptions = {'Master': self.parentWindow.processRawDataADC0WorkerInstance, 'Slave': self.parentWindow.processRawDataADC1WorkerInstance}
            self.processRawDataADCWorkerInstance = self.processRawDataADCWorkerInstanceOptions[self.FPGAType]

    def getDataFromFPGA(self):
        """Gets data from the FPGA and logs it if the corresponding option has been enabled. Calls processRawData once a chunk of data has been obtained. Loops infinitely."""
        while (self.FPGAInstance.configured):
            #if self.FPGAInstance.UpdateWire is True:
            #    self.FPGAInstance.UpdateWire = False
            #    self.FPGAInstance.xem.UpdateWireIns()
            #if self.FPGAInstance.ActivateTrigger is True:
            #    self.FPGAInstance.ActivateTrigger = False
            #    self.FPGAInstance.xem.ActivateTriggerIn(self.FPGAInstance.TriggerEndpoint, self.FPGAInstance.TriggerBitmask)
            self.executeCommands()
            if ('Master' == self.FPGAType):
                rawData = bytearray(globalConstants.FRAMELENGTH_MASTER)
            elif ('Slave' == self.FPGAType):
                rawData = bytearray(globalConstants.FRAMELENGTH_SLAVE)

            self.start = time.clock()
            errorReturn = self.FPGAInstance.xem.ReadFromBlockPipeOut(0xA0, globalConstants.BLOCKLENGTH, rawData)
            if (self.FPGAInstance.xem.Timeout == errorReturn):
                print "Transaction timed out on", self.FPGAType, "FPGA"
            if (self.FPGAInstance.xem.Failed == errorReturn):
                print "Transaction failed on", self.FPGAType, "FPGA"
                self.FPGAInstance.powered = False #Change power status to off if code breaks out of the while loop
                self.FPGAInstance.configured = False #Change configuration status to unconfigured if code breaks out of the while loop

            if ('Master' == self.FPGAType):
                if (True == self.parentWindow.writeToMasterLogFileWorkerInstance.logging):
                    self.parentWindow.writeToMasterLogFileWorkerInstance.rawData.put(rawData)
            elif ('Slave' == self.FPGAType):
                if (True == self.parentWindow.writeToMasterLogFileWorkerInstance.logging):
                    self.parentWindow.writeToSlaveLogFileWorkerInstance.rawData.put(rawData)

            self.dataReady.emit(self.FPGAType)

            if not self.processRawDataThread.isRunning():
                self.processRawDataADCWorkerInstance.rawData = rawData
                self.processRawDataThread.start()

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

    def executeCommands(self):
        while (not self.commandQueue.empty()):
            command = self.commandQueue.get(True, 1)
            if (globalConstants.CMDQUEUEWIRE == command[0]):
                error = self.FPGAInstance.xem.SetWireInValue(command[2], command[3], command[4])
            elif (globalConstants.CMDUPDATEWIRE == command[0]):
                error = self.FPGAInstance.xem.UpdateWireIns()
            elif (globalConstants.CMDTRIGGERWIRE == command[0]):
                error = self.FPGAInstance.xem.ActivateTriggerIn(command[2], command[3])
            else:
                print 'Command not found'
            if (self.FPGAInstance.xem.NoError != error):
                print command[1]

class ProcessRawDataWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    # dataReady = QtCore.pyqtSignal(numpy.ndarray)
    dataReady = QtCore.pyqtSignal(int)
    startPSDThread = QtCore.pyqtSignal()
    #Signals for the progress bar
    progress = QtCore.pyqtSignal(int, str)

    def __init__(self, parentWindow, validColumns):
        super(ProcessRawDataWorker, self).__init__()
        self.skipPoints = 0
        self.createFilter(100e3)
        self.parentWindow = parentWindow
        self.validColumns = validColumns
        self.rawDataUnpacked = 0
        self.compressedData = False

    @numba.jit
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
        for column in self.validColumns:
            #self.start = time.clock()
            # self.rawDataUnpacked = numpy.frombuffer(self.rawData, dtype='uint32')
            # ADCData = {0: numpy.bitwise_and(self.rawDataUnpacked, 0xfff),\
                    # 1: (numpy.bitwise_and(self.rawDataUnpacked, 0xfff000))>>12,\
                    # 3: numpy.bitwise_and(self.rawDataUnpacked, 0xfff)}
            # Switched from dictionary to if else implementation because of timing issues while displaying data
            if self.compressedData == False:
                ADCData = self.unpackData(column).astype(numpy.float32)
            else:
                ADCData = numpy.frombuffer(self.rawData, dtype='int16').astype(numpy.float32)

        self.numba_scale(ADCData, globalConstants.ADCBITS)

            if (self.parentWindow.ui.checkBox_enableLivePreviewFilter.isChecked()):
                # ADCData2[ADCData2 >= 2**(globalConstants.ADCBITS-1)] -= 2**(globalConstants.ADCBITS)
                # ADCData2 /= 2**(globalConstants.ADCBITS-1)
                ADCData = scipy.signal.lfilter(self.b, self.a, ADCData)

                #ADCData2[:-1] += numpy.diff(ADCData2)/(2*numpy.pi*2.5e6/globalConstants.ADCSAMPLINGRATE)

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
                # print totalNoise/self.parentWindow.RDCFB/globalConstants.AAFILTERGAIN
                # tags = ADCData < -5*totalNoise
                # print totalNoise/self.parentWindow.RDCFB, numpy.sum(numpy.bitwise_and(numpy.bitwise_and(tags[:-3], tags[1:-2]), numpy.bitwise_and(tags[2:-1], tags[3:])))

                ADCData = ADCData[self.skipPoints:]
                dataToDisplay = ADCData[::globalConstants.SUBSAMPLINGFACTOR]
                if (hasattr(self.parentWindow, 'analyzeDataWorkerInstance')): #TODO
                    self.parentWindow.analyzeDataWorkerInstance.rawData = ADCData[::self.skipPoints/4]/self.parentWindow.RDCFB/globalConstants.AAFILTERGAIN - self.parentWindow.adcList[column].idcOffset
                    self.parentWindow.analyzeDataWorkerInstance.effectiveSamplingRate = globalConstants.ADCSAMPLINGRATE/self.skipPoints*4

            else:
                #ADCData[:-1] += numpy.diff(ADCData)/(2*numpy.pi*2.5e6/globalConstants.ADCSAMPLINGRATE)
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
                #         self.parentWindow.analyzeDataWorkerInstance.rawData = ADCData[:]/self.parentWindow.RDCFB/globalConstants.AAFILTERGAIN - self.parentWindow.adcList[self.validColumn].idcOffset

                if (hasattr(self.parentWindow, 'analyzeDataWorkerInstance')):
                    self.parentWindow.analyzeDataWorkerInstance.rawData = ADCData[:]/self.parentWindow.RDCFB/globalConstants.AAFILTERGAIN - self.parentWindow.adcList[column].idcOffset

                dataToDisplay = ADCData[::globalConstants.SUBSAMPLINGFACTOR]
                # dataToDisplay[dataToDisplay >= 2**(globalConstants.ADCBITS-1)] -= 2**(globalConstants.ADCBITS)
                # dataToDisplay /= 2**(globalConstants.ADCBITS-1)
                # self.numba_scale(dataToDisplay, globalConstants.ADCBITS)

            dataToDisplay *= 1.0/self.parentWindow.RDCFB/globalConstants.AAFILTERGAIN #Prefixes (like nano or pico) are handled automatically by PyQtGraph
            self.parentWindow.adcList[column].idcRelative = numpy.mean(dataToDisplay) - self.parentWindow.adcList[column].idcOffset
            dataToDisplay -= self.parentWindow.adcList[column].idcOffset
            self.parentWindow.updateIDCLabels()
            self.progress.emit(1, 'Finished calculating data to display')

            self.parentWindow.adcList[column].adcData = ADCData

            if (hasattr(self.parentWindow.ui, 'action_enableLivePreview') and self.parentWindow.ui.action_enableLivePreview.isChecked() == False):
                pass
            else:
                if (self.parentWindow.columnSelect == column):
                    self.parentWindow.dataToDisplay = dataToDisplay
                self.parentWindow.adcList[column].yDataToDisplay = dataToDisplay
                self.parentWindow.adcList[column].xDataToDisplay = numpy.linspace(0, len(dataToDisplay) * globalConstants.SUBSAMPLINGFACTOR * 1.0 / globalConstants.ADCSAMPLINGRATE, len(dataToDisplay))

            if (not self.parentWindow.PSDThread.isRunning()):
                self.parentWindow.PSDWorkerInstance.ADCData = ADCData #ADCData is sent as float32
                self.parentWindow.PSDWorkerInstance.validColumn = column
                self.startPSDThread.emit()
                self.progress.emit(1, 'Calculating histogram')

            self.stop = time.clock()
            # print "Processing the data took", self.stop-self.start, "s"
            self.dataReady.emit(column)
        self.finished.emit()

    def createFilter(self, livePreviewFilterBandwidth):
        """livePreviewFilterBandwidth is displayLivePreview used to construct an angular frequency such that Fs/2 = 1. Filter is only approximately correct when
        filtering frequency is < Fs/4"""
        self.livePreviewFilterBandwidth = livePreviewFilterBandwidth
        # Skip first few points of filtered data to avoid edge effects due to filtering
        self.skipPoints = int(numpy.ceil(globalConstants.ADCSAMPLINGRATE/self.livePreviewFilterBandwidth))
        self.b, self.a = scipy.signal.bessel(4, self.livePreviewFilterBandwidth/globalConstants.ADCSAMPLINGRATE*2, 'low')

    def compressData(self):
        return self.unpackData().astype(numpy.int16)

    #@numba.jit    
    @numba.jit('uint32[:](pyobject, uint32[:], uint32, uint64, uint8[:])')
    def numba_bitwise_and(self, array, mask, shift, resulttype='uint32'):
        """Numba implementation of AND function with masking and shifting ability"""
        result = numpy.empty_like(array, dtype=resulttype)
        for i in xrange(len(array)):
            result[i] = numpy.bitwise_and(array[i], mask) >> shift
        return result

    def unpackData(self, column):
        """Returns unpacked ADCData for the selected column"""
        self.progress.emit(1, 'Unpacking data')

        if (0 == column):
            self.rawDataUnpacked = numpy.frombuffer(self.rawData, dtype='uint32')
            #ADCData = numpy.empty_like(self.rawDataUnpacked, dtype='uint32')
            ADCData = self.numba_bitwise_and(self.rawDataUnpacked, numpy.uint32(0xfff), 0)

        elif (1 == column):
            self.rawDataUnpacked = numpy.frombuffer(self.rawData, dtype='uint32')
            #ADCData = numpy.empty_like(self.rawDataUnpacked, dtype='uint32')
            ADCData = self.numba_bitwise_and(self.rawDataUnpacked, numpy.uint32(0xfff000), 12)

        elif (2 == column):
            self.rawData64Bit = numpy.frombuffer(self.rawData, dtype='uint64')
            ADCDataCompressed = self.numba_bitwise_and(self.rawData64Bit[0::2], numpy.uint64(0xfffffffff), 0, 'uint64')
            ADCData = numpy.empty((3 * numpy.size(ADCDataCompressed),), dtype='uint32')
            ADCData[0::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff), 0) # Can this be done in 1 for loop to avoid traversing data 3x?
            ADCData[1::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff000), 12) # Can this be done in 1 for loop to avoid traversing data 3x?
            ADCData[2::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff000000), 24) # Can this be done in 1 for loop to avoid traversing data 3x?

        elif (3 == column):
            self.rawData64Bit = numpy.frombuffer(self.rawData, dtype='uint64')
            ADCDataCompressed = self.numba_bitwise_and(self.rawData64Bit[0::2], numpy.uint64(0xfffffff000000000), 36, 'uint64')
            ADCDataCompressedMSB = self.numba_bitwise_and(self.rawData64Bit[1::2], numpy.uint64(0xff), 0, 'uint64')
            ADCData = numpy.empty((3 * numpy.size(ADCDataCompressed),), dtype='uint32')
            ADCData[0::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff), 0)
            ADCData[1::3] = self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xfff000), 12)
            ADCData[2::3] = (self.numba_bitwise_and(ADCDataCompressed, numpy.uint64(0xf000000), 24)) + (ADCDataCompressedMSB * 16)

        elif (4 == column):
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

    def __init__(self, parentWindow, fpgaInstance):
        super(WriteToLogFileWorker, self).__init__()
        self.rawData = Queue.Queue()
        self.f = 0
        self.parentWindow = parentWindow
        self.fpgaType = fpgaInstance.type
        self.frameCounter = 0
        self.logging = False
        self.defaultDirectory = "./Logfiles" + "/" + datetime.date.today().strftime("%Y%m%d") + "/"
        self.filePrefix = "default"
        self.fileName = self.defaultDirectory + "_" + self.filePrefix + '_' + self.fpgaType + ".hex"
        self.configFileName = self.defaultDirectory + "_" + self.filePrefix + ".cfg"

    def writeToLogFile(self): # TODO Write more than 1 second to a file
        start = time.clock()
        if not os.path.exists(self.defaultDirectory):
            os.makedirs(self.defaultDirectory)

        self.f = open(self.fileName, 'a+b')
        # While logging is enabled, write in 1 second bursts. Finish writing everything that is in memory when logging is disabled
        if (True == self.logging):
            for i in range(globalConstants.REFRESHRATE):
                self.f.write(self.rawData.get())
        else:
            for i in range(self.rawData.qsize()): # TODO qsize is not a reliable way to clear the queue. Maybe while(not queue.isEmpty())?
                self.f.write(self.rawData.get())
        self.f.close()
        if (not os.path.exists(self.configFileName)):
            self.parentWindow.action_saveState_triggered(self.configFileName)
        stop = time.clock()
        print "Writing data to disk took", stop-start, "s"
        # if ((stop - start)*1000 > globalConstants.FRAMEDURATION):
        #     print "Probably missed writing some data because it took too long to write the last frame"
        self.finished.emit()

    def setFileName(self, filePrefix):
        self.filePrefix = filePrefix
        self.fileName = self.defaultDirectory + self.filePrefix + '_' + self.fpgaType + ".hex"
        self.configFileName = self.defaultDirectory + self.filePrefix + ".cfg"

class AnalyzeDataWorker(QtCore.QObject):
    """This class provides methods that can detect event edges and perform CUSUM based fitting on events"""
    progress = QtCore.pyqtSignal(int, str)
    edgeDetectionFinished = QtCore.pyqtSignal()
    quit = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self, parentWindow):
        super(AnalyzeDataWorker, self).__init__()
        self.parentWindow = parentWindow
        self.rawData = 0

    def analyzeData(self, detectEdges=True):
        """This method determines the baseline and threshold values to be used for event detection"""
        # self.generateBaselineStartIndex = 222000e-6*self.effectiveSamplingRate
        # self.generateBaselineStopIndex = 232000e-6*self.effectiveSamplingRate
        if self.parentWindow.ui.checkBox_enableLivePreviewFilter.isChecked() is False: # TODO This is never True?
            self.effectiveSamplingRate = globalConstants.ADCSAMPLINGRATE
        self.generateBaselineStartIndex = int(238900e-6*self.effectiveSamplingRate)
        self.generateBaselineStopIndex = int(239500e-6*self.effectiveSamplingRate)
        #print self.generateBaselineStartIndex, self.generateBaselineStopIndex
        if (self.parentWindow.baseline is not None):
            self.baseline = self.parentWindow.baseline
        else:
            self.baseline = numpy.mean(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex])
            self.parentWindow.baseline = self.baseline
        f, Pxx = scipy.signal.welch(self.rawData, globalConstants.ADCSAMPLINGRATE, nperseg=2**13)
        Pxx = Pxx[f > 100]
        f = f[f > 100]
        self.parentWindow.analyzeF, self.parentWindow.analyzePxx = f, Pxx
        self.sigma = numpy.std(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex])
        #print self.sigma
        self.parentWindow.sigma = self.sigma
        if (self.parentWindow.threshold is not None):
            self.threshold = self.parentWindow.threshold
        else:
            if (hasattr(self.parentWindow, 'numberOfSigmas')):
                self.numberOfSigmas = self.parentWindow.numberOfSigmas
                self.threshold = self.baseline - self.numberOfSigmas * self.sigma
            else:
                self.threshold = self.baseline - 5*self.sigma
            #print numpy.std(self.rawData[self.generateBaselineStartIndex:self.generateBaselineStopIndex])
            self.parentWindow.threshold = self.threshold
        #print self.threshold
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
        if (0 == self.eventIndex.size):
            print "No events found"
            self.quit.emit()
            return
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
        #print self.baseline

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
        # self.parentWindow.PSDWorkerInstance.ADCData = self.rawData2[self.rawData >= self.baseline - self.sigma*5]*self.parentWindow.RDCFB*globalConstants.AAFILTERGAIN
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
        # self.parentWindow.dwellTime = self.dwellTime[:eventNumber]/globalConstants.ADCSAMPLINGRATE
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
        # self.parentWindow.dwellTime = self.dwellTime[:eventNumber]/globalConstants.ADCSAMPLINGRATE
        self.parentWindow.dwellTime = self.dwellTime[:eventNumber]/self.effectiveSamplingRate
        self.parentWindow.eventFitColor = self.eventFitColor

        self.finished.emit()
