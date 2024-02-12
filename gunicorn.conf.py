import multiprocessing
import os

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
wsgi_app = "exchange_rates.main:app"
workers = os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)  # noqa : PLW1508
worker_class = "uvicorn.workers.UvicornWorker"
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
