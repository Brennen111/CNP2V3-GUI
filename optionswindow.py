from PyQt4 import QtCore, QtGui
from optionsWindow_gui import Ui_Dialog
import globalConstants

class OptionsWindow(QtGui.QDialogButtonBox):
    def __init__(self):
        QtGui.QDialogButtonBox.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        #These settings correspond to the general tab of the options window
        self.PRESETMODE = globalConstants.PRESETMODE
        self.ui.comboBox_presets.setCurrentIndex(self.PRESETMODE)

        self.ui.comboBox_presets.setItemData(0, "Custom preset settings", QtCore.Qt.ToolTipRole)
        self.ui.comboBox_presets.setItemData(1, "Default preset settings. Display refresh is pretty fast while PSD accuracy is still maintained", QtCore.Qt.ToolTipRole)
        self.ui.comboBox_presets.setItemData(2, "Reduces accuracy of the PSD plot in lieu of faster data refreshes", QtCore.Qt.ToolTipRole)
        self.ui.comboBox_presets.setItemData(3, "Increases accuracy of the PSD plot while reducing the refresh rate", QtCore.Qt.ToolTipRole)

        self.ADCBITS = globalConstants.ADCBITS
        self.SUBSAMPLINGFACTOR = globalConstants.SUBSAMPLINGFACTOR
        self.REFRESHRATE = globalConstants.REFRESHRATE
        self.ADCSAMPLINGRATE = globalConstants.ADCSAMPLINGRATE
        self.BLOCKLENGTH = globalConstants.BLOCKLENGTH
        self.MBCOMMONMODE = globalConstants.MBCOMMONMODE

        self.ui.lineEdit_ADCBITS.setText(str(self.ADCBITS))
        self.ui.lineEdit_SUBSAMPLINGFACTOR.setText(str(self.SUBSAMPLINGFACTOR))
        self.ui.lineEdit_REFRESHRATE.setText(str(self.REFRESHRATE))
        self.ui.lineEdit_ADCSAMPLINGRATE.setText(str(self.ADCSAMPLINGRATE))
        self.ui.lineEdit_BLOCKLENGTH.setText(str(self.BLOCKLENGTH))
        self.ui.lineEdit_MBCOMMONMODE.setText(str(self.MBCOMMONMODE))

        self.ui.lineEdit_ADCBITS.setToolTip('Specify the number of bits at the output of the ADC')
        self.ui.lineEdit_SUBSAMPLINGFACTOR.setToolTip('This number determines the amount by which the raw data is downsampled and displayed. Higher values will give faster but less accurate visual output')
        self.ui.lineEdit_REFRESHRATE.setToolTip('Refresh rate of the GUI specified in frames per second')
        self.ui.lineEdit_ADCSAMPLINGRATE.setToolTip('Sampling rate of the ADC. Do not change unless you also plan on changing the bitfile')
        self.ui.lineEdit_BLOCKLENGTH.setToolTip('Block length (in bytes) used in the Opal Kelly BTPipe implementation')
        self.ui.lineEdit_MBCOMMONMODE.setToolTip('Set the common mode voltage for the differential traces on the motherboard')

        self.ui.lineEdit_ADCBITS.editingFinished.connect(self.lineEdit_ADCBITS_editingFinished)
        self.ui.lineEdit_SUBSAMPLINGFACTOR.editingFinished.connect(self.lineEdit_SUBSAMPLINGFACTOR_editingFinished)
        self.ui.lineEdit_REFRESHRATE.editingFinished.connect(self.lineEdit_REFRESHRATE_editingFinished)
        self.ui.lineEdit_ADCSAMPLINGRATE.editingFinished.connect(self.lineEdit_ADCSAMPLINGRATE_editingFinished)
        self.ui.lineEdit_BLOCKLENGTH.editingFinished.connect(self.lineEdit_BLOCKLENGTH_editingFinished)
        self.ui.lineEdit_MBCOMMONMODE.editingFinished.connect(self.lineEdit_MBCOMMONMODE_editingFinished)

        self.ui.comboBox_presets.activated.connect(self.comboBox_presets_activated)

        #These settings correspond to the IV tab of the options window
        self.IVSTARTVOLTAGE = globalConstants.IVSTARTVOLTAGE
        self.IVSTOPVOLTAGE = globalConstants.IVSTOPVOLTAGE
        self.IVVOLTAGESTEP = globalConstants.IVVOLTAGESTEP
        self.IVTIMESTEP = globalConstants.IVTIMESTEP
        self.IVNUMBEROFCYCLES = globalConstants.IVNUMBEROFCYCLES

        self.ui.lineEdit_startVoltage.setText(str(self.IVSTARTVOLTAGE))
        self.ui.lineEdit_stopVoltage.setText(str(self.IVSTOPVOLTAGE))
        self.ui.lineEdit_voltageStep.setText(str(self.IVVOLTAGESTEP))
        self.ui.lineEdit_timeStep.setText(str(self.IVTIMESTEP))
        self.ui.lineEdit_numberOfCycles.setText(str(self.IVNUMBEROFCYCLES))

        self.ui.lineEdit_startVoltage.setToolTip('Set the start voltage for the IV sweep')
        self.ui.lineEdit_stopVoltage.setToolTip('Set the stop voltage for the IV sweep')
        self.ui.lineEdit_voltageStep.setToolTip('Set the voltage step size for the IV sweep')
        self.ui.lineEdit_timeStep.setToolTip('Set the voltage step size for the IV sweep')
        self.ui.lineEdit_numberOfCycles.setToolTip('Set the number of cycles for the IV sweep. For unending IV, set this to 0')

        self.ui.lineEdit_startVoltage.editingFinished.connect(self.lineEdit_startVoltage_editingFinished)
        self.ui.lineEdit_stopVoltage.editingFinished.connect(self.lineEdit_stopVoltage_editingFinished)
        self.ui.lineEdit_voltageStep.editingFinished.connect(self.lineEdit_voltageStep_editingFinished)
        self.ui.lineEdit_timeStep.editingFinished.connect(self.lineEdit_timeStep_editingFinished)
        self.ui.lineEdit_numberOfCycles.editingFinished.connect(self.lineEdit_numberOfCycles_editingFinished)

    def accept(self):
        globalConstants.ADCBITS = self.ADCBITS
        globalConstants.SUBSAMPLINGFACTOR = self.SUBSAMPLINGFACTOR
        globalConstants.REFRESHRATE = self.REFRESHRATE
        globalConstants.ADCSAMPLINGRATE = self.ADCSAMPLINGRATE
        globalConstants.BLOCKLENGTH = self.BLOCKLENGTH
        globalConstants.MBCOMMONMODE = self.MBCOMMONMODE
        globalConstants.FRAMEDURATION = 1000/self.REFRESHRATE
        globalConstants.FRAMELENGTH_MASTER = int((((globalConstants.ADCSAMPLINGRATE*globalConstants.FRAMEDURATION/1000)*4)/4000000. + 0)*4000000)
        globalConstants.FRAMELENGTH_SLAVE = (int((self.ADCSAMPLINGRATE*globalConstants.FRAMEDURATION/1000)*4.0*4/3)/4000000 + 1)*4000000
        globalConstants.PRESETMODE = self.PRESETMODE

        #Make sure start voltage is always smaller than stop voltage
        if self.IVSTARTVOLTAGE > self.IVSTOPVOLTAGE:
            self.IVSTARTVOLTAGE, self.IVSTOPVOLTAGE = self.IVSTOPVOLTAGE, self.IVSTARTVOLTAGE
        globalConstants.IVSTARTVOLTAGE = self.IVSTARTVOLTAGE
        globalConstants.IVSTOPVOLTAGE = self.IVSTOPVOLTAGE
        globalConstants.IVVOLTAGESTEP = self.IVVOLTAGESTEP
        globalConstants.IVTIMESTEP = self.IVTIMESTEP
        globalConstants.IVNUMBEROFCYCLES = self.IVNUMBEROFCYCLES
        self.close()

    def reject(self):
        self.close()

    def lineEdit_ADCBITS_editingFinished(self):
        self.ADCBITS = int(self.ui.lineEdit_ADCBITS.text())
        self.ui.comboBox_presets.setCurrentIndex(0)

    def lineEdit_SUBSAMPLINGFACTOR_editingFinished(self):
        self.SUBSAMPLINGFACTOR = int(self.ui.lineEdit_SUBSAMPLINGFACTOR.text())
        self.ui.comboBox_presets.setCurrentIndex(0)

    def lineEdit_REFRESHRATE_editingFinished(self):
        self.REFRESHRATE = int(self.ui.lineEdit_REFRESHRATE.text())
        self.ui.comboBox_presets.setCurrentIndex(0)

    def lineEdit_ADCSAMPLINGRATE_editingFinished(self):
        self.ADCSAMPLINGRATE = int(self.ui.lineEdit_ADCSAMPLINGRATE.text())
        self.ui.comboBox_presets.setCurrentIndex(0)

    def lineEdit_BLOCKLENGTH_editingFinished(self):
        self.BLOCKLENGTH = int(self.ui.lineEdit_BLOCKLENGTH.text())
        self.ui.comboBox_presets.setCurrentIndex(0)

    def lineEdit_MBCOMMONMODE_editingFinished(self):
        newValue = float(self.ui.lineEdit_MBCOMMONMODE.text())
        newValue = max(newValue, 0)
        newValue = min(newValue, 3.3)
        self.MBCOMMONMODE = newValue

    def comboBox_presets_activated(self, index):
        self.PRESETMODE = index
        if (1 == self.PRESETMODE):
            self.SUBSAMPLINGFACTOR = 10
            self.ui.lineEdit_SUBSAMPLINGFACTOR.setText(str(self.SUBSAMPLINGFACTOR))
            self.REFRESHRATE = 10
            self.ui.lineEdit_REFRESHRATE.setText(str(self.REFRESHRATE))
        elif (2 == self.PRESETMODE):
            self.SUBSAMPLINGFACTOR = 2
            self.ui.lineEdit_SUBSAMPLINGFACTOR.setText(str(self.SUBSAMPLINGFACTOR))
            self.REFRESHRATE = 20
            self.ui.lineEdit_REFRESHRATE.setText(str(self.REFRESHRATE))
        elif (3 == self.PRESETMODE):
            self.SUBSAMPLINGFACTOR = 200
            self.ui.lineEdit_SUBSAMPLINGFACTOR.setText(str(self.SUBSAMPLINGFACTOR))
            self.REFRESHRATE = 2
            self.ui.lineEdit_REFRESHRATE.setText(str(self.REFRESHRATE))

    def lineEdit_startVoltage_editingFinished(self):
        newValue = float(self.ui.lineEdit_startVoltage.text()) + 0.9
        newValue = max(newValue, 0)
        newValue = min(newValue, 1.8)
        self.IVSTARTVOLTAGE = newValue - 0.9

    def lineEdit_stopVoltage_editingFinished(self):
        newValue = float(self.ui.lineEdit_stopVoltage.text()) + 0.9
        newValue = max(newValue, 0)
        newValue = min(newValue, 1.8)
        self.IVSTOPVOLTAGE = newValue - 0.9

    def lineEdit_voltageStep_editingFinished(self):
        newValue = float(self.ui.lineEdit_voltageStep.text())/1000
        newValue = max(newValue, 0.01)
        newValue = min(newValue, abs(self.IVSTOPVOLTAGE - self.IVSTARTVOLTAGE))
        self.IVVOLTAGESTEP = newValue*1000

    def lineEdit_timeStep_editingFinished(self):
        newValue = int(self.ui.lineEdit_timeStep.text())
        newValue = max(newValue, 100)
        newValue = min(newValue, 5000)
        #Make sure that time step is in multiples of 100 ms
        self.IVTIMESTEP = int(round(newValue/100.)) * 100

    def lineEdit_numberOfCycles_editingFinished(self):
        newValue = int(self.ui.lineEdit_numberOfCycles.text())
        newValue = max(newValue, 0)
        self.IVNUMBEROFCYCLES = newValue
