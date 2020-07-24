from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

celery_app = Celery(
    "worker",
    backend="redis://:password123@redis:6379/0",
    broker="amqp://user:bitnami@rabbitmq:5672//"
)

celery_app.conf.task_routes = {
    "worker.celery_worker.test_celery": "test-queue",
    "worker.celery_worker.searhvolume_celery": "test-queue",
    "worker.celery_worker.searhvolume_get_celery": "test-queue"
    }

celery_app.conf.update(
    task_track_started=True, 
    enable_utc=True 
    # CELERY_REDIS_SCHEDULER_URL = 'redis://:password123@redis:6379/0',
    # beat_schedule={
    #     'perminute': {
    #         'task': 'worker.celery_worker.test_celery',
    #         'schedule': timedelta(seconds=3),
    #     }
    # }
)
