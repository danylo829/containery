from flask import Blueprint
from flask_assets import Bundle

module_name = __name__.split('.')[-1]
container = Blueprint(module_name, __name__, template_folder='templates', static_folder='static')

from .api import api
container.register_blueprint(api, url_prefix='/api')

@container.context_processor
def inject_variables():
    return dict(active_page=module_name)

def register_assets(assets):
    actions_js = Bundle(
        "js/container_actions.js",
        "js/container_list_actions.js",
        "js/container_list_settings.js",
        filters='rjsmin',
        output=f"dist/js/{module_name}_actions.%(version)s.js",
    )
    logs_js = Bundle(
        "js/logs.js",
        filters='rjsmin',
        output=f"dist/js/{module_name}_logs.%(version)s.js",
    )
    terminal_js = Bundle(
        "js/terminal.js",
        filters='rjsmin',
        output=f"dist/js/{module_name}_terminal.%(version)s.js",
    )

    terminal_css = Bundle(
        "styles/terminal.css",
        filters='rcssmin',
        output=f"dist/css/{module_name}_terminal.%(version)s.css",
    )

    logs_css = Bundle(
        "styles/logs.css",
        filters='rcssmin',
        output=f"dist/css/{module_name}_logs.%(version)s.css",
    )

    list_css = Bundle(
        "styles/container_list.css",
        filters='rcssmin',
        output=f"dist/css/{module_name}_list.%(version)s.css",
    )

    assets.register(f"{module_name}_actions_js", actions_js)
    assets.register(f"{module_name}_logs_js", logs_js)
    assets.register(f"{module_name}_logs_css", logs_css)
    assets.register(f"{module_name}_terminal_js", terminal_js)
    assets.register(f"{module_name}_terminal_css", terminal_css)
    assets.register(f"{module_name}_list_css", list_css)

from . import routes