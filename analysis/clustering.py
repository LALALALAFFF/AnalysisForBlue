import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from django.utils import timezone

from analysis.models import PlayerFeatureVector, PlayerClusterResult


# ✅ 去掉 login / logout
BEHAVIOR_KEYS = [
    "explore",
    "gacha",
    "purchase",
    "daily_task",
    "event_task",
    "material_farm",
]


def run_dbscan_clustering(
    eps=0.35,
    min_samples=3,
    model_version="dbscan_behavior_v2"
):
    """
    基于行为占比 behavior_vector 的 DBSCAN 聚类
    （不包含 login / logout）
    """

    feature_vectors = []
    players = []

    qs = PlayerFeatureVector.objects.select_related("player")

    if not qs.exists():
        print("[DBSCAN] No PlayerFeatureVector found")
        return

    # 1️⃣ 构造行为向量
    for fv in qs:
        bv = fv.behavior_vector or {}

        vec = [
            float(bv.get(key, 0.0))
            for key in BEHAVIOR_KEYS
        ]

        feature_vectors.append(vec)
        players.append(fv.player)

    X = np.array(feature_vectors)

    # 2️⃣ 标准化（必须）
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3️⃣ DBSCAN
    dbscan = DBSCAN(
        eps=eps,
        min_samples=min_samples,
        metric="euclidean"
    )

    labels = dbscan.fit_predict(X_scaled)

    # 4️⃣ 清理旧结果
    PlayerClusterResult.objects.filter(
        algorithm="dbscan",
        model_version=model_version
    ).delete()

    # 5️⃣ 写入新结果
    results = []
    for player, label, vec in zip(players, labels, feature_vectors):
        results.append(
            PlayerClusterResult(
                player=player,
                cluster_id=int(label),   # -1 = 噪声
                algorithm="dbscan",
                model_version=model_version,
                score_vector=dict(zip(BEHIOR_KEYS := BEHAVIOR_KEYS, vec)),
                update_time=timezone.now()
            )
        )

    PlayerClusterResult.objects.bulk_create(results)

    # 6️⃣ 打印聚类摘要
    clusters = set(labels)
    print(f"[DBSCAN] clusters = {clusters}")
    for cid in sorted(clusters):
        count = sum(1 for l in labels if l == cid)
        print(f"  Cluster {cid}: {count} players")
