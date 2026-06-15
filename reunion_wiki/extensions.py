from flask_limiter import Limiter
from flask_wtf.csrf import CSRFProtect

from .utils import get_client_ip

csrf = CSRFProtect()
limiter = Limiter(key_func=get_client_ip)