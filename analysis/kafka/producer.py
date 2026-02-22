#import json
#from kafka import KafkaProducer

#producer = KafkaProducer(
#    bootstrap_servers=["127.0.0.1:9092"],
#    value_serializer=lambda v: json.dumps(v).encode(),
#    linger_ms=10,
#    batch_size=64 * 1024,
#)

from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("Kafka producer started...")

while True:
    event = {
        "user_id": random.randint(1, 5),
        "event_type": random.choice(["click", "purchase"]),
        "value": 1,
        "timestamp": int(time.time())
    }

    producer.send("events", event)
    producer.flush()

    print("send:", event)
    time.sleep(1)