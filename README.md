# Domoticz plugin for SMA Inverters using Modbus TCP/IP


## Tested on
- Sunny TriPower [(thanks to Want100Cookies)](https://github.com/Want100Cookies/Domoticz-SMA-Inverter)
- Sunny Boy 3.6

## Requirements
- Modbus TCP enabled ([check this](https://www.sma-sunny.com/en/how-to-test-the-connection-to-your-sma-inverter/))

## Installation
```bash
cd ~/domoticz/plugins
git clone https://github.com/derenback/Domoticz-SMA-Inverter.git
pip3 install -U pymodbus pymodbusTCP
systemctl restart domoticz
```

Succesfully Tested on Domoticz version: 2020.2 (build 11997)

## Thanks

Original author: Want100Cookies

