import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from django.utils import timezone

from analysis.models import PlayerFeatureVector, PlayerClusterResult
from collections import Counter
from itertools import combinations


# ------------------------------------------------------------
# 配置：行为字段（不包含 login/logout）
# ------------------------------------------------------------
BEHAVIOR_KEYS = [
    "explore",
    "gacha",
    "purchase",
    "daily_task",
    "event_task",
    "material_farm",
]


# ------------------------------------------------------------
# Apriori（从行为向量中生成 0/1 特征）
# ------------------------------------------------------------
def apriori(transactions, min_support=0.2):
    """
    传入 transactions: List[List[str]]，每个玩家的行为列表
    行为存在则加入列表，如 ["battle","gacha"]
    """

    total = len(transactions)
    support_count = Counter()

    # 1-itemset
    for t in transactions:
        for item in t:
            support_count[frozenset([item])] += 1

    # 过滤
    freq_sets = {
        item: cnt / total
        for item, cnt in support_count.items()
        if cnt / total >= min_support
    }

    results = dict(freq_sets)

    # 继续组合（2、3...）
    k = 2
    current_sets = list(freq_sets.keys())

    while current_sets:
        candidate = []
        length = len(current_sets)

        # 两两合并
        for i in range(length):
            for j in range(i + 1, length):
                c = current_sets[i] | current_sets[j]
                if len(c) == k and c not in candidate:
                    candidate.append(c)

        support_count = Counter()
        for t in transactions:
            t_set = set(t)
            for c in candidate:
                if c.issubset(t_set):
                    support_count[c] += 1

        freq_k = {
            c: cnt / total
            for c, cnt in support_count.items()
            if cnt / total >= min_support
        }

        if not freq_k:
            break

        results.update(freq_k)
        current_sets = list(freq_k.keys())
        k += 1

    return results


def generate_association_rules(freq_itemsets, min_conf=0.5):
    """
    根据频繁项集生成关联规则
    """
    rules = []

    for itemset, support in freq_itemsets.items():
        if len(itemset) < 2:
            continue

        items = list(itemset)

        for i in range(1, len(items)):
            for A in combinations(items, i):
                A = frozenset(A)
                B = itemset - A
                conf = freq_itemsets[itemset] / freq_itemsets.get(A, 1e-8)

                if conf >= min_conf:
                    rules.append({
                        "A": list(A),
                        "B": list(B),
                        "support": support,
                        "confidence": conf,
                    })

    return rules


# ------------------------------------------------------------
# 自动标签：找出每一类最突出的行为
# ------------------------------------------------------------
def assign_cluster_label(vectors):
    """
    vectors: List[List[float]]，同一簇的行为向量
    返回标签，如 "gacha-heavy" or "explore/daily_task mix"
    """

    if not vectors:
        return "unknown"

    arr = np.array(vectors)
    mean_vec = arr.mean(axis=0)

    # 找 top2 行为
    sorted_idx = np.argsort(mean_vec)[::-1]
    top1 = BEHAVIOR_KEYS[sorted_idx[0]]
    top2 = BEHAVIOR_KEYS[sorted_idx[1]]

    # 强势行为
    if mean_vec[sorted_idx[0]] > 0.45:
        return f"{top1}-heavy"

    # 混合行为
    return f"{top1}/{top2} mix"


# ------------------------------------------------------------
# DBSCAN 主流程（包含标签 + Apriori）
# ------------------------------------------------------------
def run_dbscan_all(
    eps=0.35,
    min_samples=3,
    model_version="dbscan_behavior_v3",
    run_apriori_analysis=True
):
    """
    三合一：
    1. DBSCAN 聚类
    2. 自动标签
    3. Apriori 关联分析
    """

    print("\n=== [1] 加载行为向量 ===")
    qs = PlayerFeatureVector.objects.select_related("player")

    if not qs.exists():
        print("没有 PlayerFeatureVector 数据")
        return

    players = []
    feature_vectors = []
    transactions = []  # 用于 Apriori

    for fv in qs:
        bv = fv.behavior_vector or {}

        vec = [float(bv.get(k, 0.0)) for k in BEHAVIOR_KEYS]

        players.append(fv.player)
        feature_vectors.append(vec)

        # 转为 0/1 行为，用于 Apriori
        acts = [k for k in BEHAVIOR_KEYS if bv.get(k, 0) > 0.05]
        transactions.append(acts)

    X = np.array(feature_vectors)

    # -----------------------
    # 标准化
    # -----------------------
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # -----------------------
    # DBSCAN 聚类
    # -----------------------
    print("\n=== [2] DBSCAN 聚类运行中 ===")
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)

    # 清旧记录
    PlayerClusterResult.objects.filter(
        algorithm="dbscan",
        model_version=model_version
    ).delete()

    # 聚类标签缓存
    cluster_vectors = {}

    for player, label, vec in zip(players, labels, feature_vectors):
        cluster_vectors.setdefault(label, []).append(vec)

    # 生成标签
    cluster_label_map = {
        cid: assign_cluster_label(vecs)
        for cid, vecs in cluster_vectors.items()
    }

    # 写入数据库
    print("\n=== [3] 写入聚类结果 ===")
    rows = []
    for player, label, vec in zip(players, labels, feature_vectors):
        rows.append(
            PlayerClusterResult(
                player=player,
                cluster_id=int(label),
                algorithm="dbscan",
                model_version=model_version,
                score_vector=dict(zip(BEHAVIOR_KEYS, vec)),
                cluster_label=cluster_label_map.get(label, "unknown"),
                update_time=timezone.now()
            )
        )
    PlayerClusterResult.objects.bulk_create(rows)

    print("聚类完成！")
    print("簇标签：")
    for cid, lab in cluster_label_map.items():
        print(f"  Cluster {cid}: {lab}")

    # -----------------------
    # Apriori
    # -----------------------
    if run_apriori_analysis:
        print("\n=== [4] Apriori 行为关联分析 ===")
        freq_sets = apriori(transactions, min_support=0.2)
        rules = generate_association_rules(freq_sets, min_conf=0.5)

        print("\n频繁项集：")
        for k, v in freq_sets.items():
            print(f"  {list(k)} : support={v:.2f}")

        print("\n关联规则：")
        for r in rules:
            print(f"  {r['A']} => {r['B']} | conf={r['confidence']:.2f} support={r['support']:.2f}")

    print("\n=== 运行结束 ===\n")
