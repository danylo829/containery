from flask import Blueprint
from flask_assets import Bundle

module_name = __name__.split('.')[-1]
image = Blueprint(module_name, __name__, template_folder='templates', static_folder='static')

from .api import api
image.register_blueprint(api, url_prefix='/api')

@image.context_processor
def inject_variables():
    return dict(active_page=module_name)

def register_assets(assets):
    js = Bundle(
        "js/image_actions.js",
        "js/image_list_actions.js",
        filters='rjsmin',
        output=f"dist/js/{module_name}.%(version)s.js",
    )
    assets.register(f"{module_name}_js", js)

from . import routes