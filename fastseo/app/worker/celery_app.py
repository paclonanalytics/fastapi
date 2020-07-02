from celery import Celery

celery_app = Celery(
    "worker",
    backend="redis://:password123@redis:6379/0",
    broker="amqp://user:bitnami@rabbitmq:5672//"
)

celery_app.conf.task_routes = {
    "worker.celery_worker.test_celery": "test-queue"}
celery_app.conf.update(task_track_started=True)
