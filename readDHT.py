import minimalmodbus
import time

minimalmodbus.BAUDRATE = 9600

# port name, slave address (in decimal)
minimalmodbus.TIMEOUT = 5
initial_address = 11

instrument = minimalmodbus.Instrument('/dev/ttyUSB1', initial_address)

address = instrument.read_register(0x101, 0, 3)
speed = instrument.read_register(0x102, 0, 3)
tadj = instrument.read_register(0x103, 1, 3)
hadj = instrument.read_register(0x104, 1, 3)

print 'Holding registers'
print 'Address:'
print address
print 'Speed'
print speed
print 'Temp adjustment'
print tadj
