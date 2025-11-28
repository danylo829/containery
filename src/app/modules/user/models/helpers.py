def merge_named_list(current_list, default_list):
    """Merge two lists of dicts keyed by 'name' non-destructively while preserving
    the user's ordering.

    Returns a new merged list preserving user ordering first, then new defaults.
    """
    # Map defaults by name for quick lookup and preserve their order in a list.
    default_map = {}
    default_order = []
    for d in default_list:
        if isinstance(d, dict):
            name = d.get('name')
            if name and name not in default_map:
                default_map[name] = d
                default_order.append(name)

    seen = set()
    merged = []
    # Preserve user ordering, keep only valid & first occurrences.
    for item in current_list:
        if not isinstance(item, dict):
            continue
        name = item.get('name')
        if not name or name not in default_map or name in seen:
            continue
        seen.add(name)
        # Fill missing keys from default definition (non-destructive).
        default_item = default_map[name]
        for k, v in default_item.items():
            if k not in item:
                item[k] = v
        merged.append(item)

    # Append new defaults not present in user list in default order.
    for name in default_order:
        if name not in seen:
            merged.append(default_map[name])

    return merged