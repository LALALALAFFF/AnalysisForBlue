import math
from collections import defaultdict

from django.utils.timezone import localdate
from django.db import transaction

from player.models import ActionLog, PlayerBasic
from analysis.models import PlayerFeatureVector, PlayerFeatureHistory


# =========================
# 工具函数
# =========================

def sigmoid(x):
    if x > 10:
        return 1.0
    if x < -10:
        return 0.0
    return 1 / (1 + math.exp(-x))


def compute_raw_score(freq, duration, alpha=0.6, beta=0.4):
    return alpha * math.log1p(freq) + beta * math.log1p(duration)


# =========================
# 主函数：全量重建
# =========================

@transaction.atomic
def build_all_player_features():

    players = PlayerBasic.objects.all()

    # 存储所有玩家 raw 数据
    player_raw_map = {}
    global_raw_values = defaultdict(list)

    # =========================
    # 第一阶段：计算所有玩家 raw
    # =========================

    for player in players:

        logs = ActionLog.objects.filter(uid=player.uid)

        behavior_time = defaultdict(int)
        behavior_count = defaultdict(int)

        login_count = 0
        battle_count = 0
        win_count = 0
        total_play_time = 0
        total_consume = 0
        purchase_count = 0
        active_days_set = set()

        for log in logs:

            event = log.event_type
            payload = log.payload or {}

            active_days_set.add(str(localdate(log.created_at)))

            duration = payload.get("duration", 0)
            total_play_time += duration

            behavior_time[event] += duration
            behavior_count[event] += 1

            if event == "login":
                login_count += 1

            elif event == "battle":
                battle_count += 1
                if payload.get("result") == "win":
                    win_count += 1

            elif event == "purchase":
                purchase_count += 1
                total_consume += payload.get("amount", 0)

        win_rate = win_count / battle_count if battle_count else 0
        avg_order_value = total_consume / purchase_count if purchase_count else 0

        raw_behavior_scores = {}

        for event in behavior_time.keys():

            freq = behavior_count.get(event, 0)
            duration = behavior_time.get(event, 0)

            # 提升抽卡和购买权重
            if event in ("gacha", "purchase"):
                raw = compute_raw_score(freq, duration, alpha=0.7, beta=0.3)
            else:
                raw = compute_raw_score(freq, duration)

            raw_behavior_scores[event] = raw
            global_raw_values[event].append(raw)

        player_raw_map[player.uid] = {
            "raw": raw_behavior_scores,
            "total_play_time": total_play_time,
            "active_days": len(active_days_set),
            "login_count": login_count,
            "battle_count": battle_count,
            "win_rate": win_rate,
            "total_consume": total_consume,
            "avg_order_value": avg_order_value,
        }

    # =========================
    # 第二阶段：计算全局 mean + std
    # =========================

    global_mean = {}
    global_std = {}

    for event, values in global_raw_values.items():

        if not values:
            global_mean[event] = 0
            global_std[event] = 1
            continue

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)

        global_mean[event] = mean
        global_std[event] = std if std > 0 else 1

    # =========================
    # 第三阶段：统一计算 score 并入库
    # =========================

    for player in players:

        data = player_raw_map[player.uid]
        raw_scores = data["raw"]

        behavior_vector = {}

        for event, raw_value in raw_scores.items():

            mean = global_mean.get(event, 0)
            std = global_std.get(event, 1)

            z = (raw_value - mean) / std
            score = sigmoid(z)

            behavior_vector[event] = round(score, 4)

        PlayerFeatureVector.objects.update_or_create(
            player=player,
            defaults={
                "total_play_time": data["total_play_time"],
                "active_days": data["active_days"],
                "login_count": data["login_count"],
                "battle_count": data["battle_count"],
                "win_rate": data["win_rate"],
                "total_consume": data["total_consume"],
                "avg_order_value": data["avg_order_value"],
                "behavior_vector": behavior_vector,
            }
        )

    return True