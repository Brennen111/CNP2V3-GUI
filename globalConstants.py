# -*- coding: utf-8 -*-

masterSerial = '1817000M4C'
slaveSerial = '1817000LYB'

ADCBITS = 12
SUBSAMPLINGFACTOR = 10
REFRESHRATE = 10 # in frames per second
AAFILTERGAIN = (51+620)/620.0*1.8*.51
ADCSAMPLINGRATE = 4000000
FRAMEDURATION = 1000/REFRESHRATE
FRAMELENGTH_MASTER = int((((ADCSAMPLINGRATE*FRAMEDURATION/1000)*4)/4000000. + 0)*4000000) # Multiplied by 4 because of the specific FPGA data packing implementation
FRAMELENGTH_SLAVE = (int((ADCSAMPLINGRATE*FRAMEDURATION/1000)*4*4.0/3)/4000000 + 1)*4000000 #Slave data is packed with 3/4 efficiency
# BLOCKLENGTH = 1024
BLOCKLENGTH = 256 # While transferring data from the FPGA, the transaction is broken up into blocks of this length (in bytes)
MBCOMMONMODE = 1.65 # Nominal common mode voltage for the motherboard is 1.65 V
PRESETMODE = 1
SQUAREWAVEAMPLITUDE = 0.9
IVSTARTVOLTAGE = -0.5
IVSTOPVOLTAGE = 0.5
IVVOLTAGESTEP = 100
IVTIMESTEP = 500
IVNUMBEROFCYCLES = 0

CMDQUEUEWIRE   = 0
CMDUPDATEWIRE  = 1
CMDTRIGGERWIRE = 2

# dictOfConstants = {'ADCBITS':ADCBITS, 'SUBSAMPLINGFACTOR': SUBSAMPLINGFACTOR, 'REFRESHRATE': REFRESHRATE, 'AAFILTERGAIN': AAFILTERGAIN, 'ADCSAMPLINGRATE': ADCSAMPLINGRATE, 'FRAMEDURATION': FRAMEDURATION, 'FRAMELENGTH_MASTER': FRAMELENGTH_MASTER, 'FRAMELENGTH_SLAVE': FRAMELENGTH_SLAVE, 'BLOCKLENGTH': BLOCKLENGTH, 'MBCOMMONMODE': MBCOMMONMODE, 'SQUAREWAVEAMPLITUDE': SQUAREWAVEAMPLITUDE, 'PRESETMODE': PRESETMODE, 'IVSTARTVOLTAGE': IVSTARTVOLTAGE, 'IVSTOPVOLTAGE': IVSTOPVOLTAGE, 'IVVOLTAGESTEP': IVVOLTAGESTEP, 'IVTIMESTEP': IVTIMESTEP, 'IVNUMBEROFCYCLES': IVNUMBEROFCYCLES, 'CMDQUEUEWIRE': CMDQUEUEWIRE, 'CMDUPDATEWIRE': CMDUPDATEWIRE, 'CMDTRIGGERWIRE': CMDTRIGGERWIRE}
