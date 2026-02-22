from django.db import models

# Create your models here.
from django.db import models


class PlayerBasic(models.Model):
    uid = models.IntegerField(unique=True, db_index=True)   # ✅ 新增（核心）
    username = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, blank=True)
    age = models.IntegerField(null=True, blank=True)
    region = models.CharField(max_length=50, blank=True)
    register_time = models.DateTimeField()
    last_login = models.DateTimeField()

    def __str__(self):
        return f"{self.uid}-{self.username}"


class PlayerEvent(models.Model):
    player = models.ForeignKey(PlayerBasic, on_delete=models.CASCADE)
    uid = models.IntegerField(db_index=True)
    event_type = models.CharField(max_length=50)
    event_time = models.DateTimeField()
    payload = models.JSONField()  # ✅ JSON 而不是 Text

    def __str__(self):
        return f"{self.uid}-{self.event_type}"


class PlayerClickEvent(models.Model):
    player = models.ForeignKey(PlayerBasic, on_delete=models.CASCADE)
    button = models.CharField(max_length=50)
    info = models.TextField()
    click_time = models.DateTimeField()


class PlayerBattleEvent(models.Model):
    player = models.ForeignKey(PlayerBasic, on_delete=models.CASCADE)
    uid = models.IntegerField(db_index=True)

    battle_type = models.CharField(max_length=50)
    result = models.CharField(max_length=20)     # success / fail
    duration = models.IntegerField()             # seconds
    score = models.IntegerField(null=True, blank=True)
    stars = models.IntegerField(null=True, blank=True)

    event_time = models.DateTimeField()


class PlayerPurchase(models.Model):
    player = models.ForeignKey(PlayerBasic, on_delete=models.CASCADE)
    uid = models.IntegerField(db_index=True)

    amount = models.FloatField()
    currency = models.CharField(max_length=20)
    item = models.CharField(max_length=100, blank=True)
    purchase_time = models.DateTimeField()


class EventErrorLog(models.Model):
    player = models.ForeignKey(PlayerBasic, on_delete=models.CASCADE, null=True)
    event_type = models.CharField(max_length=50)
    raw_data = models.TextField()
    error_message = models.TextField()
    error_time = models.DateTimeField()


class EventQueue(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
    ]

    player = models.ForeignKey(PlayerBasic, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    raw_data = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    enqueue_time = models.DateTimeField()
    update_time = models.DateTimeField()

class ActionLog(models.Model):
    uid = models.IntegerField(db_index=True)
    session_id = models.IntegerField(db_index=True)

    event_type = models.CharField(max_length=50)
    payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uid}-{self.event_type}"