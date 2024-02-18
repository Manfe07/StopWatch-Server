from flask import Blueprint

teams_Blueprint = Blueprint('teams', __name__,  template_folder='templates')

from . import routes, models