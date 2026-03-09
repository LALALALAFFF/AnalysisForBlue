from django.urls import path
from .views import cluster_distribution, player_profile, ClusterResultView, get_cluster_results, receive_event, \
    run_dimension_cluster_api
from .views import tag_distribution, player_tags, run_build_feature,run_assign_tags,set_task_switch
urlpatterns = [
    path("receive_event", receive_event),
    path('cluster/distribution', cluster_distribution),
    path('player/<int:player_id>', player_profile),
    path('results', ClusterResultView.as_view()),  # ← 新增
    #path("apriori", AprioriAnalysis.as_view()),
    path("tag-distribution/", tag_distribution),
    path("player-tags/<int:player_id>/", player_tags),
    path("control/build-feature/", run_build_feature),
    path("control/run-dbscan/", run_dimension_cluster_api),
    path("control/task-switch/", set_task_switch),

]