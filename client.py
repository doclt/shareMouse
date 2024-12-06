import socket
import pickle
from pynput import mouse, keyboard
import threading
import time
import subprocess
import sys
import platform
import os
import netifaces

class MouseKeyboardClient:
    def __init__(self, host='localhost', port=8001):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.is_active = False
        self.screen_width = 1920  # Default value, should be adjusted
        self.screen_height = 1080  # Default value, should be adjusted

    def print_network_info(self):
        """Print detailed network interface information"""
        print("\n=== Network Interface Information ===")
        try:
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                print(f"\nInterface: {interface}")
                try:
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            print(f"  IP Address: {addr['addr']}")
                            if 'netmask' in addr:
                                print(f"  Netmask: {addr['netmask']}")
                except Exception as e:
                    print(f"  Error getting address info: {e}")
        except Exception as e:
            print(f"Error getting network interfaces: {e}")

    def test_connectivity(self):
        """Test connectivity using system ping command"""
        try:
            # Print network information first
            self.print_network_info()
            
            print(f"\n=== Testing connectivity to {self.host} ===")
            
            # Try regular ping first
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', self.host]
            
            print(f"Testing with regular ping...")
            result = subprocess.run(command, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
            
            print(result.stdout)
            
            if result.returncode == 0:
                print("Regular ping successful!")
                return True
            
            # If regular ping failed and we're on Unix-like system, try with sudo
            if platform.system() != 'Windows':
                print("\nTrying with sudo ping...")
                command = ['sudo', 'ping', param, '1', self.host]
                result = subprocess.run(command, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
                print(result.stdout)
                
                if result.returncode == 0:
                    print("Sudo ping successful!")
                    return True
                    
            print("All ping attempts failed!")
            return False
            
        except Exception as e:
            print(f"Error during ping test: {e}")
            return False

    def connect(self):
        try:
            print(f"Attempting to connect to {self.host}:{self.port}...")
            
            # First test connectivity using system ping
            if not self.test_connectivity():
                print("Warning: System ping failed, but attempting socket connection anyway...")
            
            # Try to resolve the hostname first
            try:
                resolved_ip = socket.gethostbyname(self.host)
                print(f"Resolved {self.host} to IP: {resolved_ip}")
            except socket.gaierror:
                print(f"Error: Could not resolve hostname '{self.host}'")
                print("Tips: ")
                print("1. Make sure you're using the correct IP address")
                print("2. If using hostname, ensure it can be resolved")
                return False
                
            # Try to connect with a timeout
            self.client_socket.settimeout(5)  # 5 second timeout
            self.client_socket.connect((self.host, self.port))
            self.client_socket.settimeout(None)  # Reset timeout
            self.is_active = True
            print(f"Successfully connected to server at {self.host}:{self.port}")
            return True
            
        except socket.timeout:
            print(f"Connection timed out when trying to connect to {self.host}:{self.port}")
            print("Tips:")
            print("1. Verify the server is running")
            print("2. Check if a firewall is blocking the connection")
            print("3. Ensure both computers are on the same network")
            return False
        except ConnectionRefusedError:
            print(f"Connection refused by {self.host}:{self.port}")
            print("Tips:")
            print("1. Make sure the server is running")
            print("2. Verify the correct port number is being used")
            print("3. Check if any firewall is blocking incoming connections on the server")
            return False
        except OSError as e:
            if "No route to host" in str(e):
                print(f"No route to host {self.host}:{self.port}")
                print("Tips:")
                print("1. Verify both computers are on the same network")
                print("2. Try pinging the server IP address")
                print("3. Check network settings and firewalls")
                print("4. Ensure the IP address is correct")
            else:
                print(f"Connection error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while connecting: {e}")
            return False

    def send_event(self, event):
        try:
            data = pickle.dumps(event)
            self.client_socket.send(data)
        except Exception as e:
            print(f"Error sending event: {e}")
            self.is_active = False

    def on_mouse_move(self, x, y):
        if self.is_active:
            # Convert coordinates to relative position (0-1)
            rel_x = x / self.screen_width
            rel_y = y / self.screen_height
            event = {
                'type': 'mouse_move',
                'x': rel_x,
                'y': rel_y
            }
            self.send_event(event)

    def on_mouse_click(self, x, y, button, pressed):
        if self.is_active:
            event = {
                'type': 'mouse_click',
                'button': button,
                'pressed': pressed
            }
            self.send_event(event)

    def on_mouse_scroll(self, x, y, dx, dy):
        if self.is_active:
            event = {
                'type': 'mouse_scroll',
                'dx': dx,
                'dy': dy
            }
            self.send_event(event)

    def on_key_press(self, key):
        if self.is_active:
            event = {
                'type': 'key',
                'key': key,
                'pressed': True
            }
            self.send_event(event)

    def on_key_release(self, key):
        if self.is_active:
            event = {
                'type': 'key',
                'key': key,
                'pressed': False
            }
            self.send_event(event)

    def start(self):
        if not self.connect():
            return

        # Get actual screen resolution
        with mouse.Controller() as mouse_controller:
            screen_info = mouse_controller._display.screen()
            self.screen_width = screen_info.width_px
            self.screen_height = screen_info.height_px
            print(f"Screen resolution: {self.screen_width}x{self.screen_height}")

        # Start mouse listener with proper movement tracking
        mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        mouse_listener.start()

        # Start keyboard listener
        keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        keyboard_listener.start()

        # Keep the main thread alive
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping client...")
            self.is_active = False
            mouse_listener.stop()
            keyboard_listener.stop()
            self.client_socket.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = 'localhost'
    
    client = MouseKeyboardClient(host=host)
    client.start()
