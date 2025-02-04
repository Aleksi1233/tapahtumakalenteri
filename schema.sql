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
