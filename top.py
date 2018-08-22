# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from mainwindow import MainWindow
import sys
import sip
import platform
import FPGA

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
    window = MainWindow()
    window.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

    window.show() # Show all widgets
    width = window.ui.centralwidget.width()
    window.ui.verticalWidget_rowPlotPlots.hide() # Hide side plots widget
    window.ui.verticalWidget_rowPlotData.hide()  # Hide side data widget
    app.sendPostedEvents() # There is a delay before the widget size updates in the data structures. This adds a delay for the Qt framework to update all data structures
    window.ui.centralwidget.layout().setSizeConstraint(window.ui.centralwidget.layout().SetMinimumSize) # Updates the sizeHint() of the central widget to the new minimum size
    window.ui.centralwidget.adjustSize() # Resize the central widget to its hint (0,0). This is not necessary from what I can see
    window.adjustSize() # Tells the mainWindow widget to resize to its hint (0,0)
    window.setFixedWidth(window.width()) # Fixes the width so the gui cannot be expanded horizonatally in its startup state.

    sip.setdestroyonexit(False) # Added to remove program crash on close bug
    sys.exit(app.exec_())
