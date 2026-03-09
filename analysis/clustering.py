import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from django.utils import timezone

from analysis.models import PlayerFeatureVector, PlayerClusterResult


BEHAVIOR_KEYS = [
    "explore",
    "gacha",
    "purchase",
    "daily_task",
    "event_task",
    "material_farm",
]


TARGET_CLUSTER_COUNT = 6


def assign_cluster_label(vectors):
    if not vectors:
        return "unknown"

    arr = np.array(vectors)
    mean_vec = arr.mean(axis=0)

    sorted_idx = np.argsort(mean_vec)[::-1]
    top1 = BEHAVIOR_KEYS[sorted_idx[0]]
    top2 = BEHAVIOR_KEYS[sorted_idx[1]]

    if mean_vec[sorted_idx[0]] > 0.45:
        return f"{top1}-heavy"

    return f"{top1}/{top2} mix"


def run_dbscan_auto(
    eps_min=0.15,
    eps_max=0.80,
    eps_step=0.02,
    min_samples=3,
    model_version="dbscan_auto_v1"
):
    print("\n=== [1] 加载玩家行为向量 ===")

    qs = PlayerFeatureVector.objects.select_related("player")

    if not qs.exists():
        print("没有 PlayerFeatureVector 数据")
        return

    players = []
    feature_vectors = []

    for fv in qs:
        bv = fv.behavior_vector or {}
        vec = [float(bv.get(k, 0.0)) for k in BEHAVIOR_KEYS]

        players.append(fv.player)
        feature_vectors.append(vec)

    X = np.array(feature_vectors)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("\n=== [2] 自动搜索 eps ===")

    best_eps = None
    best_labels = None
    best_diff = 999

    eps = eps_min
    while eps <= eps_max:
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X_scaled)

        # 排除噪声 -1
        cluster_ids = set(labels)
        cluster_ids.discard(-1)
        cluster_count = len(cluster_ids)

        diff = abs(cluster_count - TARGET_CLUSTER_COUNT)

        print(f"eps={eps:.2f} -> clusters={cluster_count}")

        if cluster_count > 0 and diff < best_diff:
            best_diff = diff
            best_eps = eps
            best_labels = labels

        eps += eps_step

    if best_labels is None:
        print("未找到合适的 eps")
        return

    cluster_ids = set(best_labels)
    cluster_ids.discard(-1)
    real_cluster_count = len(cluster_ids)

    print(f"\n✅ 最佳 eps = {best_eps:.2f}")
    print(f"真实生成簇数量 = {real_cluster_count}")
    #print(f"\n✅ 最佳 eps = {best_eps:.2f}")
    #print(f"生成簇数量 = {TARGET_CLUSTER_COUNT - best_diff}")

    # 删除旧数据
    PlayerClusterResult.objects.filter(
        algorithm="dbscan",
        model_version=model_version
    ).delete()

    # 收集簇数据
    cluster_vectors = {}
    for player, label, vec in zip(players, best_labels, feature_vectors):
        cluster_vectors.setdefault(label, []).append(vec)

    cluster_label_map = {
        cid: assign_cluster_label(vecs)
        for cid, vecs in cluster_vectors.items()
        if cid != -1
    }

    # 写入数据库
    rows = []
    for player, label, vec in zip(players, best_labels, feature_vectors):
        rows.append(
            PlayerClusterResult(
                player=player,
                cluster_id=int(label),
                algorithm="dbscan",
                model_version=model_version,
                score_vector=dict(zip(BEHAVIOR_KEYS, vec)),
                cluster_label=cluster_label_map.get(label, "noise"),
                update_time=timezone.now()
            )
        )

    PlayerClusterResult.objects.bulk_create(rows)

    print("聚类完成！")
    print("簇标签：")
    for cid, lab in cluster_label_map.items():
        print(f"Cluster {cid}: {lab}")

    print("\n=== DBSCAN 自动完成 ===\n")