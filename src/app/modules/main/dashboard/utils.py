from flask import session

from app.modules.settings.models import GlobalSettings
from app.config import Config

from packaging import version
import requests
import time

GITHUB_API_URL = "https://api.github.com/repos/danylo829/containery/releases/latest"
CHECK_INTERVAL_MINUTES = 1

def validate_version(ver: str) -> bool:
    try:
        version.parse(ver)
        return True
    except Exception:
        return False

def fetch_latest_version() -> str:
    try:
        response = requests.get(GITHUB_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            tag_name = data.get("tag_name", "")
            return tag_name.lstrip("v")
    except Exception:
        pass
    return ""

def check_for_update() -> tuple[str, bool]:
    if not validate_version(Config.VERSION):
        return "unknown", False

    latest_version = GlobalSettings.get_setting('latest_version')
    last_checked_ts = GlobalSettings.get_setting('latest_version_checked_at')
    last_checked = None
    if last_checked_ts:
        try:
            last_checked = float(last_checked_ts)
        except Exception:
            last_checked = None

    now_ts = time.time()
    should_check = not last_checked or (now_ts - last_checked) > CHECK_INTERVAL_MINUTES * 60

    if should_check:
        fetched_version = fetch_latest_version()
        if fetched_version:
            latest_version = fetched_version
            GlobalSettings.set_setting('latest_version', latest_version)
            GlobalSettings.set_setting('latest_version_checked_at', str(now_ts))

    show_update_notification = (
        latest_version
        and version.parse(Config.VERSION) < version.parse(latest_version)
        and latest_version != ''
        and not session.get('dismiss_update_notification', False)
    )

    return str(latest_version or "unknown"), bool(show_update_notification)