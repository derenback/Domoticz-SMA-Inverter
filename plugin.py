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
<plugin key="SMA" name="SMA Solar Inverter (modbus TCP/IP)" version="0.8.0" author="Derenback">
    <params>
        <param field="Address" label="Your SMA IP Address" width="200px" required="true" default="192.168.0.125"/>
        <param field="Port" label="Port" width="40px" required="true" default="502"/>
        <param field="Mode1" label="Device ID" width="40px" required="true" default="3" />
        <param field="Mode2" label="Reading Interval sec." width="40px" required="true" default="5" />
        <param field="Voltage" label="Phase Voltage" width="75px">
            <options>
                <option label="True" value="1" default="true"/>
                <option label="False" value="0"/>
            </options>
        </param>
    </params>
</plugin>
"""

from pyModbusTCP.client import ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import Domoticz

def onStart():
    Domoticz.Log("Domoticz SMA Inverter Modbus plugin start")

    if 1 not in Devices:
        Domoticz.Device(Name="Solar Production", Unit=1,Type=0x71,Subtype=0x0,Used=0).Create()
    if 2 not in Devices:
        Domoticz.Device(Name="DC Power A", Unit=2, TypeName="Usage", Used=0).Create()
    if 3 not in Devices:
        Domoticz.Device(Name="DC Power B", Unit=3, TypeName="Usage", Used=0).Create()
    if 4 not in Devices:
        Domoticz.Device(Name="AC Power", Unit=4, TypeName="Usage", Used=0).Create()
    if 5 not in Devices:
        Domoticz.Device(Name="Temperature", Unit=5, TypeName="Temperature", Used=0).Create()
    if 6 not in Devices:
        Domoticz.Device(Name="Power L1", Unit=6,TypeName="Usage",Used=0).Create()
    if 7 not in Devices:
        Domoticz.Device(Name="Power L2", Unit=7,TypeName="Usage",Used=0).Create()
    if 8 not in Devices:
        Domoticz.Device(Name="Power L3", Unit=8,TypeName="Usage",Used=0).Create()        
    if Parameters["Voltage"] == 1:
        if 9 not in Devices:
            Domoticz.Device(Name="Voltage L1", Unit=9,TypeName="Voltage",Used=0).Create()
        if 10 not in Devices:
            Domoticz.Device(Name="Voltage L2", Unit=10,TypeName="Voltage",Used=0).Create()
        if 11 not in Devices:
            Domoticz.Device(Name="Voltage L3", Unit=11,TypeName="Voltage",Used=0).Create()  

    global client
    client = ModbusClient(host=Parameters["Address"], port=Parameters["Port"], unit_id=Parameters["Mode1"])
    client.open()

    Domoticz.Heartbeat(int(Parameters["Mode2"]))

def update_device(modbus_id, device_no, divisor=1):
    value_read = client.read_holding_registers(modbus_id, 2)
    value = BinaryPayloadDecoder.fromRegisters(value_read, byteorder=Endian.Big, wordorder=Endian.Big).decode_32bit_uint()

    if value == 2147483648:
        value = 0
    
    if divisor == 1:
        Devices[device_no].Update(0, str(value))
    else:
        Devices[device_no].Update(0, str(value / divisor))


def onHeartbeat():
    if not client.is_open():
        Domoticz.Log("Not connected. Reconnecting...")
        client.open()
        return

    update_device(30529,1)      # Solar Production
    update_device(30773,2)      # DC Power A
    update_device(30961,3)      # DC Power B
    update_device(30775,4)      # AC Power
    update_device(30953,5,10)   # Temperature
    update_device(30777,6)      # Power L1
    update_device(30779,7)      # Power L2
    update_device(30781,8)      # Power L3
    if Parameters["Voltage"] == 1:
        update_device(30783,9)      # Voltage L1
        update_device(30785,10)     # Voltage L2
        update_device(30787,11)     # Voltage L3
