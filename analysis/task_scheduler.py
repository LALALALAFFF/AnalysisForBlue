"""from celery import shared_task
from django.core.management import call_command
from analysis.models import SystemTaskSwitch


@shared_task
def scheduled_analysis_runner():

    tasks = SystemTaskSwitch.objects.filter(enabled=True)

    for task in tasks:

        if task.task_name == "build_feature":
            call_command("build_features")

        if task.task_name == "run_dbscan":
            call_command("run_dbscan")"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command

from analysis.models import SystemTaskSwitch


@shared_task
def scheduled_analysis_runner():

    tasks = SystemTaskSwitch.objects.filter(enabled=True)

    for task in tasks:

        now = timezone.now()

        # 判断是否需要运行
        if not task.last_run_time:
            should_run = True
        else:
            delta = now - task.last_run_time
            should_run = delta >= timedelta(minutes=task.interval_minutes)

        if not should_run:
            continue

        # 执行任务
        if task.task_name == "build_feature":
            call_command("build_features")

        elif task.task_name == "run_dbscan":
            call_command("run_dbscan")

        # 更新最后运行时间
        task.last_run_time = now
        task.save()