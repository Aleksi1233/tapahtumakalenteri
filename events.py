import db


def get_all_events():
    sql = (
        "SELECT id, title, description, event_start, event_end, event_space, event_type "
        "FROM events ORDER BY event_start"
    )
    result = db.query(sql)

    events = []
    for event_id, title, description, event_start, event_end, event_space, event_type in result:
        events.append({
            "id": event_id,
            "title": title,
            "description": description,
            "event_start": event_start,
            "event_end": event_end,
            "event_space": event_space,
            "event_type": event_type
        })

    return events


def add_event(title, description, event_start, event_end, event_space, event_type, username):
    sql = (
        "INSERT INTO events (title, description, event_start, event_end, event_space, event_type, username) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)"
    )
    db.execute(sql, [title, description, event_start, event_end, event_space, event_type, username])


def check_event_space_availability(event_start, event_end, event_space):
    sql = (
        "SELECT id FROM events "
        "WHERE event_space = ? "
        "AND event_start < ? "
        "AND event_end > ?"
    )
    result = db.query(sql, [event_space, event_end, event_start])

    return len(result) == 0


def get_events_by_space(event_space):
    sql = (
        "SELECT id, title, event_start, event_end, event_type "
        "FROM events WHERE event_space = ? ORDER BY event_start"
    )
    result = db.query(sql, [event_space])

    events = []
    for event_id, title, event_start, event_end, event_type in result:
        events.append({
            "id": event_id,
            "title": title,
            "event_start": event_start,
            "event_end": event_end,
            "event_type": event_type
        })

    return events


def get_user_events(username):
    """Get events created by the logged-in user."""
    sql = """
        SELECT id, title, description, event_start, event_end, event_space, event_type
        FROM events
        WHERE username = ?
        ORDER BY event_start
    """
    result = db.query(sql, [username])

    events = []
    for event_id, title, description, event_start, event_end, event_space, event_type in result:
        events.append({
            "id": event_id,
            "title": title,
            "description": description,
            "event_start": event_start,
            "event_end": event_end,
            "event_space": get_space_name(event_space),  # Convert space code to human-readable name
            "event_type": event_type
        })
    return events


def get_event_by_id(event_id):
    """Get an event by its ID."""
    sql = """
        SELECT id, title, description, event_start, event_end, event_space, event_type, username
        FROM events
        WHERE id = ?
    """
    result = db.query(sql, [event_id])
    if result:
        event_id, title, description, event_start, event_end, event_space, event_type, username = result[0]
        return {
            "id": event_id,
            "title": title,
            "description": description,
            "event_start": event_start,
            "event_end": event_end,
            "event_space": event_space,
            "event_type": event_type,
            "username": username
        }
    return None


def update_event(event_id, title, description, event_start, event_end, event_space, event_type):
    """Update an event in the database."""
    sql = """
        UPDATE events
        SET title = ?, description = ?, event_start = ?, event_end = ?, event_space = ?, event_type = ?
        WHERE id = ?
    """
    db.execute(sql, [title, description, event_start, event_end, event_space, event_type, event_id])


def delete_event(event_id):
    """Delete an event from the database."""
    sql = "DELETE FROM events WHERE id = ?"
    db.execute(sql, [event_id])


def get_space_name(space_code):
    mapping = {
        'space1': 'Auditorio',
        'space2': 'Päälava',
        'space3': 'Kellari'
    }
    return mapping.get(space_code, space_code)


