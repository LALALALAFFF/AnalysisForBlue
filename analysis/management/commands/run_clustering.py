# analysis/management/commands/run_clustering.py

from django.core.management.base import BaseCommand
from django.utils import timezone

from analysis.clustering import run_player_clustering
from analysis.utils import build_feature_vector
from analysis.models import (
    PlayerClusterResult,
    PlayerTag,
    PlayerTagMapping
)

# ======================
# 玩家画像规则
# ======================
def assign_tag(feature):
    (
        play_time,
        active_days,
        login_count,
        battle_count,
        win_rate,
        total_consume,
        avg_order_value,
        battle_ratio,
        gacha_ratio,
        purchase_ratio,
        explore_ratio,
    ) = feature

    if total_consume > 500:
        return "高付费玩家"

    if battle_count > 100 and win_rate > 0.55:
        return "PVP 重度玩家"

    if gacha_ratio > 0.4:
        return "抽卡偏好玩家"

    if play_time > 100 and login_count > 20:
        return "高活跃玩家"

    if play_time < 20:
        return "低活跃玩家"

    return "普通玩家"


class Command(BaseCommand):
    help = "Run KMeans clustering and generate player personas"

    def handle(self, *args, **kwargs):

        pfv_list, labels = run_player_clustering(n_clusters=3)

        if not pfv_list:
            self.stdout.write(self.style.ERROR("No PlayerFeatureVector found."))
            return

        for pfv, cluster_id in zip(pfv_list, labels):
            player = pfv.player
            feature = build_feature_vector(pfv)

            tag_name = assign_tag(feature)

            # ---- 创建 / 获取标签 ----
            tag_obj, _ = PlayerTag.objects.get_or_create(
                tag_name=tag_name,
                defaults={
                    "tag_type": "cluster_rule",
                    "description": f"Auto generated tag: {tag_name}",
                    "create_time": timezone.now(),
                }
            )

            # ---- 保存聚类结果 ----
            PlayerClusterResult.objects.update_or_create(
                player=player,
                algorithm="KMeans",
                model_version="v1",
                defaults={
                    "cluster_id": int(cluster_id),
                    "score_vector": feature,
                    "update_time": timezone.now(),
                    "player_tag": tag_name,
                }
            )

            # ---- 建立标签映射 ----
            PlayerTagMapping.objects.update_or_create(
                player=player,
                tag=tag_obj,
                defaults={
                    "source": "kmeans+rule",
                    "assign_time": timezone.now(),
                }
            )

        self.stdout.write(
            self.style.SUCCESS("✔ Player clustering & persona analysis finished.")
        )
