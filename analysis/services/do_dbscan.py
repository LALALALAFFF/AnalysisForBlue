from django.utils import timezone
from analysis.services.feature_normalizer import normalize_by_percentile
from analysis.services.dbscan_cluster import auto_dbscan_1d, label_levels
from analysis.models import PlayerClusterProfile
from player.models import PlayerBasic


BEHAVIOR_KEYS = [
    "explore",
    "gacha",
    "purchase",
    "daily_task",
    "event_task",
    "material_farm",
]


def run_dimension_cluster():

    print("=== 开始维度聚类 ===")

    normalized = normalize_by_percentile(p=95)

    players = PlayerBasic.objects.all()

    # 每个维度分别聚类
    dimension_labels = {}

    for dim in BEHAVIOR_KEYS:

        values = [
            normalized.get(p.id, {}).get(dim, 0)
            for p in players
        ]

        labels, eps = auto_dbscan_1d(values)

        level_map = label_levels(values, labels)

        dimension_labels[dim] = {
            "labels": labels,
            "level_map": level_map
        }

        print(f"{dim} 聚类完成 eps={eps}")

    # 写入数据库
    PlayerClusterProfile.objects.all().delete()

    for idx, player in enumerate(players):

        def get_level(dim):
            cid = dimension_labels[dim]["labels"][idx]
            level = dimension_labels[dim]["level_map"].get(cid, "low")
            return cid, level

        spender_cid, spender_tag = get_level("purchase")
        activity_cid, activity_tag = get_level("explore")
        gacha_cid, gacha_tag = get_level("gacha")
        skill_cid, skill_tag = get_level("daily_task")

        PlayerClusterProfile.objects.create(
            player=player,

            spender_score=normalized[player.id]["purchase"],
            skill_score=normalized[player.id]["daily_task"],
            activity_score=normalized[player.id]["explore"],
            gacha_score=normalized[player.id]["gacha"],

            spender_level=spender_cid,
            skill_level=skill_cid,
            activity_level=activity_cid,
            gacha_level=gacha_cid,

            spender_tag=spender_tag,
            skill_tag=skill_tag,
            activity_tag=activity_tag,
            gacha_tag=gacha_tag,
        )

    print("=== 聚类标签生成完成 ===")