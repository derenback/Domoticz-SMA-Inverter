# Domoticz plugin for SMA Inverters using Modbus TCP/IP


## Tested on
- Sunny TriPower [(thanks to Want100Cookies)](https://github.com/Want100Cookies/Domoticz-SMA-Inverter)

## Requirements
- Modbus TCP and UDP enabled ([check this](https://www.sma-sunny.com/en/how-to-test-the-connection-to-your-sma-inverter/))

## Installation
```bash
cd ~/domoticz/plugins
git clone https://github.com/derenback/Domoticz-SMA-Inverter.git
pip3 install -U pymodbus pymodbusTCP
systemctl restart domoticz
```
- Make sure to have the setting "Accept new Hardware Devices" turned on for new devices to be added when adding the Hardware in domoticz.

## Update
```bash
cd ~/domoticz/plugins/Domoticz-SMA-Inverter
git pull
systemctl restart domoticz
```

## Tested on
- Domoticz version: 2020.2 (build 11997)
- Sunny Tripower 10, STP10.0-3AV-40 601

## Version history
    0.1.0 Initial version
    0.2.0 Reduced code duplication
    0.3.0 Added phase voltage and power sensors
    0.3.1 Fixed voltage divisor
    0.3.2 Removed decimals on voltage reading
    0.3.3 Made phase power and voltage optional (Extended sensors)
    0.3.4 Read serial number on start
    0.3.5 Added debug information and option

## Modbus parameters used
    
### Default
    30529, Solar Production
    30773, DC Power A
    30961, DC Power B
    30775, AC Power
    30953, Temperature

### Extended
    30777, Power L1
    30779, Power L2
    30781, Power L3
    30783, Voltage L1
    30785, Voltage L2
    30787, Voltage L3

## Thanks

Original author: Want100Cookies

