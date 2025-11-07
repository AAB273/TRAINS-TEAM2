import socket
import threading
import json
from typing import Dict, Set, Callable, Optional

class TrainSocketServer:
    def __init__(self, port=12345, ui_id: str = None):
        self.port = port
        self.ui_id = ui_id or f"ui_{port}"
        self.server_socket = None
        self.running = False
        self.connected_clients: Dict[str, socket.socket] = {}
        self.allowed_connections: Set[str] = set()  # IDs of UIs this UI can communicate with
        self.max_connections = 3
        self.update_callback: Optional[Callable] = None
        
    def set_allowed_connections(self, ui_ids: list):
        """Set which UI IDs this server can communicate with (max 2)"""
        self.allowed_connections = set(ui_ids[:self.max_connections])
        print(f"UI {self.ui_id} can communicate with: {self.allowed_connections}")
        
    def start_server(self, update_callback):
        """Start the socket server in a separate thread"""
        self.update_callback = update_callback
        self.running = True
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(5)
            print(f"Train GUI Server {self.ui_id} listening on port {self.port}")
            
            # Start accepting connections in background thread
            self.thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.thread.start()
        except Exception as e:
            print(f"Failed to start server: {e}")
            
    def _accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Connection from {addr}")
                
                # Start handshake to identify the client
                handshake_thread = threading.Thread(
                    target=self._handle_handshake, 
                    args=(client_socket,), 
                    daemon=True
                )
                handshake_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Connection error: {e}")
                    
    def _handle_handshake(self, client_socket):
        """Handle initial handshake to identify and validate the connecting UI"""
        try:
            # Wait for identification message
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                client_socket.close()
                return
                
            message = json.loads(data)
            if message.get('type') == 'handshake':
                client_ui_id = message.get('ui_id')
                
                # Check if this UI is allowed to connect
                if client_ui_id in self.allowed_connections:
                    self.connected_clients[client_ui_id] = client_socket
                    print(f"Accepted connection from {client_ui_id}")
                    
                    # Send acknowledgment
                    ack = {'type': 'handshake_ack', 'status': 'accepted', 'ui_id': self.ui_id}
                    client_socket.send(json.dumps(ack).encode('utf-8'))
                    
                    # Start handling messages from this client
                    threading.Thread(
                        target=self._handle_client, 
                        args=(client_socket, client_ui_id), 
                        daemon=True
                    ).start()
                else:
                    print(f"Rejected connection from unauthorized UI: {client_ui_id}")
                    reject_msg = {'type': 'handshake_ack', 'status': 'rejected'}
                    client_socket.send(json.dumps(reject_msg).encode('utf-8'))
                    client_socket.close()
                    
        except Exception as e:
            print(f"Handshake error: {e}")
            client_socket.close()
                    
    def _handle_client(self, client_socket, client_ui_id):
        """Handle client messages - with multiple JSON support"""
        buffer = ""
        while self.running:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                
                # Try to parse complete JSON objects from buffer
                while buffer:
                    try:
                        # Find complete JSON object
                        message, idx = self._extract_json(buffer)
                        if message:
                            if message.get('type') != 'handshake':
                                if self.update_callback:
                                    self.update_callback(message, client_ui_id)
                            buffer = buffer[idx:]  # Remove processed part
                        else:
                            break  # Incomplete JSON, wait for more data
                    except json.JSONDecodeError:
                        # If we can't parse, clear buffer to prevent buildup
                        print("JSON decode error, clearing buffer")
                        buffer = ""
                        break
                        
            except Exception as e:
                print(f"Client handling error: {e}")
                break
                
        # Clean up disconnected client
        if client_ui_id in self.connected_clients:
            del self.connected_clients[client_ui_id]
        client_socket.close()
        print(f"Client {client_ui_id} disconnected")

    def _extract_json(self, buffer):
        """Extract first complete JSON object from buffer"""
        try:
            # Try to parse the entire buffer
            message = json.loads(buffer)
            return message, len(buffer)
        except json.JSONDecodeError:
            # If that fails, try to find where the JSON ends
            # This is a simple approach - look for balanced braces
            brace_count = 0
            in_string = False
            escape = False
            
            for i, char in enumerate(buffer):
                if escape:
                    escape = False
                    continue
                    
                if char == '\\':
                    escape = True
                elif char == '"' and not escape:
                    in_string = not in_string
                elif not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found complete JSON object
                            try:
                                message = json.loads(buffer[:i+1])
                                return message, i+1
                            except json.JSONDecodeError:
                                continue
            
            return None, 0  # No complete JSON found
        
    def connect_to_ui(self, host: str, port: int, target_ui_id: str):
        """Connect to another UI server"""
        if target_ui_id not in self.allowed_connections:
            print(f"Cannot connect to {target_ui_id} - not in allowed connections")
            return False
            
        if target_ui_id in self.connected_clients:
            print(f"Already connected to {target_ui_id}")
            return True
            
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            
            # Send handshake to identify ourselves
            handshake = {'type': 'handshake', 'ui_id': self.ui_id}
            client_socket.send(json.dumps(handshake).encode('utf-8'))
            
            # Wait for acknowledgment
            data = client_socket.recv(1024).decode('utf-8')
            ack = json.loads(data)
            
            if ack.get('status') == 'accepted':
                self.connected_clients[target_ui_id] = client_socket
                print(f"Successfully connected to {target_ui_id}")
                
                # Start handling messages from this connection
                threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, target_ui_id), 
                    daemon=True
                ).start()
                return True
            else:
                print(f"Connection rejected by {target_ui_id}")
                client_socket.close()
                return False
                
        except Exception as e:
            print(f"Failed to connect to {target_ui_id}: {e}")
            return False
    
    def send_to_ui(self, target_ui_id: str, message: dict):
        """Send a message to a specific UI"""
        if target_ui_id not in self.allowed_connections:
            print(f"Cannot send to {target_ui_id} - not in allowed connections")
            return False
            
        if target_ui_id not in self.connected_clients:
            print(f"Not connected to {target_ui_id}")
            return False
            
        try:
            client_socket = self.connected_clients[target_ui_id]
            client_socket.send(json.dumps(message).encode('utf-8'))
            return True
        except Exception as e:
            print(f"Failed to send to {target_ui_id}: {e}")
            # Clean up broken connection
            if target_ui_id in self.connected_clients:
                del self.connected_clients[target_ui_id]
            return False
    
    def broadcast_to_allowed(self, message: dict):
        """Broadcast a message to all allowed and connected UIs"""
        success_count = 0
        for ui_id in list(self.connected_clients.keys()):
            if self.send_to_ui(ui_id, message):
                success_count += 1
        return success_count

    def stop_server(self):
        """Stop the server and close all connections"""
        self.running = False
        
        # Close all client connections
        for client_socket in self.connected_clients.values():
            try:
                client_socket.close()
            except:
                pass
        self.connected_clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print(f"Socket server {self.ui_id} stopped")
    
    



"""
USAGE EXAMPLE

# UI 1 - Can communicate with UI 2 and UI 3
server1 = TrainSocketServer(port=12345, ui_id="ui_1")
server1.set_allowed_connections(["ui_2", "ui_3"])
server1.start_server(update_callback)

# Connect to other UIs
server1.connect_to_ui('localhost', 12346, "ui_2")
server1.connect_to_ui('localhost', 12347, "ui_3")

# Send a message to UI 2
server1.send_to_ui("ui_2", {"command": "set_power", "value": 0.5})

#Need to create your own "process_message" function that proccesses the commands other UI's send to so that you can act on those commands.
Look at Train Model Passenger Ui for an example of what it looks like. 
For Test UI's, put this section of code into your _init_ definition

def empty_handler(message, source_ui_id):
            print(f"Test UI received: {message} from {source_ui_id}")
        
        self.server.start_server(empty_handler)
        # then connect to the server here.


#You also need to create a "launch_both".py file that launches both the UI's at the same time so they connect. Loom at Alex's example of launch both.py
and just change the file address of the UI's to yours.
"""