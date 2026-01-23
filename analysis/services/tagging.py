import json
from datetime import datetime
from django.utils import timezone

from analysis.models import (
    PlayerFeatureVector,
    PlayerTag,
    PlayerTagMapping,
    PlayerBasic
)


# ========== 帮助函数：确保标签存在 ==========
def get_or_create_tag(name, tag_type="behavior", desc=""):
    tag, created = PlayerTag.objects.get_or_create(
        tag_name=name,
        defaults={
            "tag_type": tag_type,
            "description": desc,
            "create_time": timezone.now(),
        }
    )
    return tag


# ========== 标签逻辑 ==========
def generate_tags_from_vector(fv: PlayerFeatureVector):
    tags = []

    bv = fv.behavior_vector or {}

    gacha = bv.get("gacha", 0)
    explore = bv.get("explore", 0)
    purchase = bv.get("purchase", 0)
    material = bv.get("material_farm", 0)
    daily = bv.get("daily_task", 0)
    event = bv.get("event_task", 0)

    # 行为规则
    if gacha > 0.2:
        tags.append("重抽卡玩家")
    if purchase > 0.1:
        tags.append("氪金玩家")
    if material > 0.4:
        tags.append("刷材料玩家")
    if explore > 0.2:
        tags.append("探索玩家")
    if (daily + event) > 0.4:
        tags.append("高活跃玩家")

    # 技巧
    if fv.win_rate > 0.6:
        tags.append("高技巧玩家")
    elif fv.win_rate < 0.3:
        tags.append("低技巧玩家")

    # 消费
    if fv.total_consume == 0:
        tags.append("0氪玩家")
    elif fv.total_consume > 2000:
        tags.append("重氪玩家")

    return tags


# ========== 核心入口 ==========
def run_assign_tags():
    print("=== 加载玩家特征向量 ===")
    all_fv = PlayerFeatureVector.objects.select_related("player").all()

    print(f"共 {all_fv.count()} 个玩家")

    for fv in all_fv:
        player = fv.player
        uid = player.uid  # 仅用于打印（不保存）

        tags = generate_tags_from_vector(fv)

        print(f"\n玩家 UID {uid} → 标签：{tags}")

        for tag_name in tags:
            tag_obj = get_or_create_tag(tag_name)

            # ★★★ 修复点：不再使用 uid，只用 player + tag 判断重复 ★★★
            exists = PlayerTagMapping.objects.filter(
                player=player,
                tag=tag_obj
            ).exists()

            if exists:
                continue

            PlayerTagMapping.objects.create(
                player=player,
                tag=tag_obj,
                source="feature_vector",
                assign_time=timezone.now()
            )

    print("\n=== 标签分配完毕 ===")
