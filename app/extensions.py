from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)  # creating an instance of Limiter

ma = Marshmallow()  # Instantiate Marshmallow for serialization
