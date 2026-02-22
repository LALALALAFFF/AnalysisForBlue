import os
import sys
import django
import json

# ====== 关键修复点 ======
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
# =======================

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "analysisapp.settings")
django.setup()

from kafka import KafkaConsumer
from analysis.tasks import save_event_async

consumer = KafkaConsumer(
    "player-events",
    bootstrap_servers=["127.0.0.1:9092"],
    value_deserializer=lambda v: json.loads(v.decode()),
    group_id="analysis-group",
    auto_offset_reset="earliest",
    max_poll_records=500,
)

print("Kafka consumer started...")

for msg in consumer:
    save_event_async.delay(msg.value)