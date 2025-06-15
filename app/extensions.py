from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache


ma = Marshmallow()  # Instantiate Marshmallow for serialization
limiter = Limiter(key_func=get_remote_address)  # creating an instance of Limiter
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})  # Simple in-memory cache
