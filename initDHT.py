import minimalmodbus
import time

minimalmodbus.BAUDRATE = 9600

# port name, slave address (in decimal)
minimalmodbus.TIMEOUT = 5
initial_address = 1
new_address=12

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', initial_address)

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
print 'Hum adjustment'
print hadj



print 'Configuring address to:'
print new_address

instrument.write_register(0x101, new_address, 0, 0x6)
time.sleep(10)
print 'Initializing on new address'
minimalmodbus.TIMEOUT = 5
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', new_address)

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
print 'Hum adjustment'
print hadj
