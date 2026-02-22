from django.core.management import call_command
from analysis.models import SystemTaskSwitch


def run_scheduled_tasks():
    tasks = SystemTaskSwitch.objects.filter(enabled=True)

    for task in tasks:
        if task.task_name == "build_feature":
            call_command("build_feature")

        elif task.task_name == "run_tags":
            call_command("run_tags")