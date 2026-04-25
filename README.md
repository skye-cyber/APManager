# AP Manager - Hotspot and Captive Portal Management

A comprehensive WiFi hotspot and captive portal management system with advanced authentication, firewall control, and monitoring capabilities.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Commands](#cli-commands)
  - [Hotspot Management](#hotspot-management)
  - [Authentication Management](#authentication-management)
  - [Firewall Management](#firewall-management)
  - [Monitoring](#monitoring)
  - [Configuration](#configuration)
  - [System Information](#system-information)
- [Configuration](#configuration-1)
- [Requirements](#requirements)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## Features

### Core Features
- **WiFi Hotspot Management**: Create and manage WiFi access points with custom SSIDs and passwords
- **Multiple Sharing Methods**: NAT, Bridge, or No sharing configurations
- **Virtual Interface Support**: Automatic creation of virtual WiFi interfaces
- **Multi-SSID Support**: Run multiple hotspots simultaneously

### Authentication & Firewall
- **Device Authentication**: Authenticate devices by MAC address
- **Captive Portal**: Web-based authentication system
- **Firewall Control**: Block/unblock devices at the network level
- **Webhook Integration**: Real-time notifications for device events
- **API Integration**: Connect to Django backend for centralized management

### Monitoring & Management
- **Real-time Device Monitoring**: Track connected devices and their status
- **Network Interface Management**: View and configure network interfaces
- **System Information**: Comprehensive system and network status
- **Configuration Management**: Easy configuration editing and management

### Advanced Features
- **MAC Address Filtering**: Whitelist/blacklist devices by MAC
- **Client Isolation**: Prevent devices from communicating with each other
- **Custom DNS Configuration**: Configure DNS settings and hosts
- **Bandwidth Management**: Control network bandwidth allocation
- **Multi-Channel Support**: Configure WiFi channels and bands

## Installation

### Prerequisites
- Linux system (tested on Ubuntu/Debian)
- Python 3.8+
- Root privileges (required for network operations)
- WiFi adapter supporting AP mode

### Install from Source

```bash
# Clone the repository
git clone https://github.com/skye-cyber/APManager.git
cd APManager

# Install dependencies
./deps.sh

# Install the application
./install.sh

# Set up systemd service (optional: handled by install)
cp ap_manager.service /etc/systemd/system/
systemctl enable ap_manager
systemctl start ap_manager
```

### Install Dependencies Manually

```bash
# Required packages
apt-get update
apt-get install -y python3-pip python3-venv hostapd dnsmasq iptables

# Python dependencies
pip3 install -r requirements.txt
```

## Quick Start

```bash
# Start a basic hotspot
sudo ap_manager hospot start

# Start a basic with custom arguments
sudo ap_manager hotspot start --ssid "MyHotspot" --password "secure123"

# Authenticate a device
sudo ap_manager auth authenticate --mac "00:11:22:33:44:55"

# Monitor connected devices
sudo ap_manager monitor devices

# Stop the hotspot
sudo ap_manager hotspot stop
```

## CLI Commands

### Hotspot Management

#### Start Hotspot
```bash
ap_manager hotspot start [OPTIONS]
```

Options:
- `--wifi-iface`: WiFi interface (default: wlan0)
- `--internet-iface`: Internet interface (default: wlan0)
- `--ssid`: Hotspot SSID
- `--password`: Hotspot password
- `--channel`: WiFi channel (default: 6)
- `--share-method`: Sharing method (nat, bridge, none)
- `--no-virt`: Disable virtual interface creation
- `--daemon`: Run in background

#### Stop Hotspot
```bash
ap_manager hotspot stop [--force]
```

#### Hotspot Status
```bash
ap_manager hotspot status
```

Shows running hotspot instances and connected clients.

#### List Interfaces
```bash
ap_manager hotspot interfaces
```

Lists all available network interfaces with their status.

### Authentication Management

#### Authenticate Device
```bash
ap_manager auth authenticate --mac MAC_ADDRESS [OPTIONS]
```

Options:
- `--hook`: Webhook URL for callback
- `--api`: Use Django API (default)
- `--local`: Use local firewall only

#### Block Device
```bash
ap_manager auth block --mac MAC_ADDRESS [OPTIONS]
```

#### Check Status
```bash
ap_manager auth status --mac MAC_ADDRESS [OPTIONS]
```

#### Real-time Monitoring
```bash
ap_manager auth monitor [--hook HOOK_URL] [--interval SECONDS]
```

### Firewall Management

#### Start Firewall
```bash
ap_manager firewall start [--config-file CONFIG]
```

#### Stop Firewall
```bash
ap_manager firewall stop [--config-file CONFIG]
```

#### Firewall Status
```bash
ap_manager firewall status [--config-file CONFIG]
```

#### Reset Firewall
```bash
ap_manager firewall reset [--config-file CONFIG]
```

#### Debug Firewall
```bash
ap_manager firewall debug [--config-file CONFIG]
```

### Monitoring

#### Device Monitoring
```bash
ap_manager monitor devices
```

Interactive TUI for monitoring connected devices.

### Configuration

#### Show Configuration
```bash
ap_manager config show
```

#### Set Configuration Value
```bash
ap_manager config set KEY VALUE
```

#### Edit Configuration File
```bash
ap_manager config edit [--editor EDITOR]
```

### System Information

#### Show Version
```bash
ap_manager version
```

#### System Information
```bash
ap_manager info
```

Shows system information including interfaces and capabilities.

## Configuration

The main configuration file is located at `/etc/ap_manager/conf/config.json`.

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `ssid` | Hotspot SSID | "nethub@ap1" |
| `password` | Hotspot password | "nethub@ap1" |
| `wifi_iface` | WiFi interface | "wlan0" |
| `internet_iface` | Internet interface | "eth0" |
| `channel` | WiFi channel | 6 |
| `share_method` | Sharing method | "nat" |
| `gateway` | Gateway IP | "192.168.100.1" |
| `ip_range` | IP range | "192.168.100.0/24" |
| `country` | Country code | "KE" |
| `freq_band` | Frequency band | 2.4 |
| `isolate_clients` | Client isolation | false |
| `mac_filter` | MAC filtering | false |
| `daemon` | Run as daemon | true |

### Configuration Files

- **Main Config**: `/etc/ap_manager/conf/config.json`
- **Hostapd Config**: `/etc/ap_manager/conf/hostapd.json`
- **Network Config**: `/etc/ap_manager/conf/netconf.json`
- **Captive Portal**: `/etc/ap_manager/conf/captive.json`

## Requirements

### Hardware Requirements
- WiFi adapter supporting AP mode (master mode)
- Minimum 1GB RAM
- Disk space: any size as long as os can work

### Software Requirements
- Python 3.8+
- hostapd
- dnsmasq
- iptables
- iproute2
- wireless-tools

### Python Dependencies
```
click
rich
requests
asyncio
```

## Architecture

```
AP Manager Architecture
├── CLI Interface (Click + Rich)
├── Core Services
│   ├── AP Manager
│   ├── Network Configuration
│   ├── Process Management
│   └── Hostapd Management
├── Captive Portal
│   ├── Firewall Control
│   ├── Authentication
│   └── Web Interface
├── Monitoring
│   ├── Device Monitoring
│   ├── Network Monitoring
│   └── TUI Interface
└── Configuration Management
```

## Usage Examples

### Basic Hotspot Setup
```bash
# Start hotspot with custom SSID and password
sudo ap_manager hotspot start --ssid "MyCafeWiFi" --password "welcome123"

# Check status
sudo ap_manager hotspot status

# Stop hotspot
sudo ap_manager hotspot stop
```

### Advanced Configuration
```bash
# Start hotspot with specific interface and channel
sudo ap_manager hotspot start \
  --wifi-iface wlan1 \
  --internet-iface eth0 \
  --ssid "ConferenceWiFi" \
  --password "conference2023" \
  --channel 11 \
  --share-method nat

# Configure client isolation
sudo ap_manager config set isolate_clients true

# Restart hotspot to apply changes
sudo ap_manager hotspot stop
sudo ap_manager hotspot start
```

### Device Management
```bash
# Authenticate a device
sudo ap_manager auth authenticate --mac "AA:BB:CC:DD:EE:FF"

# Check device status
sudo ap_manager auth status --mac "AA:BB:CC:DD:EE:FF"

# Block a device
sudo ap_manager auth block --mac "AA:BB:CC:DD:EE:FF"
```

### Monitoring and Troubleshooting
```bash
# Monitor devices in real-time
sudo ap_manager monitor devices

# Check firewall status
sudo ap_manager firewall status

# Debug firewall issues
sudo ap_manager firewall debug

# Show system information
sudo ap_manager info
```

## Troubleshooting

### Common Issues

**WiFi interface not found**:
- Check if your WiFi adapter is detected: `iwconfig`
- Ensure the interface name is correct

**AP mode not supported**:
- Check if your WiFi adapter supports AP mode: `iw list | grep "AP"`
- Some adapters require specific drivers

**Permission denied**:
- AP Manager requires root privileges
- Use `sudo` or run as root user

**Hostapd errors**:
- Check hostapd logs: `/var/log/syslog`
- Ensure no other processes are using the WiFi interface

**DNS issues**:
- Check dnsmasq configuration: `/etc/dnsmasq.conf`
- Ensure port 53 is not used by another service

### Debugging Commands

```bash
# Check WiFi interfaces
sudo ap_manager hotspot interfaces

# Check system information
sudo ap_manager info

# Debug firewall
sudo ap_manager firewall debug

# View logs
journalctl -u ap_manager -f
```

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the project repository.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Create a pull request

## Changelog

### Version 1.0.3
- Added real-time device monitoring
- Improved authentication system
- Enhanced firewall management
- Better error handling and logging
- Rich console output for better UX

### Version 1.0.2
- Initial stable release
- Basic hotspot functionality
- Device authentication
- Configuration management

## Contact

For more information, please contact the project maintainers.

## LICENSE
    Copyright (C) <2026>  <wambua>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
