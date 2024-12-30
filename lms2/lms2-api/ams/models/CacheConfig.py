from flask_caching import Cache
from flask import current_app as app

api_cache = Cache(app)
