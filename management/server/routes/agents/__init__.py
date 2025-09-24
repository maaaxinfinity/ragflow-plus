from flask import Blueprint

agent_bp = Blueprint("agents", __name__, url_prefix="/api/v1/agents")

from . import routes