from django.urls import path
from .views import cluster_distribution, player_profile, ClusterResultView, get_cluster_results, receive_event

urlpatterns = [
    path("receive_event/", receive_event),
    path('cluster/distribution', cluster_distribution),
    path('player/<int:player_id>', player_profile),
    path('results', ClusterResultView.as_view()),  # ← 新增
]