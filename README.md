# Domoticz SMA Inverter Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A [Domoticz](https://www.domoticz.com/) plugin for monitoring SMA solar inverters via Modbus TCP/IP.

## Features

- Real-time solar production monitoring
- AC/DC power readings
- Temperature monitoring
- Optional extended sensors (per-phase voltage, power, grid frequency)
- Optional battery sensors (state of charge, temperature, grid feed-in)
- Automatic reconnection on connection failure

---

## Requirements

- **Domoticz** 2020.2 or later
- **Python** 3.8+
- **pyModbusTCP** package
- SMA inverter with **Modbus TCP enabled** ([how to check](https://www.sma-sunny.com/en/how-to-test-the-connection-to-your-sma-inverter/))

---

## Installation

> **Note:** On recent Raspberry Pi OS versions (2023.10+), you may encounter an `externally-managed-environment` error. See [this guide](https://www.jeffgeerling.com/blog/2023/how-solve-error-externally-managed-environment-when-installing-pip3) for solutions.

```bash
cd ~/domoticz/plugins
git clone https://github.com/derenback/Domoticz-SMA-Inverter.git
sudo pip3 install -U pymodbusTCP
sudo systemctl restart domoticz
```

> **Important:** Enable **"Accept new Hardware Devices"** in Domoticz settings before adding the hardware.

---

## Updating

```bash
cd ~/domoticz/plugins/Domoticz-SMA-Inverter
git pull
sudo systemctl restart domoticz
```

---

## Configuration

After installation, add the hardware in Domoticz:

1. Go to **Setup → Hardware**
2. Select **SMA Solar Inverter (modbus TCP/IP)**
3. Configure:
   - **IP Address**: Your inverter's IP
   - **Port**: `502` (default Modbus port)
   - **Device ID**: Usually `3`
   - **Reading Interval**: Polling frequency in seconds
   - **Extended sensors**: Enable for per-phase readings
   - **Battery sensors**: Enable for battery monitoring

---

## Docker

See the [Docker setup repository](https://github.com/derenback/Domoticz-SMA-Inverter-Docker) for containerized deployment.

---

## Testing

A standalone test script is available in the `test/` folder to verify connectivity:

```bash
cd test
python3 sma_test.py
```

---

## Compatibility

### Tested Environments

| Component    | Versions                                        |
|--------------|-------------------------------------------------|
| Domoticz     | 2020.2, 2021.1, 2022.1, 2022.2, 2023.2, 2024.7, 2025.2 |
| Inverter     | Sunny Tripower 10 (STP10.0-3AV-40 601)          |
| Firmware     | 3.10.15.R, 3.11.11.R, 4.0.61.R                  |
| pyModbusTCP  | 0.1.8, 0.2.0, 0.2.1                             |

---

## Supported Sensors

### Core Sensors (always enabled)

| Address | Name             | Unit | Sensor Type | Note                             |
|---------|------------------|------|-------------|----------------------------------|
| 30529   | Solar Production | kWh  | Counter     |                                  |
| 30773   | DC Power A       | W    | Usage       |                                  |
| 30961   | DC Power B       | W    | Usage       |                                  |
| 30775   | AC Power         | W    | kWh         | + 30529 for daily and total prod |
| 30953   | Temperature      | °C   | Temperature |                                  |

### Extended Sensors (optional)

| Address | Name              | Unit | Sensor Type |
|---------|-------------------|------|-------------|
| 30777   | Power L1          | W    | Usage       |
| 30779   | Power L2          | W    | Usage       |
| 30781   | Power L3          | W    | Usage       |
| 30783   | Voltage L1        | V    | Voltage     |
| 30785   | Voltage L2        | V    | Voltage     |
| 30787   | Voltage L3        | V    | Voltage     |
| 30803   | Grid Frequency    | Hz   | Custom      |
| 30807   | Reactive Power L1 | VAr  | Custom      |
| 30809   | Reactive Power L2 | VAr  | Custom      |
| 30811   | Reactive Power L3 | VAr  | Custom      |
| 30813   | Apparent Power L1 | VA   | Custom      |
| 30815   | Apparent Power L2 | VA   | Custom      |
| 30817   | Apparent Power L3 | VA   | Custom      |
| 30769   | Current String A  | A    | Ampere      |
| 30957   | Current String B  | A    | Ampere      |
| 30771   | Voltage String A  | V    | Voltage     |
| 30959   | Voltage String B  | V    | Voltage     |

### Battery Sensors (optional)

| Address | Name                      | Unit | Sensor Type |
|---------|---------------------------|------|-------------|
| 30849   | Battery Temperature       | °C   | Temperature |
| 30845   | Battery State of Charge   | %    | Percentage  |
| 30867   | Battery Grid Feed-In      | kWh  | kWh         |
| 30865   | Battery Grid Supplied     | kWh  | kWh         |

---

## Changelog

<details>
<summary>Click to expand version history</summary>

| Version | Changes |
|---------|---------|
| 1.3.0   | Remove pymodbus dependency; use only pyModbusTCP + standard library |
| 1.2.0   | Refactor plugin code |
| 1.1.0   | Added battery temperature and charge sensors (thanks @daserra23) |
| 1.0.0   | Moved Docker files to [separate repo](https://github.com/derenback/Domoticz-SMA-Inverter-Docker) |
| 0.9.9   | Fix for pymodbus constants breaking change (test script) |
| 0.9.8   | Fix for [pymodbus constants](https://github.com/pymodbus-dev/pymodbus/pull/1743) breaking change |
| 0.9.7   | Bugfix: support intervals longer than 60 seconds (#21) |
| 0.9.6   | Bugfix: issue after dataclass refactor (#19) |
| 0.9.5   | Code cleanup |
| 0.9.4   | Improved connection recovery on socket failure |
| 0.9.3   | Fix client open check; ensure port/unit are integers |
| 0.9.2   | Handle negative numbers correctly |
| 0.9.1   | Added string current and voltage sensors |
| 0.9.0   | Refactor and cleanup |
| 0.8.0   | Added reactive and apparent power sensors |
| 0.7.x   | Various fixes for production tracking and values |
| 0.6.0   | Restore total production on restart |
| 0.5.x   | AC power daily production improvements |
| 0.4.0   | AC Power sensor type changed to kWh |
| 0.3.x   | Added phase voltage/power, debug option |
| 0.2.0   | Reduced code duplication |
| 0.1.0   | Initial version |

</details>

---

## Acknowledgments

Original author: [Want100Cookies](https://github.com/Want100Cookies/Domoticz-SMA-Inverter)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

