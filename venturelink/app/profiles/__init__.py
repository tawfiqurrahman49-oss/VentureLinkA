from flask import Blueprint
profiles_bp = Blueprint('profiles', __name__, url_prefix='/profile')
from app.profiles import routes
