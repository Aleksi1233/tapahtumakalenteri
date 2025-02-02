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
            "event_type": event_type  # Added event_type to the result
        })

    return events


def add_event(title, description, event_start, event_end, event_space, event_type):
    sql = (
        "INSERT INTO events (title, description, event_start, event_end, event_space, event_type) "
        "VALUES (?, ?, ?, ?, ?, ?)"
    )
    db.execute(sql, [title, description, event_start, event_end, event_space, event_type])  # Include event_type


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
            "event_type": event_type  # Added event_type to the result
        })

    return events

