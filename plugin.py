#!/usr/bin/env python
"""
SMA Solar Inverter
Author: Derenback
Requirements:
    1. SMA Sunny Tripower or Sunny Boy with Modbus TCP enabled.
    2. python 3.x
    3. pip3 install -U pymodbus pymodbusTCP

"""
"""
<plugin key="SMA" name="SMA Solar Inverter (modbus TCP/IP)" version="1.0.0" author="Derenback">
    <params>
        <param field="Address" label="Your SMA IP Address" width="200px" required="true" default="192.168.0.125"/>
        <param field="Port" label="Port" width="40px" required="true" default="502"/>
        <param field="Mode1" label="Device ID" width="40px" required="true" default="3" />
        <param field="Mode2" label="Reading Interval sec." width="40px" required="true" default="5" />
        <param field="Mode3" label="Extended sensors" width="75px">
            <options>
                <option label="On" value="On" default="true" />
                <option label="Off" value="Off"/>
            </options>
        </param>
        <param field="Mode4" label="Debug" width="75px">
            <options>
                <option label="On" value="Debug"/>
                <option label="Off" value="Off" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
from dataclasses import dataclass
from pyModbusTCP.client import ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import traceback

# Fix for breaking change in pymodbus constants
ENDIAN_BIG = Endian.BIG if hasattr(Endian, 'BIG') else Endian.Big

@dataclass
class device_info:
  address: int
  unit: int
  divisor: int
  decimals: int
  nan: int
  name: str
  device_type: str
  options: str = None

SERIAL_NUMBER_ADDRESS = 30057

U32 = 0xFFFFFFFF
S32 = 0x80000000

devs = []
last_saved_total_prod = 0
connection_has_failed = False
heartbeat = 5
heartbeat_count = 0

def get_modbus_value(modbus_address, data_len=2, byteorder=ENDIAN_BIG, wordorder=ENDIAN_BIG):
    valueread = client.read_holding_registers(modbus_address, data_len)
    value = BinaryPayloadDecoder.fromRegisters(valueread, byteorder, wordorder).decode_32bit_uint()
    if (Parameters["Mode4"] == "Debug"):
        Domoticz.Log("SMA address: " + str(modbus_address) + " value: " + str(value))
    return value

def onStart():
    global devs, last_saved_total_prod, heartbeat
    Domoticz.Log("Domoticz SMA Inverter Modbus plugin start")

    devs.append(    device_info(30529,  1,    1, 1, U32, "Solar Production", "0x71")) 
    devs.append(    device_info(30773,  2,    1, 1, S32, "DC Power A",       "Usage"))
    devs.append(    device_info(30961,  3,    1, 1, S32, "DC Power B",       "Usage"))
    devs.append(    device_info(30775,  4,    1, 1, S32, "AC Power",         "kWh"))
    devs.append(    device_info(30953,  5,   10, 1, S32, "Temperature",      "Temperature"))
    if (Parameters["Mode3"] == "On"):
        devs.append(device_info(30777,  6,    1, 1, S32, "Power L1",          "Usage"))
        devs.append(device_info(30779,  7,    1, 1, S32, "Power L2",          "Usage"))
        devs.append(device_info(30781,  8,    1, 1, S32, "Power L3",          "Usage"))
        devs.append(device_info(30783,  9,  100, 0, U32, "Voltage L1",        "Voltage"))
        devs.append(device_info(30785, 10,  100, 0, U32, "Voltage L2",        "Voltage"))
        devs.append(device_info(30787, 11,  100, 0, U32, "Voltage L3",        "Voltage"))
        devs.append(device_info(30803, 12,  100, 2, U32, "Grid frequency",    "Custom", {'Custom': '1;Hz'}))
        devs.append(device_info(30807, 13,    1, 0, S32, "Reactive power L1", "Custom", {'Custom': '1;VAr'}))
        devs.append(device_info(30809, 14,    1, 0, S32, "Reactive power L2", "Custom", {'Custom': '1;VAr'}))
        devs.append(device_info(30811, 15,    1, 0, S32, "Reactive power L3", "Custom", {'Custom': '1;VAr'}))
        devs.append(device_info(30815, 16,    1, 0, S32, "Apparent power L1", "Custom", {'Custom': '1;VA'}))
        devs.append(device_info(30817, 17,    1, 0, S32, "Apparent power L2", "Custom", {'Custom': '1;VA'}))
        devs.append(device_info(30819, 18,    1, 0, S32, "Apparent power L3", "Custom", {'Custom': '1;VA'}))
        devs.append(device_info(30769, 19, 1000, 3, S32, "Current String A",  "Ampere"))
        devs.append(device_info(30957, 20, 1000, 3, S32, "Current String B",  "Ampere"))
        devs.append(device_info(30771, 21,  100, 0, S32, "Voltage String A",  "Voltage"))
        devs.append(device_info(30959, 22,  100, 0, S32, "Voltage String B",  "Voltage"))

    if (Parameters["Mode3"] == "On"):
        Domoticz.Log("Extended sensors On")
    else:
        Domoticz.Log("Extended sensors Off")
    
    if (Parameters["Mode4"] == "Debug"):
        Domoticz.Log("SMA Debug is On")
        Domoticz.Log("SMA Heartbeat time: " + Parameters["Mode2"])

    if 4 in Devices:       
        temp_str = Devices[4].sValue.split(";")
        last_saved_total_prod = int(float(temp_str[1]))
        if (Parameters["Mode4"] == "Debug"):
            Domoticz.Log("SMA restored total production on restart " + str(last_saved_total_prod)) 

    for dev in devs:
        if dev.unit not in Devices:
            if dev.device_type == "0x71":
                Domoticz.Device(Name=dev.name, Unit=dev.unit,Type=0x71,Subtype=0x0,Used=1).Create()
            elif dev.device_type == "Custom":
                Domoticz.Device(Name=dev.name, Unit=dev.unit,Type=243,Subtype=31,Options=dev.options,Used=1).Create() 
            elif dev.device_type == "Ampere":
                Domoticz.Device(Name=dev.name, Unit=dev.unit,Type=243,Subtype=23,Used=1).Create() 
            else:
                Domoticz.Device(Name=dev.name, Unit=dev.unit, TypeName=dev.device_type, Used=1).Create()

    Domoticz.Heartbeat(1)
    heartbeat = int(Parameters["Mode2"])

    try:
        global client
        client = ModbusClient(host=Parameters["Address"], port = int(Parameters["Port"]), unit_id=int(Parameters["Mode1"]))
        client.open()
        Domoticz.Log("SMA Inverter serial number: " + str(get_modbus_value(SERIAL_NUMBER_ADDRESS)))        
    except:
        Domoticz.Log("SMA failed to connect to inverter")
        Domoticz.Log(traceback.print_exc())

def update_device(dev):
    global last_saved_total_prod
    if dev.unit in Devices:
        value = get_modbus_value(dev.address)

        if dev.unit == 1:
            if value == dev.nan:
                value = last_saved_total_prod
            else:
                last_saved_total_prod = value
        else:
            if value == dev.nan:
                value = 0
        
        # Handle negative numbers
        if dev.nan == S32:
            if value > S32:
                value = value - (U32 + 1)
        
        if dev.divisor == 1:
            if dev.unit == 4:
                if (Parameters["Mode4"] == "Debug"):
                    Domoticz.Log("SMA AC Power: " + str(value) + " Total solar production: " + str(last_saved_total_prod))
                Devices[dev.unit].Update(0, str(value) + ";" + str(last_saved_total_prod))
            else:
                Devices[dev.unit].Update(0, str(value))
        else:
            Devices[dev.unit].Update(0, str(round(value / dev.divisor, dev.decimals)))


def onHeartbeat():
    global connection_has_failed, heartbeat_count
    if heartbeat_count > 1:
        heartbeat_count -= 1
    else:
        heartbeat_count = heartbeat
        if not client.is_open or connection_has_failed:
            Domoticz.Log("SMA inverter not connected. Reconnecting...")
            try:
                connection_has_failed = False
                client.close()
                client.open()
            except:
                Domoticz.Log("SMA failed to connect to inverter")
                Domoticz.Log(traceback.print_exc())
        else:
            try:
                for dev in devs:
                    update_device(dev)
            except:
                connection_has_failed = True
                Domoticz.Log("SMA Failed to read data")
                Domoticz.Log(traceback.print_exc())


