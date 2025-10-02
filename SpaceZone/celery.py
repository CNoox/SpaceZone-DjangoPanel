import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SpaceZone.settings')

app = Celery('SpaceZone')

broker_url = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
app.conf.broker_url = broker_url

app.autodiscover_tasks()