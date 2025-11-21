def merge_named_list(current_list, default_list):
    """Merge two lists of dicts keyed by 'name' non-destructively.

    Steps:
    1. Filter out obsolete items (names not in defaults)
    2. Map user items by name for quick lookup
    3. For each default item (preserving default order):
        - Use user item if exists (preserve flags)
        - Add missing keys from default into user item
        - If absent, append default item
    4. Ignore duplicates beyond first occurrence
    Returns new merged list preserving default ordering.
    """
    default_names = [d['name'] for d in default_list if isinstance(d, dict) and 'name' in d]
    name_to_user_item = {}
    for item in current_list:
        if not isinstance(item, dict):
            continue
        name = item.get('name')
        if name in default_names and name not in name_to_user_item:
            name_to_user_item[name] = item
    merged = []
    for d_item in default_list:
        name = d_item.get('name') if isinstance(d_item, dict) else None
        if name and name in name_to_user_item:
            user_item = name_to_user_item[name]
            # Fill missing keys (non-destructive)
            for k, v in d_item.items():
                if k not in user_item:
                    user_item[k] = v
            merged.append(user_item)
        else:
            merged.append(d_item)
    return merged