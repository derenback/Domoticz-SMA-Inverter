# Domoticz plugin for SMA Inverters using Modbus TCP/IP


## Requirements
- Modbus TCP and UDP enabled ([check this](https://www.sma-sunny.com/en/how-to-test-the-connection-to-your-sma-inverter/))

## Installation
Note! On later versions of Pi OS (2023.10) you will probably get an error that say "error: externally-managed-environment". Checkout Jeff Geerlings post [here](https://www.jeffgeerling.com/blog/2023/how-solve-error-externally-managed-environment-when-installing-pip3) on one way to solve this.

```bash
cd ~/domoticz/plugins
git clone https://github.com/derenback/Domoticz-SMA-Inverter.git
sudo pip3 install -U pymodbus pymodbusTCP
sudo systemctl restart domoticz
```
- Make sure to have the setting "Accept new Hardware Devices" turned on for new devices to be added when adding the Hardware in domoticz.

## Update
```bash
cd ~/domoticz/plugins/Domoticz-SMA-Inverter
git pull
sudo systemctl restart domoticz
```

## Docker
See docker example files [here](https://github.com/derenback/Domoticz-SMA-Inverter-Docker)

## Test file
In the folder test you will find a simple stand alone test script.

## Tested on
- Domoticz versions: 2020.2, 2021.1, 2022.1, 2022.2, 2023.2, 2024.7
- Sunny Tripower 10, STP10.0-3AV-40 601 
      FW 3.10.15.R, 3.11.11.R, 4.0.61.R
- pymodbus: 2.4.0, 2.5.0, 3.5.0, 3.5.4, 3.6.3
- pyModbusTCP: 0.1.8, 0.2.0, 0.2.1

## Modbus parameters used and sensor types
    
| Address | Name              | Unit | Ext | Sensor Type | Note                             |
|---------|-------------------|------|-----|-------------|----------------------------------|
|  30529  | Solar production  | kWh  |     | Counter     |                                  | 
|  30773  | DC Power A        |  W   |     | Usage       |                                  |
|  30961  | DC Power B        |  W   |     | Usage       |                                  |
|  30775  | AC Power          |  W   |     | kWh         | + 30529 for daily and total prod |
|  30953  | Temperature       |  C   |     | Temperatur  |                                  |
|  30777  | Power L1          |  W   |  X  | Usage       |                                  |
|  30779  | Power L2          |  W   |  X  | Usage       |                                  |
|  30781  | Power L3          |  W   |  X  | Usage       |                                  |
|  30783  | Voltage L1        |  V   |  X  | Voltage     |                                  |
|  30785  | Voltage L2        |  V   |  X  | Voltage     |                                  |
|  30787  | Voltage L3        |  V   |  X  | Voltage     |                                  |
|  30803  | Grid frequency    |  Hz  |  X  | Custom      |                                  |
|  30807  | Reactive power L1 |  VAr |  X  | Custom      |                                  |
|  30809  | Reactive power L2 |  VAr |  X  | Custom      |                                  |
|  30811  | Reactive power L3 |  VAr |  X  | Custom      |                                  |
|  30813  | Apparent power L1 |  VA  |  X  | Custom      |                                  |
|  30815  | Apparent power L2 |  VA  |  X  | Custom      |                                  |
|  30817  | Apparent power L3 |  VA  |  X  | Custom      |                                  |
|  30769  | Current String A  |  A   |  X  | Ampere      |                                  |
|  30957  | Current String B  |  A   |  X  | Ampere      |                                  |
|  30771  | Voltage String A  |  V   |  X  | Voltage     |                                  |
|  30959  | Voltage String B  |  V   |  X  | Voltage     |                                  |

## Version history
    1.0.0 Move docker files to a separate [repo](https://github.com/derenback/Domoticz-SMA-Inverter-Docker)
    0.9.9 Fix for breaking change in [pymodbus constants](https://github.com/pymodbus-dev/pymodbus/pull/1743).
          Now also in test script.
    0.9.8 Fix for breaking change in [pymodbus constants](https://github.com/pymodbus-dev/pymodbus/pull/1743).
    0.9.7 Bugfix #21 Added support for inteval longer than 60 seconds
    0.9.6 Bugfix #19 Issue after refactor to use dataclass
    0.9.5 Code cleanup
    0.9.4 Improve ability to recover connection on socket failure
    0.9.3 Fix check if client is open and make sure port and unit number are integers
    0.9.2 Fix Handle negative numbers
    0.9.1 Added String Current and Voltage sensors
    0.9.0 Refactor and cleanup
    0.8.0 Added Reactive and apparent power sensors
    0.7.4 Fix for decimal value stored for total production
    0.7.3 Code cleanup, Fix issue with U32 vs S32 and undefined value
    0.7.2 Fix so that total production is not set to zero on undefind value
    0.7.1 Skip update if a device has been removed
    0.7.0 Added grid frquency
    0.6.0 Reverted removal of total production and restore total production on restart or no data.
    0.5.1 Fix for undefined value of total production
    0.5.0 AC power daily production based on total production + Removed device for Solar production. 
          (Now included in AC power)
    0.4.0 Changed AC Power to be sensor type kWh to also show daily production
    0.3.5 Added debug information and option
    0.3.4 Read serial number on start
    0.3.3 Made phase power and voltage optional (Extended sensors)
    0.3.2 Removed decimals on voltage reading
    0.3.1 Fixed voltage divisor
    0.3.0 Added phase voltage and power sensors
    0.2.0 Reduced code duplication
    0.1.0 Initial version

## Thanks

Original author: [(Want100Cookies)](https://github.com/Want100Cookies/Domoticz-SMA-Inverter)

