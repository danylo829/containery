from flask import Flask

from sys import argv
from os import path, listdir, walk
from shutil import copytree, rmtree
from importlib import import_module
from datetime import timedelta

from flask_assets import Bundle
from werkzeug.debug import DebuggedApplication

import app.lib.common as common
import app.core.extensions as extensions
import app.core.error_handlers as error_handlers

from app.modules.user.models import Permissions, User, PersonalSettings
from app.modules.settings.models import GlobalSettings, DockerHost

class ApplicationFactory:
    def __init__(self):
        self.db = extensions.db
        self.csrf = extensions.csrf
        self.login_manager = extensions.login_manager
        self.socketio = extensions.socketio
        self.migrate = extensions.migrate
        self.assets = extensions.assets

    def configure_extensions(self, app):
        """Configure Flask extensions."""
        self.db.init_app(app)
        self.migrate.init_app(app, self.db, render_as_batch=True)
        self.socketio.init_app(app)
        self.csrf.init_app(app)

        self.assets.init_app(app)

        self.login_manager.init_app(app)
        self.login_manager.login_view = 'auth.login'

    def register_blueprints(self, app):
        """
        Register blueprints from app.modules where each module has a blueprint named after its folder.
        Add each module's static folder (recursively) to assets.load_path.
        """
        modules_path = path.join(app.root_path, 'modules')
        # Start with the main static folder
        load_paths = [path.join(app.root_path, 'static')]

        # Recursively find all static folders in modules
        for root, dirs, files in walk(modules_path):
            if 'static' in dirs:
                static_path = path.join(root, 'static')
                load_paths.append(static_path)

        for module_name in listdir(modules_path):
            module_dir = path.join(modules_path, module_name)
            init_file = path.join(module_dir, '__init__.py')

            if not path.isdir(module_dir) or not path.isfile(init_file):
                continue

            try:
                module_path = f'app.modules.{module_name}'
                module = import_module(module_path)

                blueprint = getattr(module, module_name)
                app.register_blueprint(blueprint)
                if hasattr(module, "register_assets"):
                    module.register_assets(self.assets)
                print(f"✔ Registered module: {module_name}")

            except (ImportError, AttributeError) as e:
                print(f"✘ Failed to load module '{module_name}': {e}")
                exit(1)

        # Set the assets load_path after collecting all static folders
        with app.app_context():
            self.assets.load_path = load_paths

    def configure_base_assets(self, app):
        """Configure and register asset bundles."""
        app_css = Bundle(
            "styles/common.css",
            "styles/colors.css",
            "styles/base.css",
            "styles/inputs.css",
            "styles/spinner.css",
            "styles/sidebar.css",
            "styles/modal.css",
            "styles/flash.css",
            "styles/icons.css",
            "styles/animations.css",
            "styles/mobile.css",
            filters="rcssmin",
            output="dist/css/app.%(version)s.css"
        )

        app_js = Bundle(
            "js/base.js",
            "js/flash.js",
            "js/sidebar.js",
            "js/modal.js",
            "js/table.js",
            "js/scrollbar.js",
            filters='rjsmin',
            output="dist/js/app.%(version)s.js",
        )

        self.assets.register("app_css", app_css)
        self.assets.register("app_js", app_js)

        print("Copying lib static files...")
        src = path.join(app.static_folder, "lib")
        dst = path.join(app.static_folder, "dist", "lib")
        if path.exists(dst):
            rmtree(dst)
        if path.exists(src):
            copytree(src, dst)
        else:
            print(f"Source directory '{src}' does not exist. Skipping copy.")

    def configure_context_processors(self, app):
        """Add context processors to the application."""
        
        @app.context_processor
        def inject_context():
            return dict(
                PersonalSettings=PersonalSettings, 
                GlobalSettings=GlobalSettings, 
                Permissions=Permissions, 
                common=common
            )
        
    def configure_error_pages(self, app):
        app.register_error_handler(404, error_handlers.page_not_found)
        app.register_error_handler(500, error_handlers.internal_server_error)
        app.register_error_handler(400, error_handlers.bad_request)

    def configure_user_loader(self):
        """Configure the user loader for Flask-Login."""

        @self.login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    def configure_session_timeout(self, app):
        """Configure session timeout based on global settings."""

        @app.before_request
        def set_dynamic_session_timeout():
            try:
                timeout = int(GlobalSettings.get_setting('session_timeout'))
            except Exception:
                timeout = 1800  # fallback default
            app.permanent_session_lifetime = timedelta(seconds=timeout)

    def migrations(self, app):
        with app.app_context():
            try:
                print("Migrating personal settings...")
                PersonalSettings.migrate()
                print("Migrating docker hosts...")
                DockerHost.migrate(app.config['DOCKER_SOCKET_PATH'])
            except Exception as e:
                print(f"Migration failed: {e}")

    def create_app(self):
        """
        Create and configure the Flask application.
        
        :return: Configured Flask application
        """
        app = Flask(__name__)
        app.config.from_object('app.config.Config')

        self.configure_extensions(app)            

        # Check if the application is running in a CLI context
        # Prevents entaire app building in entrypoint or cli
        entry = argv[0].lower()
        cli_commands = ['flask', 'cli']
        if not any(x in entry for x in cli_commands):
            self.migrations(app)
            self.configure_base_assets(app)
            self.configure_context_processors(app)
            self.configure_error_pages(app)
            self.configure_user_loader()
            self.configure_session_timeout(app)
            self.register_blueprints(app)

        if app.debug:
            app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
        
        return app