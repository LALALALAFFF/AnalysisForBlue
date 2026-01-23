from analysis.models import TagCategory, Tag, PlayerTagMapping


def assign_tags_for_player(player_id: int, feature_vector: dict):
    """
    根据特征向量为玩家打标签
    """
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