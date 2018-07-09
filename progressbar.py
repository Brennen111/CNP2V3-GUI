from PyQt4 import QtCore, QtGui
from progressBarWindow_gui import Ui_Dialog

class ProgressBarWindow(QtGui.QDialog):
    def __init__(self, maximum=10):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.progressBar.setRange(0, maximum)
        self.ui.progressBar.setValue(0)

        self.oldValue = 0

    def updateValue(self, value=0, text=''):
        self.oldValue += value
        self.ui.progressBar.setFormat(text + ' ' + str(int(self.oldValue*100.0/self.ui.progressBar.maximum())) + '%')
        self.ui.progressBar.setValue(self.oldValue)
