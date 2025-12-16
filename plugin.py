#!/usr/bin/env python
"""
SMA Solar Inverter Plugin for Domoticz.

Author: Derenback
Requirements:
    1. SMA Sunny Tripower or Sunny Boy with Modbus TCP enabled.
    2. Python 3.x
    3. pip3 install -U pymodbusTCP
"""
"""
<plugin key="SMA" name="SMA Solar Inverter (modbus TCP/IP)" version="1.3.0" author="Derenback">
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
        <param field="Mode5" label="Battery sensors" width="75px">
            <options>
                <option label="On" value="On"/>
                <option label="Off" value="Off" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""

import struct
import traceback
from dataclasses import dataclass
from typing import Dict, List, Optional

import Domoticz
from pyModbusTCP.client import ModbusClient

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SERIAL_NUMBER_ADDRESS = 30057

# NaN marker values for Modbus registers
U32_NAN = 0xFFFFFFFF
S32_NAN = 0x80000000


# ---------------------------------------------------------------------------
# Register Decoding Utilities
# ---------------------------------------------------------------------------


def decode_u32_from_registers(registers: List[int]) -> int:
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
    # Word order: high word first (registers[0]), low word second (registers[1])
    packed = struct.pack(">HH", registers[0], registers[1])
    return struct.unpack(">I", packed)[0]


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DeviceInfo:
    """Configuration for a single SMA sensor device."""

    address: int
    unit: int
    divisor: int
    decimals: int
    nan: int
    name: str
    device_type: str
    options: Optional[Dict[str, str]] = None


# ---------------------------------------------------------------------------
# Sensor Definitions
# ---------------------------------------------------------------------------

CORE_SENSORS = (
    DeviceInfo(30529, 1, 1, 1, U32_NAN, "Solar Production", "0x71"),
    DeviceInfo(30773, 2, 1, 1, S32_NAN, "DC Power A", "Usage"),
    DeviceInfo(30961, 3, 1, 1, S32_NAN, "DC Power B", "Usage"),
    DeviceInfo(30775, 4, 1, 1, S32_NAN, "AC Power", "kWh"),
    DeviceInfo(30953, 5, 10, 1, S32_NAN, "Temperature", "Temperature"),
)

EXTENDED_SENSORS = (
    DeviceInfo(30777, 6, 1, 1, S32_NAN, "Power L1", "Usage"),
    DeviceInfo(30779, 7, 1, 1, S32_NAN, "Power L2", "Usage"),
    DeviceInfo(30781, 8, 1, 1, S32_NAN, "Power L3", "Usage"),
    DeviceInfo(30783, 9, 100, 0, U32_NAN, "Voltage L1", "Voltage"),
    DeviceInfo(30785, 10, 100, 0, U32_NAN, "Voltage L2", "Voltage"),
    DeviceInfo(30787, 11, 100, 0, U32_NAN, "Voltage L3", "Voltage"),
    DeviceInfo(30803, 12, 100, 2, U32_NAN, "Grid frequency", "Custom", {"Custom": "1;Hz"}),
    DeviceInfo(30807, 13, 1, 0, S32_NAN, "Reactive power L1", "Custom", {"Custom": "1;VAr"}),
    DeviceInfo(30809, 14, 1, 0, S32_NAN, "Reactive power L2", "Custom", {"Custom": "1;VAr"}),
    DeviceInfo(30811, 15, 1, 0, S32_NAN, "Reactive power L3", "Custom", {"Custom": "1;VAr"}),
    DeviceInfo(30815, 16, 1, 0, S32_NAN, "Apparent power L1", "Custom", {"Custom": "1;VA"}),
    DeviceInfo(30817, 17, 1, 0, S32_NAN, "Apparent power L2", "Custom", {"Custom": "1;VA"}),
    DeviceInfo(30819, 18, 1, 0, S32_NAN, "Apparent power L3", "Custom", {"Custom": "1;VA"}),
    DeviceInfo(30769, 19, 1000, 3, S32_NAN, "Current String A", "Ampere"),
    DeviceInfo(30957, 20, 1000, 3, S32_NAN, "Current String B", "Ampere"),
    DeviceInfo(30771, 21, 100, 0, S32_NAN, "Voltage String A", "Voltage"),
    DeviceInfo(30959, 22, 100, 0, S32_NAN, "Voltage String B", "Voltage"),
)

BATTERY_SENSORS = (
    DeviceInfo(30849, 23, 10, 1, S32_NAN, "Battery Temperature", "Temperature"),
    DeviceInfo(30845, 24, 1, 1, S32_NAN, "Battery State of Charge", "Percentage"),
    DeviceInfo(30867, 25, 1, 1, S32_NAN, "Battery Grid Feed-In Power", "kWh"),
    DeviceInfo(30865, 26, 1, 1, S32_NAN, "Battery Grid Supplied Power", "kWh"),
)

# Unit IDs with special handling
UNIT_SOLAR_PRODUCTION = 1
UNIT_AC_POWER = 4


# ---------------------------------------------------------------------------
# Plugin State
# ---------------------------------------------------------------------------


class SMAInverterPlugin:
    """Encapsulates all plugin state and logic."""

    def __init__(self) -> None:
        self.client: Optional[ModbusClient] = None
        self.devices: List[DeviceInfo] = []
        self.last_saved_total_prod: int = 0
        self.connection_failed: bool = False
        self.heartbeat_interval: int = 5
        self.heartbeat_counter: int = 0

    # -----------------------------------------------------------------------
    # Properties for cleaner config access
    # -----------------------------------------------------------------------

    @property
    def debug_enabled(self) -> bool:
        return Parameters["Mode4"] == "Debug"

    @property
    def extended_sensors_enabled(self) -> bool:
        return Parameters["Mode3"] == "On"

    @property
    def battery_sensors_enabled(self) -> bool:
        return Parameters["Mode5"] == "On"

    # -----------------------------------------------------------------------
    # Logging helpers
    # -----------------------------------------------------------------------

    def log(self, message: str) -> None:
        """Log a message to Domoticz."""
        Domoticz.Log(message)

    def log_debug(self, message: str) -> None:
        """Log a debug message (only if debug is enabled)."""
        if self.debug_enabled:
            Domoticz.Log(message)

    def log_error(self, message: str) -> None:
        """Log an error with traceback."""
        Domoticz.Log(message)
        Domoticz.Log(str(traceback.format_exc()))

    # -----------------------------------------------------------------------
    # Modbus Communication
    # -----------------------------------------------------------------------

    def read_modbus_value(self, address: int, data_len: int = 2) -> int:
        """
        Read a 32-bit unsigned value from a Modbus register.

        Args:
            address: The Modbus register address to read from
            data_len: Number of 16-bit registers to read (default: 2 for 32-bit)

        Returns:
            32-bit unsigned integer value from the registers
        """
        registers = self.client.read_holding_registers(address, data_len)
        value = decode_u32_from_registers(registers)
        self.log_debug(f"SMA address: {address} value: {value}")
        return value

    def connect(self) -> bool:
        """Establish connection to the SMA inverter."""
        try:
            self.client = ModbusClient(
                host=Parameters["Address"],
                port=int(Parameters["Port"]),
                unit_id=int(Parameters["Mode1"]),
            )
            self.client.open()
            serial = self.read_modbus_value(SERIAL_NUMBER_ADDRESS)
            self.log(f"SMA Inverter serial number: {serial}")
            return True
        except Exception:
            self.log_error("SMA failed to connect to inverter")
            return False

    def reconnect(self) -> bool:
        """Attempt to reconnect to the inverter."""
        try:
            self.connection_failed = False
            if self.client:
                self.client.close()
                self.client.open()
            return True
        except Exception:
            self.log_error("SMA failed to connect to inverter")
            return False

    # -----------------------------------------------------------------------
    # Device Management
    # -----------------------------------------------------------------------

    def _build_device_list(self) -> None:
        """Build the list of devices based on configuration."""
        self.devices = list(CORE_SENSORS)

        if self.extended_sensors_enabled:
            self.log("Extended sensors On")
            self.devices.extend(EXTENDED_SENSORS)
        else:
            self.log("Extended sensors Off")

        if self.battery_sensors_enabled:
            self.log("Battery sensors On")
            self.devices.extend(BATTERY_SENSORS)
        else:
            self.log("Battery sensors Off")

    def _create_domoticz_device(self, dev: DeviceInfo) -> None:
        """Create a Domoticz device for the given DeviceInfo."""
        if dev.unit in Devices:
            return

        device_creators = {
            "0x71": lambda: Domoticz.Device(
                Name=dev.name, Unit=dev.unit, Type=0x71, Subtype=0x0, Used=1
            ).Create(),
            "Custom": lambda: Domoticz.Device(
                Name=dev.name, Unit=dev.unit, Type=243, Subtype=31, Options=dev.options, Used=1
            ).Create(),
            "Ampere": lambda: Domoticz.Device(
                Name=dev.name, Unit=dev.unit, Type=243, Subtype=23, Used=1
            ).Create(),
            "Percentage": lambda: Domoticz.Device(
                Name=dev.name, Unit=dev.unit, Type=243, Subtype=6, Used=1
            ).Create(),
        }

        creator = device_creators.get(dev.device_type)
        if creator:
            creator()
        else:
            Domoticz.Device(Name=dev.name, Unit=dev.unit, TypeName=dev.device_type, Used=1).Create()

    def _restore_total_production(self) -> None:
        """Restore total production value from existing device."""
        if UNIT_AC_POWER not in Devices:
            return

        try:
            svalue = Devices[UNIT_AC_POWER].sValue.split(";")
            self.last_saved_total_prod = int(float(svalue[1]))
            self.log_debug(f"SMA restored total production on restart {self.last_saved_total_prod}")
        except (IndexError, ValueError):
            pass

    # -----------------------------------------------------------------------
    # Value Processing
    # -----------------------------------------------------------------------

    def _process_raw_value(self, dev: DeviceInfo, raw_value: int) -> int:
        """Process a raw Modbus value, handling NaN and sign conversion."""
        value = raw_value

        # Handle NaN values
        if dev.unit == UNIT_SOLAR_PRODUCTION:
            if value == dev.nan:
                value = self.last_saved_total_prod
            else:
                self.last_saved_total_prod = value
        elif value == dev.nan:
            value = 0

        # Convert unsigned to signed for S32 values
        if dev.nan == S32_NAN and value > S32_NAN:
            value = value - (U32_NAN + 1)

        return value

    def _format_device_value(self, dev: DeviceInfo, value: int) -> str:
        """Format the value for Domoticz device update."""
        if dev.unit == UNIT_AC_POWER:
            self.log_debug(
                f"SMA AC Power: {value} Total solar production: {self.last_saved_total_prod}"
            )
            return f"{value};{self.last_saved_total_prod}"

        if dev.divisor == 1:
            return str(value)

        return str(round(value / dev.divisor, dev.decimals))

    def update_device(self, dev: DeviceInfo) -> None:
        """Read and update a single device."""
        if dev.unit not in Devices:
            return

        raw_value = self.read_modbus_value(dev.address)
        processed_value = self._process_raw_value(dev, raw_value)
        formatted_value = self._format_device_value(dev, processed_value)
        Devices[dev.unit].Update(0, formatted_value)

    def update_all_devices(self) -> None:
        """Update all configured devices."""
        for dev in self.devices:
            self.update_device(dev)

    # -----------------------------------------------------------------------
    # Plugin Lifecycle
    # -----------------------------------------------------------------------

    def on_start(self) -> None:
        """Initialize the plugin."""
        self.log("Domoticz SMA Inverter Modbus plugin start")

        self._build_device_list()

        if self.debug_enabled:
            self.log("SMA Debug is On")
            self.log(f"SMA Heartbeat time: {Parameters['Mode2']}")

        self._restore_total_production()

        for dev in self.devices:
            self._create_domoticz_device(dev)

        Domoticz.Heartbeat(1)
        self.heartbeat_interval = int(Parameters["Mode2"])

        self.connect()

    def on_heartbeat(self) -> None:
        """Handle periodic updates."""
        if self.heartbeat_counter > 1:
            self.heartbeat_counter -= 1
            return

        self.heartbeat_counter = self.heartbeat_interval

        if not self.client or not self.client.is_open or self.connection_failed:
            self.log("SMA inverter not connected. Reconnecting...")
            self.reconnect()
            return

        try:
            self.update_all_devices()
        except Exception:
            self.connection_failed = True
            self.log_error("SMA Failed to read data")


# ---------------------------------------------------------------------------
# Plugin Instance & Domoticz Callbacks
# ---------------------------------------------------------------------------

_plugin = SMAInverterPlugin()


def onStart() -> None:
    """Domoticz callback: plugin started."""
    _plugin.on_start()


def onHeartbeat() -> None:
    """Domoticz callback: periodic heartbeat."""
    _plugin.on_heartbeat()