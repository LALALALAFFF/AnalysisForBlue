# analysis/utils.py

def build_feature_vector(pfv):
    """
    将 PlayerFeatureVector 转换为数值向量
    顺序非常重要：后续聚类 + 标签规则都依赖这个顺序
    """

    behavior = pfv.behavior_vector or {}

    behavior_vec = [
        behavior.get("battle", 0.0),
        behavior.get("gacha", 0.0),
        behavior.get("purchase", 0.0),
        behavior.get("explore", 0.0),
    ]

    return [
        pfv.total_play_time,
        pfv.active_days,
        pfv.login_count,
        pfv.battle_count,
        pfv.win_rate,
        pfv.total_consume,
        pfv.avg_order_value,
    ] + behavior_vec
