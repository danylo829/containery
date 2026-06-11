from flask import redirect, url_for, session, render_template
from flask_login import login_required

from app.modules.user.models import User
from app.config import Config

from . import index

@index.route('/', methods=['GET'])
def root():
    if User.query.first():
        return redirect(url_for('auth.login'))
    return redirect(url_for('auth.install'))

@index.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

@index.route('/toggle-sidebar', methods=['POST'])
@login_required
def toggle_sidebar():
    if session.get('sidebar_state') == 'closed':
        session['sidebar_state'] = 'open'
    else:
        session['sidebar_state'] = 'closed'
    
    return {'sidebar_state': session['sidebar_state']}, 200

@index.route('/about', methods=['GET'])
@login_required
def about():
    page_title = "About"
    return render_template('about.html', page_title=page_title, version=Config.VERSION)