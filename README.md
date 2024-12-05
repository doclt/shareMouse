# ShareMouse Clone

A simple Python application to share mouse and keyboard between two computers over the network.

## Requirements

- Python 3.7+
- pynput
- python-xlib (for Linux systems)

## Installation
sudo lsof -i :5000    # Find the process using port 5000
sudo kill <PID>       # Kill the process with the given PID
1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. On the computer that will be controlled (receiver):
```bash
python server.py
```

2. On the computer that will control (sender):
```bash
python client.py <server_ip>
```
Replace `<server_ip>` with the IP address of the receiver computer.

For example:
```bash
python client.py 192.168.1.100
```

## Features

- Mouse movement sharing
- Mouse click sharing
- Mouse scroll sharing
- Keyboard input sharing

## Notes

- Both computers must be on the same network
- The server needs to be started before the client
- To stop the application, press Ctrl+C in the terminal
- Make sure to allow the application through your firewall
- The default port used is 5000

## Security Notice

This is a basic implementation and should only be used in trusted networks. The communication is not encrypted.
