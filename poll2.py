import requests
import random
import decimal
import minimalmodbus
import time

minimalmodbus.TIMEOUT = 5
minimalmodbus.BAUDRATE = 9600

serial_if0 = '/dev/ttyUSB0'
serial_if1 = '/dev/ttyUSB1'
temperature_devices_modbus = [
    {
        'address': 10,
        'register': 1,
        'decimal': 1,
        'location_machine': 'Salad01',
        'location_human': 'Salad01',
        'mapped_name': 't1'
    },
    {
        'address': 11,
        'register': 1,
        'decimal': 1,
        'location_machine': 'Salad02',
        'location_human': 'Salahjhbjhbjhbd01',
        'mapped_name': 't1'
    },
    {

        'address': 12,
        'register': 1,
        'decimal': 1,
        'location_machine': 'Cucumber03',
        'location_human': 'Sal jbjbjhbjad01',
    }
]


def read_temp(device_id, serial_if):
    instrument = minimalmodbus.Instrument(serial_if, device_id)

    for attempt in range(1, 3):
        # Register number, number of decimals, function code
        try:
            temperature = instrument.read_register(1, 1, 4)
            return temperature
        except:
            print
            "Error reading data"
            time.sleep(attempt)
    return None


# api-endpoint
URL = "https://viber.evvide.com/push_sensor_data2"

temp_sensors_data = []
for device in temperature_devices_modbus:
    device_value = read_temp(1, serial_if0)
    if device_value is None:
        device_value = read_temp(1, serial_if1)
        if device_value is None:
            print("Unable read sensor t1")
            break
    temp_sensors_data.append(
        {
            'value':device_value,
            'type': 'temprature',
            'location_machine': device['location_machine'],
            'location_human': device['location_human'],
        }
    )

# sending get request and saving the response as response object
r = requests.post(url=URL, json=temp_sensors_data)
