# analysis/clustering.py

import numpy as np
from sklearn.cluster import KMeans
from analysis.models import PlayerFeatureVector
from analysis.utils import build_feature_vector


def run_player_clustering(n_clusters=3):
    """
    返回：
    - pfv_list: PlayerFeatureVector 列表
    - labels: 聚类标签列表
    """

    qs = PlayerFeatureVector.objects.select_related("player")

    data = []
    pfv_list = []

    for pfv in qs:
        feature = build_feature_vector(pfv)
        data.append(feature)
        pfv_list.append(pfv)

    if not data:
        return [], []

    X = np.array(data)

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init="auto"
    )
    labels = model.fit_predict(X)

    return pfv_list, labels.tolist()
