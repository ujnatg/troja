import requests 
import random
import decimal
import minimalmodbus
import time

minimalmodbus.BAUDRATE = 9600

serial_if0 = '/dev/ttyUSB0'
serial_if1 = '/dev/ttyUSB1'

def read_temp(device_id, serial_if):
    instrument = minimalmodbus.Instrument(serial_if, device_id)

    for attempt in range(1, 3):
        # Register number, number of decimals, function code
        try:
            temperature = instrument.read_register(1, 1, 4)
            return temperature
        except:
            print "Error reading data"
            time.sleep(attempt)
    return None 
# api-endpoint 
URL = "https://viber.evvide.com/push_sensor_data"


t1_value = read_temp(1, serial_if0)
if t1_value is None:
    t1_value = read_temp(1, serial_if1)
    if t1_value is None:
        sys.exit("Unable read sensor t1")
else:
    # defining a params dict for the parameters to be sent to the API 
    PARAMS = {'id1':'t1','id2':'t2','id3':'t3','id4':'t4','val1':'{}'.format(t1_value),'val2':'0','val3':'0','val4':'0'} 

# sending get request and saving the response as response object 
r = requests.get(url = URL, params = PARAMS) 
