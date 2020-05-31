import requests
import random
import decimal
import minimalmodbus
import time
import traceback

minimalmodbus.TIMEOUT = 5
minimalmodbus.BAUDRATE = 9600

modbus_debug = False

serial_if0 = '/dev/ttyUSB0'
serial_if1 = '/dev/ttyUSB1'
prefered_if = None

temperature_devices_modbus = [
    {
        'id': 10,
        'registers': [{'address': 1, 'decimal': 1, 'description': 'T', 'operation_type': 4, 'signed': True},
                      {'address': 2, 'decimal': 1, 'description': 'H', 'operation_type': 4, 'signed': True}],
        'location': 'Salad dalnij verhnij 10'
    },
    {
        'id': 11,
        'registers': [{'address': 1, 'decimal': 1, 'description': 'Temperature', 'operation_type': 4, 'signed': True},
                      {'address': 2, 'decimal': 1, 'description': 'Humidity', 'operation_type': 4, 'signed': True}],
        'location': 'Salad blignij nignij 11'
    },
    {
        'id': 12,
        'registers': [{'address': 1, 'decimal': 1, 'description': 'Temp', 'operation_type': 4, 'signed': True},
                      {'address': 2, 'decimal': 1, 'description': 'Hum', 'operation_type': 4, 'signed': True}],
        'location': 'Salad srednij 12'
    }
]


def read_data(device_id, register_packet):
    print("Trying read from line {} address {}".format(prefered_if, device_id))
    instrument = minimalmodbus.Instrument(prefered_if, device_id)
    instrument.debug = modbus_debug

    register_address = register_packet['address']
    register_decimal = register_packet['decimal']
    register_operation_type = register_packet['operation_type']
    register_signed = register_packet['signed']
    for attempt in range(1, 2):
        # Register number, number of decimals, function code
        try:
            print(
                "Reading attempt #{} device_id:{} register_address:{} register_decimal:{} register_operation_type:{} register_signed:{}".format(
                    attempt, device_id, register_address, register_decimal, register_operation_type, register_signed))
            register_data = instrument.read_register(register_address, register_decimal, register_operation_type,
                                                     signed=register_signed)

            print("Result for #{} is {}".format(attempt, register_data))
            return register_data
        except:
            traceback.print_exc()
            print("Error reading data")
            time.sleep(attempt)
    return None


def read_temp(device_id, serial_if):
    try:
        print("Trying read from line {} address {}".format(serial_if, device_id))
        instrument = minimalmodbus.Instrument(serial_if, device_id)
        instrument.debug = modbus_debug
    # instrument.precalculate_read_size = False
    except:
        print("Unable initialize device: {} on {}".format(device_id, serial_if))
        return None
    for attempt in range(1, 3):
        # Register number, number of decimals, function code
        try:
            print("#{}".format(attempt))
            temperature = instrument.read_register(1, 1, 4, signed=True)
            print("Result for #{} is {}".format(attempt, temperature))
            return temperature
        except:
            traceback.print_exc()
            print("Error reading data")
            time.sleep(attempt)
    return None


def get_modbus_device():
    try:
        instrument = minimalmodbus.Instrument(serial_if0, 1)
        instrument.debug = True
        return serial_if0
    except:
        print("Not found. Searching for RS485 on {}".format(serial_if1))
        instrument = minimalmodbus.Instrument(serial_if1, 1)
        instrument.debug = True
        return serial_if1


# api-endpoint
URL = "https://viber.evvide.com/push_sensor_data2"

response = []

prefered_if = get_modbus_device()
print
"Prefered Serial interface: {}".format(prefered_if)
for device in temperature_devices_modbus:
    device_address = device['id']
    for register in device['registers']:
        register_value = read_data(device_address, register)
        register['value'] = register_value
        register['device_address'] = device_address
        register['location'] = device['location'] 
        response.append(register)
        print
        response

# sending get request and saving the response as response object
r = requests.post(url=URL, json=response)
