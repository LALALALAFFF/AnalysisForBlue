# analysis/services/feature_builder.py

from collections import defaultdict
from django.utils.timezone import localdate

from player.models import ActionLog, PlayerBasic
from analysis.models import PlayerFeatureVector


def build_player_features(uid):
    player = PlayerBasic.objects.get(uid=uid)
    logs = ActionLog.objects.filter(uid=uid)

    if not logs.exists():
        return None

    # —— 基础统计 ——
    login_count = 0
    battle_count = 0
    win_count = 0

    total_play_time = 0
    active_days = set()

    total_consume = 0
    purchase_count = 0

    behavior_time = defaultdict(int)

    for log in logs:
        event = log.event_type
        payload = log.payload or {}

        # 活跃天数
        active_days.add(localdate(log.created_at))

        # 行为时长
        duration = payload.get("duration", 0)
        total_play_time += duration
        behavior_time[event] += duration

        # 行为计数
        if event == "login":
            login_count += 1

        elif event == "battle":
            battle_count += 1
            if payload.get("result") == "win":
                win_count += 1

        elif event == "purchase":
            purchase_count += 1
            total_consume += payload.get("amount", 0)

    # —— 派生特征 ——
    win_rate = win_count / battle_count if battle_count else 0
    avg_order_value = total_consume / purchase_count if purchase_count else 0

    # 行为偏好向量（归一化）
    total_behavior_time = sum(behavior_time.values())
    behavior_vector = {
        k: round(v / total_behavior_time, 3)
        for k, v in behavior_time.items()
        if total_behavior_time > 0
    }

    PlayerFeatureVector.objects.update_or_create(
        player=player,
        defaults={
            "total_play_time": total_play_time,
            "active_days": len(active_days),
            "login_count": login_count,
            "battle_count": battle_count,
            "win_rate": win_rate,
            "total_consume": total_consume,
            "avg_order_value": avg_order_value,
            "behavior_vector": behavior_vector,
        }
    )

    return True
