from datetime import datetime
from hashlib import sha256
from urllib.parse import urlparse, urljoin
from markupsafe import escape
import math

def format_docker_timestamp(timestamp):
    if not timestamp:
        return "unknown"
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return dt.strftime("%H:%M %d-%m-%Y")

def format_unix_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def stable_hash(value):
    return int(sha256(value.encode()).hexdigest(), 16) % (10**8)  # Limit the size of the hash

def is_safe_url(target: str, host_url: str) -> bool:
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def bytes_to_human_readable(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


_GRADIENTS = {
    #              light variant                              dark variant
    'aurora':   ('linear-gradient(135deg,#c9d6ff,#e2e2e2)',  'linear-gradient(135deg,#0f0c29,#302b63,#24243e)'),
    'ocean':    ('linear-gradient(135deg,#b2d8f7,#d6eaf8,#e8f5fe)', 'linear-gradient(135deg,#0f2027,#203a43,#2c5364)'),
    'midnight': ('linear-gradient(135deg,#e0e0e0,#f5f5f5)',  'linear-gradient(135deg,#232526,#414345)'),
    'peach':    ('linear-gradient(135deg,#ffecd2,#fcb69f)',   'linear-gradient(135deg,#3a1c71,#d76d77,#ffaf7b)'),
    'mist':     ('linear-gradient(135deg,#e0eafc,#cfdef3)',   'linear-gradient(135deg,#1a2a3a,#2d4a6e,#3a6186)'),
}

_IMAGES = {
    'mountains': '/static/images/wallpaper.jpg',
    'forest':    '/static/images/forest.jpg',
    'space':     '/static/images/space.jpg',
}


def glass_background_css(bg: str, theme: str, custom_url: str = '') -> str:
    """Return an inline <style> tag that sets body.glass background."""
    if bg.startswith('image:'):
        key = bg[len('image:'):]
        path = _IMAGES.get(key)
        if path:
            return f"body.glass{{background-image:url('{path}')}}"

    if bg.startswith('gradient:'):
        key = bg[len('gradient:'):]
        pair = _GRADIENTS.get(key)
        if pair:
            light, dark = pair
            if theme in ('dark', 'dark_mixed'):
                return f"body.glass{{background-image:{dark}}}"
            if theme == 'light':
                return f"body.glass{{background-image:{light}}}"
            # system — emit both with media query
            return (
                f"body.glass{{background-image:{light}}}"
                f"@media(prefers-color-scheme:dark){{body.glass{{background-image:{dark}}}}}"
            )

    if bg == 'custom' and custom_url:
        safe = escape(custom_url)
        return f"body.glass{{background-image:url('{safe}')}}"

    return ''

def paginate_and_sort_list(items, request, search_fields=None, default_sort=None, reverse=False):
    """
    Sorts, searches, and paginates a list of dictionaries based on request args.
    - search_fields: list of keys in the dict to search against
    - default_sort: default key to sort by if 'sort_col' is not provided
    - reverse: default sort direction
    """
    search_val = request.args.get('search', '').lower()
    sort_col = request.args.get('sort_col', default_sort)
    sort_dir = request.args.get('sort_dir', 'desc' if reverse else 'asc')
    
    try:
        page = int(request.args.get('page', 1))
        if page < 1: page = 1
    except ValueError:
        page = 1
        
    try:
        per_page = int(request.args.get('per_page', 15))
        if per_page < 1: per_page = 15
    except ValueError:
        per_page = 15

    # Filter
    if search_val and search_fields:
        filtered = []
        for item in items:
            for field in search_fields:
                val = item.get(field) if isinstance(item, dict) else getattr(item, field, None)
                if val and search_val in str(val).lower():
                    filtered.append(item)
                    break
        items = filtered

    # Sort
    if sort_col:
        is_reverse = sort_dir == 'desc'
        def sort_key(x):
            val = x.get(sort_col) if isinstance(x, dict) else getattr(x, sort_col, None)
            return str(val).lower() if val is not None else ''
        items = sorted(items, key=sort_key, reverse=is_reverse)
        
    # Paginate
    total_items = len(items)
    total_pages = max(1, math.ceil(total_items / per_page))
    if page > total_pages:
        page = total_pages
        
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]
    
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_items': total_items,
        'search': search_val,
        'sort_col': sort_col,
        'sort_dir': sort_dir
    }
    
    return paginated_items, pagination_info

