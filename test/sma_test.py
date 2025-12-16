#!/usr/bin/env python3
"""
Simple test script to verify connectivity to an SMA inverter via Modbus TCP.

This script reads various registers from the inverter and displays their values.
No pymodbus dependency required - uses only pyModbusTCP and standard library.
"""
import argparse
import struct
from ipaddress import ip_address

from pyModbusTCP.client import ModbusClient


def decode_u32_from_registers(registers):
    """
    Decode a 32-bit unsigned integer from two 16-bit Modbus registers.

    Uses big-endian byte order and big-endian word order (high word first),
    which is standard for SMA inverters.

    Args:
        registers: List of two 16-bit register values [high_word, low_word]

    Returns:
        32-bit unsigned integer value
    """
    if registers is None or len(registers) < 2:
        raise ValueError("Invalid register data: expected 2 registers")

    # Pack as two big-endian unsigned shorts, then unpack as big-endian unsigned int
    packed = struct.pack(">HH", registers[0], registers[1])
    return struct.unpack(">I", packed)[0]


def get_modbus_value(client, modbus_id, print_str, unit="", divider=1, data_len=2):
    """Read a value from the inverter and print it."""
    valueread = client.read_holding_registers(modbus_id, data_len)
    value = decode_u32_from_registers(valueread)
    if divider == 1:
        print(print_str, value, unit)
    else:
        print(print_str, round(value / divider, 2), unit)
    return value


def main():
    parser = argparse.ArgumentParser(description="Test the connection to your SMA inverter.")
    parser.add_argument(
        "ip_address",
        nargs="?",
        type=ip_address,
        default="192.168.0.125",
        help="Default: 192.168.0.125",
    )
    parser.add_argument("port", nargs="?", type=int, default=502, help="Default: 502")
    parser.add_argument("unit_id", nargs="?", type=int, default=3, help="Default: 3")
    args = parser.parse_args()

    print(f"Connecting to IP: {args.ip_address}")
    print(f"Port: {args.port}")
    print(f"Unit id: {args.unit_id}")
    print("")

    client = ModbusClient(str(args.ip_address), args.port, args.unit_id)
    client.open()

    if client.is_open:
        get_modbus_value(client, 30057, "Serial number")
        get_modbus_value(client, 30053, "Device type")
        get_modbus_value(client, 30231, "Maximum active power device", "kW", 1000)
        get_modbus_value(client, 30541, "Operating time", "h", 3600)
        get_modbus_value(client, 30225, "Insulation resistance", "kOhm", 1000)
        get_modbus_value(client, 30803, "Grid frequency", "Hz", 100)
        get_modbus_value(client, 30529, "Total production", "kWh", 1000)
        get_modbus_value(client, 30535, "Production today", "kWh", 1000)
        get_modbus_value(client, 30773, "Side A DC Power", "W")
        get_modbus_value(client, 30769, "Side A DC Current", "A")
        get_modbus_value(client, 30771, "Side A DC Voltage", "V", 100)
        get_modbus_value(client, 30961, "Side B DC Power", "W")
        get_modbus_value(client, 30957, "Side B DC Current", "A")
        get_modbus_value(client, 30959, "Side B DC Voltage", "V", 100)
        get_modbus_value(client, 30775, "AC Power", "W")
        get_modbus_value(client, 30777, "Power L1", "W")
        get_modbus_value(client, 30779, "Power L2", "W")
        get_modbus_value(client, 30781, "Power L3", "W")
        get_modbus_value(client, 30953, "Temperature", "C", 10)
        get_modbus_value(client, 30783, "Grid voltage phase L1", "V", 100)
        get_modbus_value(client, 30785, "Grid voltage phase L2", "V", 100)
        get_modbus_value(client, 30787, "Grid voltage phase L3", "V", 100)
        get_modbus_value(client, 30795, "Grid Current", "A")

        client.close()
    else:
        print("ERROR: Failed to connect to inverter")


if __name__ == "__main__":
    main()

