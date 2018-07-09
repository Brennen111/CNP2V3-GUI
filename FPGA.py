import ok

class FPGA(object):
    def __init__(self, serial, type):
        self.serial = serial
        self.type = type
        self.validColumns = []
        self.configured = False
        self.UpdateWire = False
        self.ActivateTrigger = False
        self.TriggerEndpoint = 0
        self.TriggerBitmask = 0
        return

    def initializeDevice(self, bitfile):
        self.xem = ok.okCFrontPanel()
        if (self.xem.NoError != self.xem.OpenBySerial(self.serial)):
            print "Have you connected the", self.serial, "FPGA?"
            return False

        if (self.xem.NoError != self.xem.ConfigureFPGA(bitfile)):
            print self.serial, "FPGA configuration failed!"
            return False

        if ('Master' == self.type):
            self.validColumns = [0, 1]
        elif ('Slave' == self.type):
            self.validColumns = [2, 3, 4]
        self.configured = True
        self.xem.SetTimeout(500) #Set 0.5s timeout for USB transactions
        #NOTE: The above timeout setting assumes that no USB transaction will take longer than 0.5s
        #Be careful that no data transfers more than a few 10's of MBs are initiated or they will all time out.
        return True

if __name__ == "__main__":
	test = FPGA()
	if (False == test.initializeDevice()):
		exit
