import socket
import json
import threading
import queue
from typing import Any, List, Callable, Dict, Optional, Union
from base64 import b64encode

class DushyRedisClient:
    """
    A Python client for the Redis-clone server.
    
    Example usage:
        client = DushyRedisClient.connect()
        await client.set("key", "value")
        value = await client.get("key")
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 6379):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.response_queue = queue.Queue()
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.running = False
        self._read_thread = None

    @classmethod
    def connect(cls, host: str = '127.0.0.1', port: int = 6379) -> 'DushyRedisClient':
        """
        Creates and connects a new client instance.
        
        Args:
            host: Server hostname
            port: Server port
            
        Returns:
            Connected DushyRedisClient instance
        """
        client = cls(host, port)
        client._connect()
        return client

    def _connect(self) -> None:
        self.socket.connect((self.host, self.port))
        self.running = True
        self._read_thread = threading.Thread(target=self._read_responses)
        self._read_thread.daemon = True
        self._read_thread.start()

    def _read_responses(self) -> None:
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line:
                        continue

                    if line.startswith('Message'):
                        # Handle pub/sub messages
                        try:
                            _, channel, json_str = line.split(' ', 2)
                            message = json.loads(json_str)
                            if channel in self.subscriptions:
                                content = message['Content']
                                msg_type = message['Type']
                                
                                for callback in self.subscriptions[channel]:
                                    if msg_type == 2:  # BinaryMessage
                                        content = bytes(content)
                                    callback(content)
                        except Exception as e:
                            print(f"Error processing message: {e}")
                    else:
                        self.response_queue.put(line.strip())

            except Exception as e:
                print(f"Read error: {e}")
                break

    def _send_command(self, command: str) -> str:
        """Sends a command and returns the response."""
        self.socket.send(f"{command}\n".encode('utf-8'))
        return self.response_queue.get()

    def set(self, key: str, value: Any) -> bool:
        """Sets a key-value pair."""
        if isinstance(value, str):
            value = f'"{value}"'
        response = self._send_command(f"SET {key} {value}")
        return response == "OK"

    def get(self, key: str) -> Optional[str]:
        """Gets a value by key."""
        response = self._send_command(f"GET {key}")
        return None if response == "(nil)" else response

    def lpush(self, key: str, values: List[Any]) -> int:
        """Pushes values to the left of a list."""
        response = self._send_command(f"LPUSH {key} {' '.join(map(str, values))}")
        return int(response)

    def rpush(self, key: str, values: List[Any]) -> int:
        """Pushes values to the right of a list."""
        response = self._send_command(f"RPUSH {key} {' '.join(map(str, values))}")
        return int(response)

    def lpop(self, key: str) -> Optional[str]:
        """Pops a value from the left of a list."""
        response = self._send_command(f"LPOP {key}")
        return None if response == "(nil)" else response

    def rpop(self, key: str) -> Optional[str]:
        """Pops a value from the right of a list."""
        response = self._send_command(f"RPOP {key}")
        return None if response == "(nil)" else response

    def sadd(self, key: str, members: List[Any]) -> int:
        """Adds members to a set."""
        response = self._send_command(f"SADD {key} {' '.join(map(str, members))}")
        return int(response)

    def smembers(self, key: str) -> Optional[List[str]]:
        """Gets all members of a set."""
        response = self._send_command(f"SMEMBERS {key}")
        return None if response == "(nil)" else response.split()

    def hset(self, key: str, field: str, value: Any) -> bool:
        """Sets a field in a hash."""
        response = self._send_command(f"HSET {key} {field} {value}")
        return response == "OK"

    def hget(self, key: str, field: str) -> Optional[str]:
        """Gets a field from a hash."""
        response = self._send_command(f"HGET {key} {field}")
        return None if response == "(nil)" else response

    def subscribe(self, channel: str, callback: Callable[[Any], None]) -> bool:
        """
        Subscribes to a channel.
        
        Args:
            channel: Channel name
            callback: Function to call when messages are received
        """
        if channel not in self.subscriptions:
            self.subscriptions[channel] = []
        self.subscriptions[channel].append(callback)
        response = self._send_command(f"SUBSCRIBE {channel}")
        return response == "OK"

    def publish(self, channel: str, message: str) -> bool:
        """Publishes a string message to a channel."""
        response = self._send_command(f"PUBLISH {channel} {message}")
        return response == "OK"

    def publish_json(self, channel: str, data: Any) -> bool:
        """Publishes JSON data to a channel."""
        json_str = json.dumps(data)
        response = self._send_command(f"PUBLISH_JSON {channel} {json_str}")
        return response == "OK"

    def publish_int(self, channel: str, number: int) -> bool:
        """Publishes an integer to a channel."""
        response = self._send_command(f"PUBLISH_INT {channel} {number}")
        return response == "OK"

    def publish_binary(self, channel: str, data: bytes) -> bool:
        """Publishes binary data to a channel."""
        encoded = b64encode(data).decode('utf-8')
        response = self._send_command(f"PUBLISH_BIN {channel} {encoded}")
        return response == "OK"

    def publish_array(self, channel: str, array: List[Any]) -> bool:
        """Publishes an array to a channel."""
        json_arr = json.dumps(array)
        response = self._send_command(f"PUBLISH_ARRAY {channel} {json_arr}")
        return response == "OK"

    def close(self) -> None:
        """Closes the connection."""
        self.running = False
        self.socket.close()
