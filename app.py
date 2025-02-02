import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash
import db
from werkzeug.security import check_password_hash
import config
import events
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = config.secret_key


def get_week_dates(base_date):
    """Get start and end date for the requested week and formatted day names with dates."""
    start_of_week = base_date - timedelta(days=base_date.weekday())
    week_dates = [
        (start_of_week + timedelta(days=i)).strftime("%a %d.%m.%y")  # e.g., "Ti 04.02.25"
        for i in range(7)
    ]
    return start_of_week.strftime("%Y-%m-%d"), (start_of_week + timedelta(days=6)).strftime("%Y-%m-%d"), week_dates


def get_events(start_date, end_date):
    """Get events from the database for the given date range."""
    sql = """
        SELECT title, description, event_start, event_end, event_space, event_type
        FROM events
        WHERE event_start BETWEEN ? AND ?
    """
    event_list = db.query(sql, (start_date, end_date))

    # Create a dictionary for mapping the database event space values to human-readable names
    space_mapping = {
        "space1": "Auditorio",
        "space2": "Kellari",
        "space3": "Päälava"
    }

    events_by_space = {space_name: [] for space_name in space_mapping.values()}

    for title, description, start, end, space, event_type in event_list:
        start_time = datetime.strptime(start, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end, "%Y-%m-%dT%H:%M")

        start_hour = start_time.hour
        end_hour = end_time.hour
        weekday_index = start_time.weekday()  # Monday = 0, Sunday = 6

        # Map the event space to the human-readable name
        space_name = space_mapping.get(space, "Unknown")  # Default to "Unknown" if space is not in the mapping

        # Check if event_type is None and assign a default value if so
        if event_type is None:
            event_type = "default"  # Assign a default value if event_type is None

        event_data = {
            "title": title,
            "description": description,
            "start": start_hour,
            "end": end_hour,
            "weekday_index": weekday_index,
            "type": event_type.lower()  # Ensure type is in lowercase for consistent CSS classes
        }

        # Append the event data to the corresponding space
        events_by_space[space_name].append(event_data)

    return events_by_space


@app.route("/")
def index():
    week_offset = int(request.args.get("week", 0))
    base_date = datetime.today() + timedelta(weeks=week_offset)
    start_date, end_date, week_dates = get_week_dates(base_date)

    # Get events for the week
    events_by_space = get_events(start_date, end_date)

    return render_template("index.html", events_by_space=events_by_space, week_offset=week_offset, week_dates=week_dates)


@app.route("/new_event", methods=["GET", "POST"])
def new_event():
    if "username" not in session:
        flash("Sinun täytyy kirjautua sisään luodaksesi tapahtuman.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        event_start = request.form["event-start"]
        event_end = request.form["event-end"]
        event_space = request.form.get("event-space", "default")
        event_type = request.form["event-type"]  # You need to use event_type

        start_hour = int(event_start.split("T")[1].split(":")[0])
        end_hour = int(event_end.split("T")[1].split(":")[0])

        if start_hour < 8 or end_hour > 22:
            flash("Tapahtuman täytyy olla välillä 08:00 - 22:00.", "danger")
            return redirect(url_for("new_event"))

        if events.check_event_space_availability(event_start, event_end, event_space):
            # Pass event_type along with other parameters
            username = session["username"]
            events.add_event(title, description, event_start, event_end, event_space, event_type, username)
            flash(f"Event '{title}' created successfully!", "success")
            return redirect(url_for("new_event"))
        else:
            flash("Event space is not available for the selected time.", "danger")
            return redirect(url_for("new_event"))

    return render_template("new_event.html")


@app.route("/events")
def event_list():
    sql = "SELECT title, event_start, event_end, event_space FROM events"
    event_list = db.query(sql)

    events_by_space = {"space1": [], "space2": [], "space3": []}

    for event in event_list:
        title, start, end, space = event
        start_hour = int(start.split("T")[1].split(":")[0])
        end_hour = int(end.split("T")[1].split(":")[0])

        if space in events_by_space:
            events_by_space[space].append((title, start_hour, end_hour))
        else:
            continue

    return render_template("index.html", events_by_space=events_by_space)


@app.route("/my_events")
def my_events():
    if "username" not in session:
        flash("Sinun täytyy kirjautua sisään nähdäksesi omat tapahtumat.", "danger")
        return redirect(url_for("login"))

    # Fetch events that belong to the logged-in user
    events_list = events.get_user_events(session["username"])
    return render_template("my_events.html", events=events_list)


@app.route("/edit_event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    if "username" not in session:
        flash("Sinun täytyy kirjautua sisään muokataksesi tapahtumaa.", "danger")
        return redirect(url_for("login"))

    event = events.get_event_by_id(event_id)

    if event is None or event["username"] != session["username"]:
        flash("Tätä tapahtumaa ei löydy tai et omista tätä tapahtumaa.", "danger")
        return redirect(url_for("my_events"))

    if request.method == "POST":
        # Get updated event details from the form
        title = request.form["title"]
        description = request.form["description"]
        event_start = request.form["event-start"]
        event_end = request.form["event-end"]
        event_space = request.form["event-space"]
        event_type = request.form["event-type"]

        # Update event in the database
        events.update_event(event_id, title, description, event_start, event_end, event_space, event_type)
        flash("Tapahtuma päivitetty onnistuneesti!", "success")
        return redirect(url_for("my_events"))

    return render_template("edit_event.html", event=event)


@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):
    if "username" not in session:
        flash("Sinun täytyy kirjautua sisään poistaaksesi tapahtuman.", "danger")
        return redirect(url_for("login"))

    event = events.get_event_by_id(event_id)

    if event is None or event["username"] != session["username"]:
        flash("Tätä tapahtumaa ei löydy tai et omista tätä tapahtumaa.", "danger")
        return redirect(url_for("my_events"))

    # Delete event from the database
    events.delete_event(event_id)
    flash("Tapahtuma poistettu onnistuneesti!", "success")
    return redirect(url_for("my_events"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT password_hash FROM users WHERE username = ?"
        password_hash = db.query(sql, [username])[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")
