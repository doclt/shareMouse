import socket
import pickle
from pynput import mouse, keyboard
import threading

class MouseKeyboardServer:
    def __init__(self, host='0.0.0.0', port=5001):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Add socket option to allow port reuse
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((host, port))
            self.server_socket.listen(1)
            self.mouse_controller = mouse.Controller()
            self.keyboard_controller = keyboard.Controller()
            print(f"Server listening on {host}:{port}")
        except PermissionError:
            print("Error: Permission denied. Try running with sudo or use a port number above 1024")
            raise
        except OSError as e:
            if e.errno == 48 or e.errno == 98:  # Address already in use
                print("Error: Port is already in use. Try these solutions:")
                print("1. Wait a few minutes for the port to be released")
                print("2. Kill any process using this port:")
                print(f"   sudo lsof -i :{port}")
                print(f"3. Or try a different port by modifying the port number")
            else:
                print(f"Socket error: {e}")
            raise

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                event = pickle.loads(data)
                event_type = event.get('type')
                
                if event_type == 'mouse_move':
                    self.mouse_controller.position = (event['x'], event['y'])
                elif event_type == 'mouse_click':
                    button = event['button']
                    pressed = event['pressed']
                    if pressed:
                        self.mouse_controller.press(button)
                    else:
                        self.mouse_controller.release(button)
                elif event_type == 'mouse_scroll':
                    self.mouse_controller.scroll(event['dx'], event['dy'])
                elif event_type == 'key':
                    key = event['key']
                    pressed = event['pressed']
                    if pressed:
                        self.keyboard_controller.press(key)
                    else:
                        self.keyboard_controller.release(key)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connected to client: {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

if __name__ == '__main__':
    import sys
    port = 5001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Error: Port must be a number")
            sys.exit(1)
    
    server = MouseKeyboardServer(port=port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
