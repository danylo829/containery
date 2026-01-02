from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user

from app.modules.settings.models import GlobalSettings
from app.modules.settings.forms import GlobalSettingsForm

from app.modules.user.models import Permissions
from app.core.decorators import permission

from app.modules.settings import settings

@settings.route('', methods=['GET', 'POST'])
@permission(Permissions.GLOBAL_SETTINGS_VIEW)
def get_list():
    form = GlobalSettingsForm()

    if request.method == 'POST' and not current_user.has_permission(Permissions.GLOBAL_SETTINGS_EDIT):
        message = f'You do not have the necessary permission.'
        code = 403
        return render_template('error.html', message=message, code=code), code
    
    if request.method == 'GET':
        for field_name, field in form._fields.items():
            if field_name in GlobalSettings.defaults:
                field_value = GlobalSettings.get_setting(field_name)
                field.data = field_value

    if form.validate_on_submit():
        for field_name, field in form._fields.items():
            if field_name in GlobalSettings.defaults:
                try:
                    GlobalSettings.set_setting(field_name, field.data)
                except (ValueError, KeyError) as e:
                    flash(f"Error updating {field_name}: {str(e)}", "error")
                except RuntimeError as e:
                    flash(f"Database error when updating {field_name}: {str(e)}", "error")

        flash("Settings have been saved successfully!", "success")
        return redirect(url_for('settings.get_list'))

    breadcrumbs = [
        {"name": "Dashboard", "url": url_for('main.dashboard.index')},
        {"name": "Settings", "url": None},
    ]
    page_title = 'Global settings'
    
    return render_template('settings/table.html', 
                           breadcrumbs=breadcrumbs, 
                           page_title=page_title,
                           form=form)

@settings.route('/reset', methods=['POST'])
@permission(Permissions.GLOBAL_SETTINGS_EDIT)
def reset_setting():
    field_name = request.json.get('field_name')
    
    if not field_name:
        return jsonify({'error': "Field name is required."}), 400
    
    try:
        GlobalSettings.delete_setting(field_name)
        return jsonify({'message': f"Setting '{field_name}' reset to default."}), 204

    except KeyError:
        return jsonify({'error': f"Setting '{field_name}' is not a valid setting key."}), 400
    except ValueError:
        return jsonify({'error': f"Setting '{field_name}' does not exist in the database."}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
