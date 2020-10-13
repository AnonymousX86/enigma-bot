def find_user(id_or_mention):
    """Check if argument is ID or mention and return ID or None"""
    # No arg provided
    if id_or_mention is None:
        return None

    # User ID
    elif len(id_or_mention) == 18:
        try:
            id_or_mention = int(id_or_mention)
            return id_or_mention
        except TypeError:
            pass

    # User mention
    elif len(id_or_mention) == 22:
        try:
            # Mention format: <@!185078376037591478>
            id_or_mention = int(id_or_mention[3:-1])
            return id_or_mention
        except TypeError:
            pass

    # Neither
    else:
        return None
