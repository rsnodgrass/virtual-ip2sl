# Virtual IP2SL (IP to Serial)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=WREP29UDAMB6G)

Provides bidirectional TCP-to-serial access to physical serial ports connected to the
host running this microservice by emulating an iTach IP to Serial (IP2SL). Each instance
of the Virtual IP2SL microservice can expose up to eight physical RS232 serial ports.

I decided to build this after having physical USB to serial adapters hooked up to a
Raspberry Pi (and the native Raspberry Pi GPIO pin outs), but had several iOS and other client applications 
which supported RS232 over IP by implementing a subset of the published iTach TCP protocol.
While Open Source projects existed to emulate iTach IR devices, none implemented raw access
to serial ports via TCP. For my home, I paired this with [Flex IP](https://amazon.com/Global-Cache-iTach-Flex-IP/dp/B00C6FRPIC/?tag=carreramfi-20) hardware devices for cases where the serial port connection wasn't in the rack with my Raspberry Pi.

#### Security

**The IP2SL protocol definition does not provide any authentication or security model. Caveat emptor!**

* IP2SL has no authentication model for command/control or for communication
* all traffic is sent unencrypted over network

A minimial security improvement is restricting which IP addresses can connect to the Virtual IP2SL server.
Here is a config example:

```
allowed_ip:
  - 10.10.1.7
  - 10.10.1.132
```

## Configuration

By default, the Virtual IP2SL is configured to open a single port attached 
at 9600 baud to one USB serial port adapter on /dev/ttyUSB0. However, a
wide variety of serial port configurations are possible, up to eight
serial ports per Virutal IP2SL instance. The environment variable IP2SL_CONFIG
can be used to point to YAML config files other than [config/default.yaml](config/default.yaml).

Below is an example of four USB serial ports connected.
See the "[iTach TCP API Specification](https://www.globalcache.com/files/releases/flex-16/API-Flex_TCP_1.6.pdf)"
PDF manual for the available configuration values for each serial port.

```yaml
serial:
  1: # port 1
    path: /dev/ttyUSB0
    baud: 9600
    flow: FLOW_NONE
    timeout: 4 # optional, default = 5 seconds

  2: 
    path: /dev/ttyUSB1
    baud: 9600
    flow: FLOW_HARDWARE

  3: 
    path: /dev/ttyUSB2
    baud: 14400

  4: 
    path: /dev/ttyUSB3
    baud: 115200
```

## Running

#### Standalone

```bash
python3 ip2sl
```

#### As Docker Container

Under Docker (may require modifying Dockerfile to specify the BUILD_FROM architecture base you need):

```bash
docker build -t virtual-ip2sl .
docker run virtual-ip2sl
```

NOTE: Since multicast is not supported from within a Docker container, the AMX discovery beacon will
not be published so you must manually configure clients to communicate with your Virtual IP2SL
instance.

#### As Home Assistant Hass.io Add-On

To run as a Home Assistant Hass.io add-on, install the repository:

 https://github.com/rsnodgrass/hassio-addons

## Network Ports

This microservice implements the open AMX Discovery Beacon protocol, raw TCP sockets to 
RS232 serial ports, and a TCP Port exposing the iTach command protocol.

The Virtual IP2SL listens on a variety of TCP ports, both for controlling the service
as well as the configuration for each serial port interface. Data sent to any of these
ports is relayed directly out the RS232 serial port associated with that TCP port in
configuration. Similarly, any data received from the RS232 will be written to the
TCP port.

| TCP Port | Description                              |
| -------- | ---------------------------------------- |
| 4998     | iTach TCP API command/control port       |
| 4999     | TCP port to the first serial port        |
| 5000     | ... second serial port *(optional)*      |
| 5001     | ... third serial port *(optional)*       |
| 5002     | ... fourth serial port *(optional)*      |
| 5003     | ... fifth serial port *(optional)*       |
| 5004     | ... sixth serial port *(optional)*       |
| 5005     | ... seventh serial port *(optional)*     |
| 5006     | ... eighth serial port *(optional)*      |

* For security, it is recommended disabling any ports that are not in use.
If no configuration exists for a given serial port (1-8), the associated TCP port
will not be opened.

## Example TTY Paths

The following are a variety of example TTY paths for different serial port interfaces:

| Serial Path                 | Description                                         |
| --------------------------- | --------------------------------------------------- |
| /dev/ttyS0                  | Raspberry Pi mini UART GPIO                         |
| /dev/ttyAMA0                | Raspberry Pi GPIO pins 14/15 (pre-Bluetooth RPi 3)  |
| /dev/serial0                | RPi 3/4 serial port alias 1                         |
| /dev/serial1                | RPi 3/4 serial port alias 2                         |
| /dev/tty.usbserial          | MacOS USB serial adapter                            |
| /dev/ttyUSB0                | Raspberry Pi USB serial adapter 1                   |
| /dev/ttyUSB1                | Raspberry Pi USB serial adapter 2                   |
| /dev/tty.usbserial-A501SGSU | StarTach ICUSB232I (8-port) serial port 1 (MacOS)   |
| /dev/tty.usbserial-A501SGSV | StarTach ICUSB232I (8-port) serial port 2 (MacOS)   |

## See Also

* [Virtual IP2SL for Home Assistant](https://github.com/rsnodgrass/hassio-addons/tree/master/virtual-ip2sl-addon)

#### Clients

* [iTest for Windows](https://www.globalcache.com/downloads/) and [iTest for MacOS (by Martijn Rijnbeek)](http://www.rmartijnr.eu/itest.html) - tools for connecting and sending test queries
* [Home Assistant IP2SL client by tinglis1](https://github.com/tinglis1/home-assistant-custom/tree/master/custom_components/notify) (last updated 2016)
* [Home Assistant gc100 sensor/switch (no serial)](https://www.home-assistant.io/components/gc100)

#### API

Special thanks to [Global Caché](https://www.globalcache.com/products/) for opening and publishing TCP control APIs:

* [iTach Flex TCP API Specification v1.6](https://www.globalcache.com/files/releases/flex-16/API-Flex_TCP_1.6.pdf)
  (earlier [v1.5 specificaiton](https://www.globalcache.com/files/docs/API-iTach.pdf))
* [iTach TCP/IP to Serial (RS232) specs](https://www.globalcache.com/products/itach/ip2slspecs/) and [Flex specs](https://www.globalcache.com/products/flex/flc-slspec/)

#### Related Emulators

* [GlobalCovfefe](https://platformio.org/lib/show/5679/GlobalCovfefe): Global Cache device emulator with one IR sender and one optional IR learner
* [ESP8266iTachEmulator](https://github.com/probonopd/ESP8266iTachEmulator): iTach/LIRC IP2IR emulator for IR signals
* [Global Cache Wireless Emulator (ESP8266)](https://hackaday.io/project/8233-global-cache-wireless-emulator-esp8266)
* [socat](https://linux.die.net/man/1/socat) / [ser2net](https://linux.die.net/man/8/ser2net)

Note that [socat](https://linux.die.net/man/1/socat) clients can communicate with any IP2SL exposed serial device.

## Community Support

Links to several forums for community engagement around iTach Flex:

* https://community.home-assistant.io/t/itach-ip2sl/28805
* https://community.smartthings.com/t/home-theater-macro-global-cache-itach/126450

## TODO

NOTE: While this works for my use cases (and most common ones users will encounter),
it would be great to have other contributors help take this to the next level and
implement features, stability improvements, etc.

Planned:

* improve error handling (e.g. invalid port modules specified in get_SERIAL)

Ideas for eventual implementation (**feel free to contribute; no plans by me to add**):

* add support for RS485 connections
* persist set_SERIAL changes across restarts (optional)
* enhance security of the IP2SL interface (e.g. authentication token headers)
* web UI console showing details about the config and each port (including metrics)
* emulation compatibility for [GC-100-xx](https://www.globalcache.com/files/docs/API-GC-100.pdf)
* add an optional MQTT interface
* when Docker supports UDP multicast publishing from within a container, enable beacon for Docker image

