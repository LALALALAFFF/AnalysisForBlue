#from analysis.models import TagCategory, Tag, PlayerTagMapping


from analysis.models import (
    TagCategory,
    Tag,
    PlayerTagMapping,
    PlayerFeatureVector,
)


def run_assign_tags():
    """
    为所有拥有特征向量的玩家打标签
    """
    # 取所有玩家特征向量
    feature_vectors = PlayerFeatureVector.objects.select_related("player")

    for fv in feature_vectors:
        player_id = fv.player_id
        feature_vector = fv.behavior_vector or {}

        for category in TagCategory.objects.all():
            value = feature_vector.get(category.code)
            if value is None:
                continue

            tag = (
                Tag.objects
                .filter(category=category)
                .filter(min_value__lte=value, max_value__gt=value)
                .first()
            )

            if not tag:
                continue

            PlayerTagMapping.objects.update_or_create(
                player_id=player_id,
                category=category,
                defaults={"tag": tag}
            )