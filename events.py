import db


def get_all_events():
    sql = (
        "SELECT id, title, description, event_start, event_end, event_space "
        "FROM events ORDER BY event_start"
    )
    result = db.query(sql)

    events = []
    for event_id, title, description, event_start, event_end, event_space in result:
        events.append({
            "id": event_id,
            "title": title,
            "description": description,
            "event_start": event_start,
            "event_end": event_end,
            "event_space": event_space
        })

    return events


def add_event(title, description, event_start, event_end, event_space):
    sql = (
        "INSERT INTO events (title, description, event_start, event_end, event_space) "
        "VALUES (?, ?, ?, ?, ?)"
    )
    db.execute(sql, [title, description, event_start, event_end, event_space])


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
        "SELECT id, title, event_start, event_end "
        "FROM events WHERE event_space = ? ORDER BY event_start"
    )
    result = db.query(sql, [event_space])

    events = []
    for event_id, title, event_start, event_end in result:
        events.append({
            "id": event_id,
            "title": title,
            "event_start": event_start,
            "event_end": event_end
        })

    return events
