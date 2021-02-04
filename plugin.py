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
<plugin key="SMA" name="SMA Solar Inverter (modbus TCP/IP)" version="0.6.0" author="Derenback">
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

from pyModbusTCP.client import ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import Domoticz

last_saved_total_prod = 0

def get_modbus_value(modbus_id, data_len=2, byteorder=Endian.Big, wordorder=Endian.Big):
    valueread = client.read_holding_registers(modbus_id, data_len)
    value = BinaryPayloadDecoder.fromRegisters(valueread, byteorder, wordorder).decode_32bit_uint()
    if (Parameters["Mode4"] == "Debug"):
        Domoticz.Log("SMA ID: " + str(modbus_id) + " value: " + str(value))
    return value

def onStart():
    global last_saved_total_prod
    Domoticz.Log("Domoticz SMA Inverter Modbus plugin start")

    if (Parameters["Mode3"] == "On"):
        Domoticz.Log("Extended sensors On")
    else:
        Domoticz.Log("Extended sensors Off")
    
    if (Parameters["Mode4"] == "Debug"):
        Domoticz.Log("SMA Debug is On")
        Domoticz.Log("SMA Heartbeat time: " + Parameters["Mode2"])

    if 1 not in Devices:
        Domoticz.Device(Name="Solar Production", Unit=1,Type=0x71,Subtype=0x0,Used=1).Create()
    if 2 not in Devices:
        Domoticz.Device(Name="DC Power A", Unit=2, TypeName="Usage", Used=1).Create()
    if 3 not in Devices:
        Domoticz.Device(Name="DC Power B", Unit=3, TypeName="Usage", Used=1).Create()
    if 4 not in Devices:
        Domoticz.Device(Name="AC Power", Unit=4, TypeName="kWh", Used=1).Create()
    else:
        temp_str = Devices[4].sValue.split(";")
        last_saved_total_prod = int(temp_str[1])
        if (Parameters["Mode4"] == "Debug"):
            Domoticz.Log("SMA restored total production on restart " + str(last_saved_total_prod)) 
    if 5 not in Devices:
        Domoticz.Device(Name="Temperature", Unit=5, TypeName="Temperature", Used=1).Create()
    if (Parameters["Mode3"] == "On"):
        if 6 not in Devices:
            Domoticz.Device(Name="Power L1", Unit=6,TypeName="Usage",Used=1).Create()
        if 7 not in Devices:
            Domoticz.Device(Name="Power L2", Unit=7,TypeName="Usage",Used=1).Create()
        if 8 not in Devices:
            Domoticz.Device(Name="Power L3", Unit=8,TypeName="Usage",Used=1).Create()        
        if 9 not in Devices:
            Domoticz.Device(Name="Voltage L1", Unit=9,TypeName="Voltage",Used=1).Create()
        if 10 not in Devices:
            Domoticz.Device(Name="Voltage L2", Unit=10,TypeName="Voltage",Used=1).Create()
        if 11 not in Devices:
            Domoticz.Device(Name="Voltage L3", Unit=11,TypeName="Voltage",Used=1).Create()  

    try:
        global client
        client = ModbusClient(host=Parameters["Address"], port=Parameters["Port"], unit_id=Parameters["Mode1"])
        client.open()
    except:
        Domoticz.Log("SMA Inverter connection problem");

    Domoticz.Log("SMA Inverter serial number: " + str(get_modbus_value(30057)))

    Domoticz.Heartbeat(int(Parameters["Mode2"]))

def update_device(modbus_id, device_no, divisor=1, decimals=1):
    global last_saved_total_prod
    value = get_modbus_value(modbus_id)
    if modbus_id == 30775:
        total_prod = get_modbus_value(30529) # Solar production total
        if total_prod == 4294967295:
            total_prod = last_saved_total_prod
        last_saved_total_prod = total_prod

    if value == 2147483648:
        value = 0
    if value == 4294967295:
        value = 0    
    
    if divisor == 1:
        if modbus_id == 30775:
            if (Parameters["Mode4"] == "Debug"):
                Domoticz.Log("SMA AC Power: " + str(value) + " Total solar production: " + str(total_prod))
            Devices[device_no].Update(0, str(value) + ";" + str(total_prod))
        else:
            Devices[device_no].Update(0, str(value))
    else:
        Devices[device_no].Update(0, str(round(value / divisor, decimals)))


def onHeartbeat():
    if not client.is_open():
        Domoticz.Log("SMA inverter not connected. Reconnecting...")
        try:
            client.open()
        except:
            Domoticz.Log("SMA Inverter connection problem");
            return

    update_device(30529,  1)         # Solar Production
    update_device(30773,  2)         # DC Power A
    update_device(30961,  3)         # DC Power B
    update_device(30775,  4)         # AC Power + Solar production
    update_device(30953,  5,  10)    # Temperature
    # Extended sensors
    if (Parameters["Mode3"] == "On"):
        update_device(30777,  6)         # Power L1
        update_device(30779,  7)         # Power L2
        update_device(30781,  8)         # Power L3
        update_device(30783,  9, 100, 0) # Voltage L1
        update_device(30785, 10, 100, 0) # Voltage L2
        update_device(30787, 11, 100, 0) # Voltage L3
