from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.db.models import Count
from analysis.models import (
    PlayerClusterResult,
    PlayerFeatureVector,
    PlayerTagMapping,
    PlayerTag, TagCategory,
)
from django.core.management import call_command
from analysis.models import SystemTaskSwitch
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from analysis.models import PlayerBasic
from analysis.tasks import save_event_async
from analysis.models import PlayerClusterProfile
# ==============================
# 接收模拟平台事件（核心接口）
# ==============================




logger = logging.getLogger(__name__)


@csrf_exempt
def receive_event(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        logger.exception("JSON parse failed")
        return JsonResponse({"error": "invalid json"}, status=400)

    # 必填字段校验（保持你原字段）
    required_fields = ["uid", "session_id", "event_type", "payload", "created_at"]
    for f in required_fields:
        if f not in data:
            return JsonResponse({"error": f"missing {f}"}, status=400)

    # created_at 兜底
    created_at = None
    if data.get("created_at"):
        created_at = parse_datetime(data["created_at"])
    if created_at is None:
        created_at = timezone.now()

    # 确保玩家存在（同步做）
    PlayerBasic.objects.get_or_create(
        uid=int(data["uid"]),
        defaults={
            "username": f"user_{data['uid']}",
            "register_time": created_at,
            "last_login": created_at,
        }
    )

    # ✅ 入队（不要写 ActionLog）
    save_event_async.delay({
        "uid": int(data["uid"]),
        "session_id": int(data["session_id"]),
        "event_type": str(data["event_type"]),
        "payload": data.get("payload", {}),
        "created_at": created_at.isoformat(),
    })

    return JsonResponse({"status": "ok"})


# ==============================
# 聚类结果接口
# ==============================
@api_view(["GET"])
def get_cluster_results(request):
    """
    返回玩家聚类 + 标签信息
    """
    results = []

    all_results = PlayerClusterResult.objects.all()

    for r in all_results:
        tag_map = (
            PlayerTagMapping.objects
            .filter(player_id=r.player_id)
            .order_by("-assign_time")
            .first()
        )
        tag_name = tag_map.tag.tag_name if tag_map else "未打标签"

        results.append({
            "player_id": r.player_id,
            "cluster_id": r.cluster_id,
            "player_tag": tag_name,
            "score_vector": r.score_vector,
        })

    return Response(results)


# ==============================
# 聚类分布
# ==============================
def cluster_distribution(request):
    data = (
        PlayerClusterResult.objects
        .values("cluster_id")
        .annotate(cluster_count=Count("cluster_id"))
    )

    count = {str(item["cluster_id"]): item["cluster_count"] for item in data}

    print("DEBUG cluster_distribution:", count)

    return JsonResponse({
        "status": "success",
        "cluster_distribution": count,
    })


# ==============================
# 玩家画像
# ==============================
def player_profile(request, player_id):
    cluster = PlayerClusterResult.objects.filter(player_id=player_id).first()
    feature = PlayerFeatureVector.objects.get(player_id=player_id)

    return JsonResponse({
        "player_id": feature.player_id,
        "cluster_id": cluster.cluster_id if cluster else None,
        "player_tag": cluster.player_tag if cluster else "未打标签",
        "total_play_time": feature.total_play_time,
        "login_frequency": feature.login_frequency,
        "consume_amount": feature.consume_amount,
        "battle_count": feature.battle_count,
        "win_rate": feature.win_rate,
        "social_interaction": feature.social_interaction,
    })


# ==============================
# DRF 形式的聚类结果
# ==============================
class ClusterResultView(APIView):
    def get(self, request):
        results = PlayerClusterResult.objects.all()
        data = []

        for r in results:
            data.append({
                "player_id": r.player_id,
                "cluster_id": r.cluster_id,
                "player_tag": r.player_tag,
                "score_vector": json.loads(r.score_vector),
            })

        return Response(data)

from rest_framework.views import APIView
from rest_framework.response import Response
from analysis.apriori import apriori


class AprioriAnalysis(APIView):
    """
    POST /analysis/apriori
    """
    def post(self, request):
        transactions = request.data.get("transactions", [])
        min_support = request.data.get("min_support", 0.2)
        min_confidence = request.data.get("min_confidence", 0.5)

        result = apriori(transactions, min_support, min_confidence)
        return Response(result)


# 1) 标签分布
LEVEL_MAP_CN = {
    "low": "低活跃",
    "medium": "中活跃",
    "high": "高活跃"
}


def tag_distribution(request):

    dimensions = {
        "消费等级": "spender_tag",
        "活跃等级": "activity_tag",
        "抽卡等级": "gacha_tag",
        "任务等级": "skill_tag",
    }

    result = []

    for name, field in dimensions.items():

        data = (
            PlayerClusterProfile.objects
            .values(field)
            .annotate(count=Count("id"))
        )

        chart_data = []

        for item in data:
            level = item[field]
            cn_label = LEVEL_MAP_CN.get(level, level)

            chart_data.append({
                "name": cn_label,
                "value": item["count"]
            })

        result.append({
            "category": name,
            "code": field,
            "data": chart_data
        })

    return JsonResponse({"data": result})


# 2) 玩家个人标签
LEVEL_MAP_CN = {
    "low": "低",
    "medium": "中",
    "high": "高"
}


def player_tags(request, player_id):

    profile = PlayerClusterProfile.objects.filter(player_id=player_id).first()

    if not profile:
        return JsonResponse({"tags": {}})

    data = {
        "消费能力": LEVEL_MAP_CN.get(profile.spender_tag, ""),
        "活跃程度": LEVEL_MAP_CN.get(profile.activity_tag, ""),
        "抽卡偏好": LEVEL_MAP_CN.get(profile.gacha_tag, ""),
        "任务投入": LEVEL_MAP_CN.get(profile.skill_tag, ""),
    }

    return JsonResponse({
        "player_id": player_id,
        "tags": data
    })
#去前端控制启动特征生成、聚类打标签接口
def run_build_feature(request):
    try:
        call_command("build_features")
        return JsonResponse({"status": 200, "msg": "特征向量生成完成"})
    except Exception as e:
        return JsonResponse({"status": 500, "error": str(e)})

def run_dimension_cluster_api(request):
    try:
        call_command("run_dbscan")
        return JsonResponse({"msg": "维度聚类完成"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def run_assign_tags(request):
    call_command("run_tags")
    return JsonResponse({"msg": "标签生成完成"})

#开关定时任务
def set_task_switch(request):

    task = request.GET.get("task")
    enabled = request.GET.get("enabled") == "true"
    interval = int(request.GET.get("interval", 1))

    obj, _ = SystemTaskSwitch.objects.update_or_create(
        task_name=task,
        defaults={
            "enabled": enabled,
            "interval_minutes": interval
        }
    )

    return JsonResponse({
        "task": obj.task_name,
        "enabled": obj.enabled,
        "interval": obj.interval_minutes
    })
