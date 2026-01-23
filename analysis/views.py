import json

from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from rest_framework.views import APIView
from analysis.models import PlayerClusterResult, PlayerFeatureVector, PlayerTag, PlayerTagMapping
from django.db.models import Count

from rest_framework.decorators import api_view
from rest_framework.response import Response


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from player.models import ActionLog


@csrf_exempt
def receive_event(request):
    if request.method != "POST":
        return JsonResponse({"error": "method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    # —— 必填字段校验（非常重要）——
    required_fields = ["uid", "session_id", "event_type", "payload", "created_at"]
    for f in required_fields:
        if f not in data:
            return JsonResponse({"error": f"missing {f}"}, status=400)

    created_at = parse_datetime(data["created_at"])
    if created_at is None:
        return JsonResponse({"error": "invalid created_at"}, status=400)

    # —— 入库 ——
    ActionLog.objects.create(
        uid=data["uid"],
        session_id=data["session_id"],
        event_type=data["event_type"],
        payload=data["payload"],
        created_at=created_at
    )

    return JsonResponse({"status": "ok"})




@api_view(["GET"])
def get_cluster_results(request):
    """
    返回玩家聚类 + 标签信息
    """
    results = []

    all_results = PlayerClusterResult.objects.all()

    for r in all_results:
        # 获取标签（如果一个玩家多个标签，取最新的那个）
        tag_map = PlayerTagMapping.objects.filter(player_id=r.player_id).order_by("-assign_time").first()
        tag_name = tag_map.tag.tag_name if tag_map else "未打标签"

        results.append({
            "player_id": r.player_id,
            "cluster_id": r.cluster_id,
            "player_tag": tag_name,
            "score_vector": r.score_vector
        })

    return Response(results)

def cluster_distribution(request):
    # 按 cluster_id 统计数量
    data = PlayerClusterResult.objects.values("cluster_id").annotate(cluster_count=Count("cluster_id"))

    # 转成字典，key 是 cluster_id，value 是数量
    count = {str(item["cluster_id"]): item["cluster_count"] for item in data}

    print("DEBUG cluster_distribution:", count)  # 调试用

    return JsonResponse({
        "status": "success",
        "cluster_distribution": count
    })

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

class ClusterResultView(APIView):
    def get(self, request):
        results = PlayerClusterResult.objects.all()
        data = []
        for r in results:
            data.append({
                'player_id': r.player_id,
                'cluster_id': r.cluster_id,
                "player_tag": r.player_tag,
                'score_vector': json.loads(r.score_vector)
            })
        return Response(data)