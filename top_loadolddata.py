# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from loadolddata import LoadOldDataWindow
import sys
import sip
import platform

def f(x):
    return x**(x+1)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    if (platform.system() == 'Linux'):
        app.setStyle('Plastique')
    # FPGAMasterInstance = FPGA('13430005WX')
    # FPGASlaveInstance = FPGA('1447000A5T')
    # FPGASlaveInstance = FPGA('14230007A8')
    # FPGASlaveInstance = FPGA('14120001WJ') #David's Opal Kelly
    # if (False == FPGAMasterInstance.initializeDevice('top_40M2222.bit')):
    # 	sys.exit("Check the power supply to the FPGAs and the USB cables!")
    # # if (False == FPGASlaveInstance.initializeDevice('top_slave_40M22.bit')):
    # if (False == FPGASlaveInstance.initializeDevice('top_slave_test.bit')):
    # 	sys.exit()
    window = LoadOldDataWindow()
    window.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
    window.show()
    sip.setdestroyonexit(False) #Added to remove program crash on close bug
    sys.exit(app.exec_())
