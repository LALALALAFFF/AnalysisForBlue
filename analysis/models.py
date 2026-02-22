from django.db import models
from player.models import PlayerBasic


class PlayerFeatureVector(models.Model):
    player = models.ForeignKey(PlayerBasic, on_delete=models.CASCADE)

    # —— 时间类 ——
    total_play_time = models.FloatField()     # 秒
    active_days = models.IntegerField()

    # —— 行为计数 ——
    login_count = models.IntegerField()
    battle_count = models.IntegerField()
    win_rate = models.FloatField()

    # —— 消费 ——
    total_consume = models.FloatField()
    avg_order_value = models.FloatField()

    # —— 行为偏好（从 ActionLog / Event 推导） ——
    behavior_vector = models.JSONField()  # {"gacha":0.3,"battle":0.6}

    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"FV-{self.player.uid}"


class PlayerClusterResult(models.Model):
    player = models.ForeignKey(PlayerBasic, on_delete=models.CASCADE)
    cluster_id = models.IntegerField()
    algorithm = models.CharField(max_length=50)
    model_version = models.CharField(max_length=50)
    score_vector = models.JSONField()
    update_time = models.DateTimeField()
    player_tag = models.CharField(max_length=50, default='', blank=True)


    def __str__(self):
        return f"{self.player.username}-Cluster:{self.cluster_id}"


class PlayerTag(models.Model):
    tag_name = models.CharField(max_length=50)
    tag_type = models.CharField(max_length=50)
    description = models.TextField()
    create_time = models.DateTimeField()

    def __str__(self):
        return self.tag_name




class TagCategory(models.Model):
    """
    标签类别 = 一个行为维度
    如：daily_task、purchase
    """
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    某一维度下的具体标签
    """
    category = models.ForeignKey(
        TagCategory,
        on_delete=models.CASCADE,
        related_name="tags"
    )

    name = models.CharField(max_length=100)

    min_value = models.FloatField()
    max_value = models.FloatField()

    def match(self, value: float) -> bool:
        return self.min_value <= value < self.max_value

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class PlayerTagMapping(models.Model):
    player_id = models.IntegerField(db_index=True)
    category = models.ForeignKey(TagCategory, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("player_id", "category")

class SystemTaskSwitch(models.Model):
    task_name = models.CharField(max_length=50, unique=True)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.task_name}: {self.enabled}"

class Feature(models.Model):
    user_id = models.BigIntegerField(unique=True)
    vector = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)