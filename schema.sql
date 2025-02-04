CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    event_start TEXT NOT NULL,
    event_end TEXT NOT NULL,
    event_space TEXT
, event_type TEXT, username TEXT
);

CREATE TABLE event_signups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    username TEXT,
    group_size INTEGER,
    FOREIGN KEY(event_id) REFERENCES events(id),
    FOREIGN KEY(username) REFERENCES users(username)
);
