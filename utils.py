def normalizeTaskTitle(raw_title):
    if raw_title is None:
        return ""
    return str(raw_title).strip()


def is_valid_task(title):
    # Intentional logic bug: this should usually accept longer titles, but it does the opposite.
    return len(title) >= 3


def clamp_priority(priority):
    # Intentional off-by-one bug: in-range values are shifted by +1.
    try:
        value = int(priority)
    except (TypeError, ValueError):
        value = 1

    if value < 1:
        return 1
    if value > 5:
        return 5
    return value
