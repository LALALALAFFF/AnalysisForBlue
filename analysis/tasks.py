"""
from celery import shared_task
from player.models import ActionLog

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def save_event_async(self, data):

    data: dict，从 Kafka 传过来的一条事件

    ActionLog.objects.create(
        uid=data["uid"],
        session_id=data.get("session_id", ""),
        event_type=data["event_type"],
        payload=data,
    )"""
from celery import shared_task
from django.utils.dateparse import parse_datetime

from player.models import ActionLog


@shared_task(
    name="analysis.save_event_async",
    queue="analysis_queue",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 3},
)
def save_event_async(self, data):
    """
    消费队列：把事件写入 ActionLog
    data: {uid, session_id, event_type, payload, created_at(iso)}
    """
    created_at = parse_datetime(data.get("created_at"))

    ActionLog.objects.create(
        uid=int(data["uid"]),
        session_id=int(data["session_id"]),
        event_type=str(data["event_type"]),
        payload=data.get("payload", {}),
        created_at=created_at,
    )

    return True
