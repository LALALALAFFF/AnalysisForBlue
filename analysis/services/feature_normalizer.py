import numpy as np
from collections import defaultdict
from analysis.models import PlayerFeatureVector


BEHAVIOR_KEYS = [
    "explore",
    "gacha",
    "purchase",
    "daily_task",
    "event_task",
    "material_farm",
]


def normalize_by_percentile(p=95):
    """
    使用 P95 做 xmax
    y = x / xmax
    超过则截断 1.0
    """

    qs = PlayerFeatureVector.objects.all()

    # 收集所有玩家原始值
    raw_map = defaultdict(list)

    for fv in qs:
        bv = fv.behavior_vector or {}
        for k in BEHAVIOR_KEYS:
            raw_map[k].append(float(bv.get(k, 0)))

    # 计算 P95
    percentile_map = {}
    for k, values in raw_map.items():
        if not values:
            percentile_map[k] = 1
        else:
            percentile_map[k] = np.percentile(values, p)

    # 归一化
    normalized_data = {}

    for fv in qs:
        bv = fv.behavior_vector or {}
        norm_vec = {}

        for k in BEHAVIOR_KEYS:
            x = float(bv.get(k, 0))
            xmax = percentile_map[k] or 1
            y = x / xmax
            norm_vec[k] = min(round(y, 4), 1.0)

        normalized_data[fv.player.id] = norm_vec

    return normalized_data