from flask import render_template, request, redirect
from flask_login import current_user

def page_not_found(e):
    code = 404
    if current_user.is_authenticated:
        return render_template('error.html', code=code, message=e), code
    else:
        return render_template('error_unauthenticated.html', code=code, message=e), code

def internal_server_error(e):
    code = 500
    if current_user.is_authenticated:
        return render_template('error.html', code=code, message=e), code
    else:
        return render_template('error_unauthenticated.html', code=code, message=e), code

def bad_request(e):
    code = 400
    if "CSRF" in str(e):
        return redirect(request.url)
    if current_user.is_authenticated:
        return render_template('error.html', code=code, message=e), code
    else:
        return render_template('error_unauthenticated.html', code=code, message=e), code