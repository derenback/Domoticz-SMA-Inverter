# Domoticz plugin for SMA Inverters using Modbus TCP/IP


## Requirements
- Modbus TCP and UDP enabled ([check this](https://www.sma-sunny.com/en/how-to-test-the-connection-to-your-sma-inverter/))

## Installation
```bash
cd ~/domoticz/plugins
git clone https://github.com/derenback/Domoticz-SMA-Inverter.git
pip3 install -U pymodbus pymodbusTCP
sudo systemctl restart domoticz
```
- Make sure to have the setting "Accept new Hardware Devices" turned on for new devices to be added when adding the Hardware in domoticz.

## Update
```bash
cd ~/domoticz/plugins/Domoticz-SMA-Inverter
git pull
sudo systemctl restart domoticz
```

## Tested on
- Domoticz version: 2020.2 (build 11997)
- Sunny Tripower 10, STP10.0-3AV-40 601

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

## Version history
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

