import socket
import pickle
from pynput import mouse, keyboard
import threading
import time

class MouseKeyboardClient:
    def __init__(self, host='localhost', port=5001):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.is_active = False
        self.screen_width = 1920  # Default value, should be adjusted
        self.screen_height = 1080  # Default value, should be adjusted

    def connect(self):
        try:
            print(f"Attempting to connect to {self.host}:{self.port}...")
            
            # Try to resolve the hostname first
            try:
                socket.gethostbyname(self.host)
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

        # Start mouse listener
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

        # Keep the main thread running
        try:
            while self.is_active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping client...")
        finally:
            self.client_socket.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = 'localhost'
    
    client = MouseKeyboardClient(host=host)
    client.start()
