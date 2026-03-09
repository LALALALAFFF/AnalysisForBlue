import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from django.utils import timezone

from analysis.models import PlayerFeatureVector
from analysis.models import PlayerClusterProfile


LEVEL_NAME_MAP = {
    0: "low",
    1: "mid",
    2: "high"
}


def _cluster_dimension(values):
    """
    对某一个维度做 3 类聚类
    返回 每个值对应的 level
    """

    X = np.array(values).reshape(-1, 1)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # 根据中心点排序（保证 0=低 1=中 2=高）
    centers = kmeans.cluster_centers_.flatten()
    sorted_idx = np.argsort(centers)

    level_map = {
        sorted_idx[0]: 0,
        sorted_idx[1]: 1,
        sorted_idx[2]: 2,
    }

    final_levels = [level_map[l] for l in labels]

    return final_levels


def run_tag_clustering():

    print("=== 开始标签聚类 ===")

    qs = PlayerFeatureVector.objects.select_related("player")

    if not qs.exists():
        print("没有特征数据")
        return

    players = []
    spender_values = []
    skill_values = []
    activity_values = []
    gacha_values = []

    for fv in qs:
        players.append(fv.player)

        spender_values.append(fv.total_consume)
        skill_values.append(fv.win_rate)
        activity_values.append(fv.active_days)
        gacha_values.append(
            fv.behavior_vector.get("gacha", 0.0)
        )

    # 分维度聚类
    spender_levels = _cluster_dimension(spender_values)
    skill_levels = _cluster_dimension(skill_values)
    activity_levels = _cluster_dimension(activity_values)
    gacha_levels = _cluster_dimension(gacha_values)

    # 清空旧数据
    PlayerClusterProfile.objects.all().delete()

    rows = []

    for i, player in enumerate(players):

        row = PlayerClusterProfile(
            player=player,

            spender_score=spender_values[i],
            skill_score=skill_values[i],
            activity_score=activity_values[i],
            gacha_score=gacha_values[i],

            spender_level=spender_levels[i],
            skill_level=skill_levels[i],
            activity_level=activity_levels[i],
            gacha_level=gacha_levels[i],

            spender_tag=LEVEL_NAME_MAP[spender_levels[i]],
            skill_tag=LEVEL_NAME_MAP[skill_levels[i]],
            activity_tag=LEVEL_NAME_MAP[activity_levels[i]],
            gacha_tag=LEVEL_NAME_MAP[gacha_levels[i]],

            update_time=timezone.now()
        )

        rows.append(row)

    PlayerClusterProfile.objects.bulk_create(rows)

    print("=== 标签聚类完成 ===")