# AP Manager Captive Portal System

A comprehensive captive portal implementation integrated with the AP Manager system, providing advanced network access control, device authentication, and firewall management.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [CLI Commands](#cli-commands)
- [Core Components](#core-components)
- [Authentication System](#authentication-system)
- [Firewall Integration](#firewall-integration)
- [Monitoring and Management](#monitoring-and-management)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Overview

The AP Manager Captive Portal is a sophisticated network access control system that integrates seamlessly with the AP Manager hotspot management system. It provides MAC-based authentication, firewall control, and real-time monitoring capabilities.

## Features

### Core Features
- **MAC-based Authentication**: Secure device authentication using MAC addresses
- **Firewall Integration**: iptables-based access control
- **Automatic Redirection**: Seamless captive portal detection and redirection
- **Real-time Monitoring**: Live tracking of connected devices and their status

### Advanced Features
- **Multi-Interface Support**: Works with virtual and physical network interfaces
- **Configuration Management**: Easy configuration through CLI and JSON files
- **Webhook Integration**: Real-time notifications for device events
- **API Integration**: Connect to Django backend for centralized management
- **Client Isolation**: Prevent devices from communicating with each other
- **Bandwidth Management**: Control network bandwidth allocation

### Management Features
- **Device Management**: Authenticate, block, and monitor devices
- **Configuration Management**: Easy editing and management of settings
- **System Monitoring**: Comprehensive system and network status
- **Debugging Tools**: Advanced troubleshooting and diagnostic tools

## Architecture

```
AP Manager Captive Portal Architecture
├── CLI Interface (Click + Rich)
├── Core Services
│   ├── Captive Portal Entry
│   ├── Configuration Management
│   ├── Firewall Control
│   └── Device Authentication
├── Monitoring
│   ├── Device Monitoring
│   ├── Network Monitoring
│   └── TUI Interface
└── Integration
    ├── AP Manager Integration
    ├── Django API Integration
    └── Webhook Integration
```

### Data Flow

```
Client Device → Hotspot Interface → Captive Portal → Firewall → Internet
                    │                           │
                    ├── MAC Authentication      ├── Access Control
                    ├── Device Tracking          ├── Traffic Redirection
                    └── Connection Monitoring    └── Bandwidth Management
```

## Installation

### Prerequisites
- Linux system (tested on Ubuntu/Debian)
- Python 3.8+
- Root privileges (required for network operations)
- iptables for firewall management
- dnsmasq for DNS services

### Install Dependencies

```bash
# Install system dependencies
apt-get update
apt-get install -y iptables dnsmasq python3-pip

# Install Python dependencies
pip3 install click rich requests
```

### Configuration Setup

```bash
# Create required directories
mkdir -p /etc/ap_manager/auth
mkdir -p /etc/ap_manager/logs

# Set up configuration files
cp /home/skye/APManager/config/captive.json /etc/ap_manager/conf/
```

## Configuration

### Main Configuration File

The main configuration file is located at `/etc/ap_manager/conf/captive.json`.

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `BASE_DIR` | Base directory | `/etc/ap_manager` |
| `GATEWAY` | Gateway IP address | `192.168.100.1` |
| `SUBNET` | Network subnet | `192.168.100.0/24` |
| `CAPTIVE_PORT` | Captive portal port | `8001` |
| `CLIENT_INTERFACE` | Client interface | `xap0` |
| `INTERNET_INTERFACE` | Internet interface | `eth0` |
| `AUTH_DIR` | Authentication directory | `/etc/ap_manager/auth` |
| `MAC_FILE` | Authenticated MACs file | `/etc/ap_manager/auth/authenticated_macs` |

### Configuration Files

- **Main Config**: `/etc/ap_manager/conf/captive.json`
- **Authenticated MACs**: `/etc/ap_manager/auth/authenticated_macs`
- **DNSMasq Config**: `/etc/dnsmasq.d/ap_manager_portal.conf`
- **Logs**: `/etc/ap_manager/logs/`

## CLI Commands

The captive portal is managed through the AP Manager CLI interface.

### Firewall Management

#### Start Firewall
```bash
ap_manager firewall start [--config-file CONFIG]
```

Starts the captive portal firewall and authentication system.

#### Stop Firewall
```bash
ap_manager firewall stop [--config-file CONFIG]
```

Stops the captive portal firewall and cleans up rules.

#### Firewall Status
```bash
ap_manager firewall status [--config-file CONFIG]
```

Shows current firewall status and configuration.

#### Reset Firewall
```bash
ap_manager firewall reset [--config-file CONFIG]
```

Completely resets the firewall to default state.

#### Debug Firewall
```bash
ap_manager firewall debug [--config-file CONFIG]
```

Provides detailed debugging information for troubleshooting.

### Configuration Management

#### Show Configuration
```bash
ap_manager fconfig show
```

Displays current firewall configuration.

#### Set Configuration Value
```bash
ap_manager fconfig set KEY VALUE
```

Sets a specific configuration value.

#### Edit Configuration File
```bash
ap_manager fconfig edit [--editor EDITOR]
```

Edits the configuration file with your preferred editor.

## Core Components

### Captive Portal Entry

The main entry point for the captive portal system, located in `captive_portal/core/captive_entry.py`.

**Key Methods:**
- `start()`: Start the captive portal service
- `stop()`: Stop the captive portal service
- `status()`: Get current status information
- `monitor()`: Monitor captive portal activity
- `debug()`: Debug captive portal issues
- `reset()`: Reset to default state

### Configuration Management

Handles all configuration aspects of the captive portal system.

**Key Features:**
- JSON-based configuration
- Runtime configuration updates
- Multiple configuration profiles
- Easy editing and management

### Firewall Control

Advanced firewall management system using iptables.

**Key Features:**
- MAC-based access control
- Chain management (CAPTIVE_PORTAL, AUTH_REDIRECT)
- Rule verification and validation
- Real-time rule updates
- Comprehensive debugging tools

### Device Authentication

MAC-based device authentication system.

**Key Features:**
- MAC address validation
- Authenticated device tracking
- Real-time authentication updates
- Persistent authentication storage
- Easy device management

## Authentication System

### How Authentication Works

1. **Device Connection**: Device connects to the WiFi network
2. **Redirection**: Device is redirected to captive portal
3. **Authentication**: Device MAC address is authenticated
4. **Access Granted**: Firewall rules are updated to allow internet access
5. **Persistent Access**: Device remains authenticated until explicitly blocked

### Authentication Methods

#### Local Authentication
```bash
ap_manager auth authenticate --mac MAC_ADDRESS --local
```

#### API Authentication
```bash
ap_manager auth authenticate --mac MAC_ADDRESS --api
```

#### Webhook Integration
```bash
ap_manager auth authenticate --mac MAC_ADDRESS --hook WEBHOOK_URL
```

### Device Management

#### Authenticate Device
```bash
ap_manager auth authenticate --mac MAC_ADDRESS
```

#### Block Device
```bash
ap_manager auth block --mac MAC_ADDRESS
```

#### Check Device Status
```bash
ap_manager auth status --mac MAC_ADDRESS
```

#### Monitor Devices
```bash
ap_manager auth monitor
```

## Firewall Integration

### Firewall Architecture

The captive portal uses a sophisticated firewall architecture with custom iptables chains:

**Chains:**
- **CAPTIVE_PORTAL**: Filters forwarded traffic based on MAC authentication
- **AUTH_REDIRECT**: NAT chain for HTTP/HTTPS redirection bypass

### Rule Flow

1. **New Device**: HTTP/HTTPS → AUTH_REDIRECT → Portal (8001)
2. **Authenticated Device**: MAC matches → RETURN → Internet access
3. **Unauthenticated Device**: No MAC match → REDIRECT → Portal

### Firewall Commands

#### Verify Chains
```bash
ap_manager firewall debug
```

#### Clear Rules
```bash
ap_manager firewall reset
```

#### Update Rules
```bash
# Rules are automatically updated when devices are authenticated/blocked
```

## Monitoring and Management

### Real-time Monitoring

```bash
ap_manager monitor devices
```

Interactive TUI for monitoring connected devices and their status.

### System Status

```bash
ap_manager firewall status
```

Shows comprehensive system status including:
- Running services
- Authenticated devices
- Firewall rules
- Configuration details

### Debugging Tools

```bash
ap_manager firewall debug
```

Provides detailed debugging information including:
- Current configuration
- Firewall status
- Authenticated devices
- Verbose firewall rules

## Usage Examples

### Basic Setup

```bash
# Start the captive portal
sudo ap_manager firewall start

# Authenticate a device
sudo ap_manager auth authenticate --mac "00:11:22:33:44:55"

# Check status
sudo ap_manager firewall status

# Stop the captive portal
sudo ap_manager firewall stop
```

### Advanced Configuration

```bash
# Start with custom configuration
sudo ap_manager firewall start --config-file /path/to/custom_config.json

# Configure client isolation
sudo ap_manager fconfig set isolate_clients true

# Set custom gateway
sudo ap_manager fconfig set GATEWAY "192.168.1.1"

# Restart to apply changes
sudo ap_manager firewall stop
sudo ap_manager firewall start
```

### Device Management

```bash
# Authenticate multiple devices
sudo ap_manager auth authenticate --mac "AA:BB:CC:DD:EE:FF"
sudo ap_manager auth authenticate --mac "11:22:33:44:55:66"

# Check device status
sudo ap_manager auth status --mac "AA:BB:CC:DD:EE:FF"

# Block a device
sudo ap_manager auth block --mac "AA:BB:CC:DD:EE:FF"

# Monitor devices in real-time
sudo ap_manager auth monitor
```

### Monitoring and Troubleshooting

```bash
# Check firewall status
sudo ap_manager firewall status

# Debug firewall issues
sudo ap_manager firewall debug

# Show system information
sudo ap_manager info

# Monitor devices
sudo ap_manager monitor devices
```

## Troubleshooting

### Common Issues

**Captive portal not redirecting:**
- Check firewall rules: `sudo ap_manager firewall debug`
- Verify interface configuration: `sudo ap_manager info`
- Check DNSMasq status: `systemctl status dnsmasq`

**Authenticated devices have no internet:**
- Verify MAC authentication: `sudo ap_manager auth status --mac MAC_ADDRESS`
- Check firewall rules: `sudo ap_manager firewall debug`
- Test connectivity: `ping 8.8.8.8`

**Service not starting:**
- Check logs: `journalctl -u ap_manager`
- Verify dependencies: `sudo ap_manager info`
- Check configuration: `sudo ap_manager fconfig show`

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

# Check firewall rules manually
iptables -L CAPTIVE_PORTAL -n --line-numbers
iptables -t nat -L AUTH_REDIRECT -n --line-numbers
```

## Advanced Configuration

### Custom Configuration

Edit the configuration file directly:

```bash
sudo ap_manager fconfig edit
```

Or set specific values:

```bash
sudo ap_manager fconfig set CLIENT_INTERFACE "wlan0"
sudo ap_manager fconfig set INTERNET_INTERFACE "eth1"
sudo ap_manager fconfig set GATEWAY "192.168.1.1"
```

### Multiple Interfaces

Configure multiple client interfaces:

```bash
sudo ap_manager fconfig set CLIENT_INTERFACE "xap0,xap1"
```

### Custom Ports

Change the captive portal port:

```bash
sudo ap_manager fconfig set CAPTIVE_PORT "8080"
```

### Client Isolation

Enable client isolation to prevent devices from communicating:

```bash
sudo ap_manager fconfig set isolate_clients true
```

### MAC Filtering

Enable MAC filtering for additional security:

```bash
sudo ap_manager fconfig set mac_filter true
```

## Integration

### Django API Integration

The captive portal can integrate with a Django backend for centralized management:

```bash
# Use API for authentication
sudo ap_manager auth authenticate --mac MAC_ADDRESS --api
```

### Webhook Integration

Configure webhooks for real-time notifications:

```bash
# Authenticate with webhook callback
sudo ap_manager auth authenticate --mac MAC_ADDRESS --hook "https://your-webhook-url.com"
```

### AP Manager Integration

The captive portal integrates seamlessly with the AP Manager hotspot system:

```bash
# Start hotspot and captive portal
sudo ap_manager hotspot start
sudo ap_manager firewall start

# Manage both systems together
sudo ap_manager hotspot status
sudo ap_manager firewall status
```

## Security Features

- **MAC Address Validation**: Secure device authentication
- **Connection State Tracking**: Monitor active connections
- **Secure Redirect Handling**: Prevent redirection attacks
- **Isolated Network Segmentation**: Separate client networks
- **Regular Security Updates**: Keep system secure

## Performance

- **Handles 100+ concurrent connections**
- **Low latency authentication**
- **Efficient connection tracking**
- **Minimal resource footprint**
- **Optimized firewall rules**

## Best Practices

1. **Regular Updates**: Keep the system and dependencies updated
2. **Monitor Logs**: Regularly check system logs for issues
3. **Backup Configuration**: Backup configuration files before making changes
4. **Test Changes**: Test configuration changes in a non-production environment
5. **Monitor Performance**: Track system performance and resource usage

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the project repository or contact the maintainers.

## Changelog

### Version 1.0.3
- Added real-time device monitoring
- Improved authentication system
- Enhanced firewall management
- Better error handling and logging
- Rich console output for better UX

### Version 1.0.2
- Initial stable release
- Basic captive portal functionality
- Device authentication
- Configuration management

## Contact

For more information, please contact the project maintainers.
