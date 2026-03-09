import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score


def auto_dbscan_1d(values):
    """
    对一个维度进行自动 DBSCAN
    目标：尽量得到 3 类
    """

    X = np.array(values).reshape(-1, 1)

    best_labels = None
    best_score = -1
    best_eps = None

    for eps in np.linspace(0.05, 0.5, 15):
        db = DBSCAN(eps=eps, min_samples=5)
        labels = db.fit_predict(X)

        # 至少2类
        if len(set(labels)) <= 1:
            continue

        try:
            score = silhouette_score(X, labels)
        except:
            continue

        if score > best_score:
            best_score = score
            best_labels = labels
            best_eps = eps

    if best_labels is None:
        return np.zeros(len(values)), None

    return best_labels, best_eps


def label_levels(values, labels):
    """
    将 cluster id 映射成 低/中/高
    """

    cluster_means = {}
    for cid in set(labels):
        cluster_means[cid] = np.mean(
            [v for v, l in zip(values, labels) if l == cid]
        )

    # 按均值排序
    sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1])

    level_map = {}
    level_names = ["low", "medium", "high"]

    for i, (cid, _) in enumerate(sorted_clusters):
        if i < 3:
            level_map[cid] = level_names[i]
        else:
            level_map[cid] = "high"

    return level_map