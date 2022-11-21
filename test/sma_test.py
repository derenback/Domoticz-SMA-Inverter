#!/usr/bin/env python3
from ipaddress import ip_address
from pyModbusTCP.client import ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import argparse

parser = argparse.ArgumentParser(description="Test the connection to your SMA inverter.")
parser.add_argument("ip_address", nargs="?", type=ip_address, default="192.168.0.125", help="Default: 192.168.0.125")
parser.add_argument("port", nargs="?", type=int, default=502, help="Default: 502")
parser.add_argument("unit_id", nargs="?", type=int, default=3, help="Default: 3")
args = parser.parse_args()
print(f"Connecting to IP: {args.ip_address}")
print(f"Port: {args.port}")
print(f"Unit id: {args.unit_id}")
print("")

def get_modbus_value(modbus_id, print_str, unit="", divider=1, data_len=2, byteorder=Endian.Big, wordorder=Endian.Big):
    valueread = client.read_holding_registers(modbus_id, data_len)
    value = BinaryPayloadDecoder.fromRegisters(valueread, byteorder, wordorder).decode_32bit_uint()
    if divider == 1:
        print(print_str, value, unit)
    else:
        print(print_str, round(value / divider, 2), unit)
    return value

client = ModbusClient(str(args.ip_address), args.port, args.unit_id)
client.open()

if client.is_open:
    get_modbus_value(30057, "Serial number")
    get_modbus_value(30053, "Device type")
    get_modbus_value(30231, "Maximum active power device","kW", 1000)
    get_modbus_value(30541, "Operating time", "h", 3600)
    get_modbus_value(30225, "Insulation resistance", "kOhm", 1000)
    get_modbus_value(30803, "Grid frequency", "Hz", 100)

    print(" ")

    get_modbus_value(30529, "Total production", "kWh", 1000)
    get_modbus_value(30535, "Production today", "kWh", 1000)
    print(" ")
    print("Side A")
    get_modbus_value(30773, "DC Power", "W")
    get_modbus_value(30769, "DC Current", "A")
    get_modbus_value(30771, "DC Voltage", "V", 100)
    print(" ")
    print("Side B")
    get_modbus_value(30961, "DC Power", "W")
    get_modbus_value(30957, "DC Current", "A")
    get_modbus_value(30959, "DC Voltage", "V", 100)
    print(" ")
    get_modbus_value(30775, "AC Power", "W")
    get_modbus_value(30777, "Power L1", "W")
    get_modbus_value(30779, "Power L2", "W")
    get_modbus_value(30781, "Power L3", "W")
    print(" ")
    get_modbus_value(30953, "Temperature", "C", 10)
    print(" ")
    get_modbus_value(30783, "Grid voltage phase L1", "V", 100)
    get_modbus_value(30785, "Grid voltage phase L2", "V", 100)
    get_modbus_value(30787, "Grid voltage phase L3", "V", 100)
    print(" ")
    get_modbus_value(30795, "Grid Current", "A")

    client.close()

