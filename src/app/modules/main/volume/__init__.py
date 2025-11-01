from flask import Blueprint
from flask_assets import Bundle

module_name = __name__.split('.')[-1]
volume = Blueprint(module_name, __name__, template_folder='templates', static_folder='static')

from .api import api
volume.register_blueprint(api, url_prefix='/api')

@volume.context_processor
def inject_variables():
    return dict(active_page=module_name)

from . import routes

def register_assets(assets):
    js = Bundle(
        "js/volume_actions.js",
        "js/volume_list_actions.js",
        filters='rjsmin',
        output=f"dist/js/{module_name}.%(version)s.js",
    )
    assets.register(f"{module_name}_js", js)