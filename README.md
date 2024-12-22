# DushyRedis Python Client

A feature-rich Python client for the Redis-clone server with support for strings, lists, sets, hashes, and pub/sub messaging.

## Installation

```bash
pip install dushy-redis
```

## Quick Start

```python
from dushy_redis_lib import DushyRedisClient

# Connect to server
client = DushyRedisClient.connect()

# Basic operations
client.set("key", "value")
value = client.get("key")

# Close connection when done
client.close()
```

## Features

- String operations
- List operations (LPUSH, RPUSH, LPOP, RPOP)
- Set operations (SADD, SMEMBERS)
- Hash operations (HSET, HGET)
- Pub/Sub with support for multiple message types:
  - String messages
  - JSON messages
  - Binary data
  - Integers
  - Arrays

## API Reference

### Connection

```python
client = DushyRedisClient.connect(host='127.0.0.1', port=6379)
```

### String Operations

```python
client.set(key: str, value: Any) -> bool
client.get(key: str) -> Optional[str]
```

### List Operations

```python
client.lpush(key: str, values: List[Any]) -> int
client.rpush(key: str, values: List[Any]) -> int
client.lpop(key: str) -> Optional[str]
client.rpop(key: str) -> Optional[str]
```

### Set Operations

```python
client.sadd(key: str, members: List[Any]) -> int
client.smembers(key: str) -> Optional[List[str]]
```

### Hash Operations

```python
client.hset(key: str, field: str, value: Any) -> bool
client.hget(key: str, field: str) -> Optional[str]
```

### Pub/Sub Operations

```python
# Subscribe to channel
def callback(message):
    print(f"Received: {message}")
client.subscribe(channel: str, callback: Callable) -> bool

# Publishing different types of messages
client.publish(channel: str, message: str) -> bool
client.publish_json(channel: str, data: Any) -> bool
client.publish_binary(channel: str, data: bytes) -> bool
client.publish_int(channel: str, number: int) -> bool
client.publish_array(channel: str, array: List[Any]) -> bool
```

## Example Usage

Check out `comprehensive_example.py` for a complete demonstration of all features:

```python
# Basic string operations
client.set("greeting", "Hello, Redis!")
print(client.get("greeting"))  # Output: Hello, Redis!

# List operations
client.lpush("my_list", ["first", "second"])
client.rpush("my_list", ["third", "fourth"])

# Set operations
client.sadd("my_set", ["apple", "banana", "cherry"])
print(client.smembers("my_set"))  # Output: ['apple', 'banana', 'cherry']

# Hash operations
client.hset("user:1", "name", "John")
print(client.hget("user:1", "name"))  # Output: John

# Pub/Sub with different message types
def handle_messages(message):
    print(f"Received: {message}")

client.subscribe("channel", handle_messages)
client.publish_json("channel", {"hello": "world"})
```

## Error Handling

The client handles connection errors and malformed responses gracefully. All methods return `None` or `False` on failure.

## Thread Safety

The client uses a dedicated thread for reading responses and is thread-safe for concurrent operations.
