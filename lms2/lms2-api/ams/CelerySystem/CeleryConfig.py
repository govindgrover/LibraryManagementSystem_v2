from celery import Celery, Task
from flask import current_app as app

celery = Celery("API - Tasks")

class CeleryContextClass(Celery, Task):
    def __call__(self, *arg, **kwargs):
        with app.app_context():
            return self.run(*arg, **kwargs)

