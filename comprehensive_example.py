from dushy_redis_lib import DushyRedisClient
import time
from datetime import datetime
import json

def log(message):
    """Helper to print timestamped messages"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def handle_string_messages(message):
    log(f"Received string message: {message}")

def handle_json_messages(message):
    log(f"Received JSON message: {message}")
    log(f"Access nested data: {message.get('nested', {}).get('value')}")

def handle_binary_messages(message):
    log(f"Received binary message: {message}")
    log(f"Decoded text: {message.decode('utf-8')}")

def handle_int_messages(message):
    log(f"Received integer message: {message}")
    log(f"Incremented value: {message + 1}")

def handle_array_messages(message):
    log(f"Received array message: {message}")
    log(f"Array length: {len(message)}")

def main():
    # Connect to the server
    client = DushyRedisClient.connect()
    log("Connected to Redis server")

    # 1. String Operations
    log("\n=== String Operations ===")
    client.set("greeting", "Hello, Redis!")
    client.set("number", 42)
    client.set("json_str", json.dumps({"hdshb": "value"}))

    log(f"greeting: {client.get('greeting')}")
    log(f"number: {client.get('number')}")
    log(f"json_str: {client.get('json_str')}")

    # 2. List Operations
    log("\n=== List Operations ===")
    client.lpush("my_list", ["first", "second"])
    client.rpush("my_list", ["third", "fourth"])

    log(f"Left pop: {client.lpop('my_list')}")
    log(f"Right pop: {client.rpop('my_list')}")

    # 3. Set Operations
    log("\n=== Set Operations ===")
    client.sadd("my_set", ["apple", "banana", "apple", "cherry"])
    members = client.smembers("my_set")
    log(f"Set members: {members}")

    # 4. Hash Operations
    log("\n=== Hash Operations ===")
    client.hset("user:1", "name", "John Doe")
    client.hset("user:1", "email", "john@example.com")
    client.hset("user:1", "age", "30")

    log(f"User name: {client.hget('user:1', 'name')}")
    log(f"User email: {client.hget('user:1', 'email')}")
    log(f"User age: {client.hget('user:1', 'age')}")

    # 5. Pub/Sub Operations
    log("\n=== Pub/Sub Operations ===")
    
    # Subscribe to different channels for different message types
    client.subscribe("string_channel", handle_string_messages)
    client.subscribe("json_channel", handle_json_messages)
    client.subscribe("binary_channel", handle_binary_messages)
    client.subscribe("int_channel", handle_int_messages)
    client.subscribe("array_channel", handle_array_messages)

    # Publish different types of messages
    log("Publishing messages...")
    
    # String message
    client.publish("string_channel", "Hello, subscribers!")

    # JSON message
    client.publish_json("json_channel", {
        "name": "JSON Message",
        "timestamp": time.time(),
        "nested": {"value": 42}
    })

    # Binary message
    client.publish_binary("binary_channel", "Binary Data 🚀".encode('utf-8'))

    # Integer message
    client.publish_int("int_channel", 42)

    # Array message
    client.publish_array("array_channel", [1, "two", {"three": 3}, [4, 5]])

    # Keep the program running to receive messages
    log("\nListening for messages (press Ctrl+C to exit)...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Shutting down...")
        client.close()

if __name__ == "__main__":
    main()
