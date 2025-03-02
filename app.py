import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, url_for, flash, abort
from werkzeug.security import generate_password_hash
import db
from werkzeug.security import check_password_hash
import config
import events
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key


def check_csrf():
    if "csrf_token" not in session or request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


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
        SELECT id, title, description, event_start, event_end, event_space, event_type
        FROM events
        WHERE event_start BETWEEN ? AND ?
    """
    event_list = db.query(sql, (start_date, end_date))

    # Create a dictionary for mapping the database event space values to human-readable names
    space_mapping = {
        "space1": "Auditorio",
        "space2": "Päälava",
        "space3": "Kellari"
    }

    events_by_space = {space_name: [] for space_name in space_mapping.values()}

    for event_id, title, description, start, end, space, event_type in event_list:
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
            "id": event_id,
            "title": title,
            "description": description,
            "start": start_hour,
            "end": end_hour,
            "weekday_index": weekday_index,
            "type": event_type.lower() if event_type else "default"
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

    # Get selected event types from the filter
    selected_filters = request.args.getlist("filter")

    # Filter events based on selected event types
    if selected_filters:
        filtered_events_by_space = {}
        for space_name, space_events in events_by_space.items():
            filtered_events_by_space[space_name] = [
                event for event in space_events if event["type"] in selected_filters
            ]
        events_by_space = filtered_events_by_space
    else:
        filtered_events_by_space = events_by_space  # No filters, show all events

    return render_template(
        "index.html",
        events_by_space=events_by_space,
        selected_filters=selected_filters,
        week_offset=week_offset,
        week_dates=week_dates
    )


@app.route("/clear_filter")
def clear_filter():
    week_offset = int(request.args.get("week", 0))
    return redirect(url_for('index', week=week_offset))  # Redirect back to the same week with no filter applied


@app.route("/new_event", methods=["GET", "POST"])
def new_event():
    if "username" not in session:
        flash("Sinun täytyy kirjautua sisään luodaksesi tapahtuman.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        check_csrf()

        title = request.form["title"]
        description = request.form["description"]
        event_date = request.form["event-date"]
        event_start_time = request.form["event-start-time"]
        event_end_time = request.form["event-end-time"]
        event_space = request.form.get("event-space", "default")
        event_type = request.form["event-type"]  # You need to use event_type

        start_hour = int(event_start_time.split(":")[0])
        end_hour = int(event_end_time.split(":")[0])

        event_start = f"{event_date}T{event_start_time}"
        event_end = f"{event_date}T{event_end_time}"

        if start_hour < 8 or end_hour > 22:
            flash("Tapahtuman täytyy olla välillä 08:00 - 22:00.", "danger")
            return redirect(url_for("new_event"))
        max_participants = int(request.form["max_participants"])

        if events.check_event_space_availability(event_start, event_end, event_space):
            username = session["username"]
            events.add_event(title, description, event_start, event_end, event_space, event_type, username, max_participants)
            flash(f"Event '{title}' created successfully!", "success")
            return redirect(url_for("new_event"))
        else:
            flash("Event space is not available for the selected time.", "danger")
            return redirect(url_for("new_event"))

        if not title or not description or not event_start or not event_end or not event_space or not event_type:
            flash("Täytä kaikki kentät!", "danger")
            return redirect(url_for("new_event"))

        if end_hour <= start_hour:
            flash("Päättymisaika täytyy olla alkamisaikaa myöhemmin!", "danger")
            return redirect(url_for("new_event"))

    user_events = events.get_user_events(session["username"]) if "username" in session else []
    return render_template("new_event.html", events=user_events)


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
        check_csrf()
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

    check_csrf()

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
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)  # Ensure CSRF token is created
    print("CSRF Token in Session:", session["csrf_token"])  # Debugging output
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    check_csrf()

    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if not username or not password1 or not password2:
        flash("Täytä kaikki kentät!", "danger")
        return redirect(url_for("register"))

    if password1 != password2:
        return render_template("register.html", error="VIRHE: Salasanat eivät ole samat.")

    if len(password1) < 6:
        flash("Salasanan täytyy olla vähintään 6 merkkiä pitkä!", "danger")
        return redirect(url_for("register"))

    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])

        session["success_message"] = "Tunnus luotiin onnistuneesti! Kirjaudu sisään ilmoittaaksesi tapahtuman."

        return redirect(url_for("login"))  # Redirect to login
    except sqlite3.IntegrityError:
        return render_template("register.html", error="VIRHE: Tunnus on jo varattu.")


@app.route("/event/<int:event_id>", methods=["GET", "POST"])
def event_page(event_id):
    event = events.get_event_by_id(event_id)

    if event is None:
        flash("Tapahtumaa ei löytynyt!", "danger")
        return redirect(url_for("index"))

    # Get total signed-up participants
    sql = "SELECT SUM(group_size) FROM event_signups WHERE event_id = ?"
    total_signed_up = db.query(sql, [event_id])[0][0] or 0

    # Calculate remaining spots
    remaining_spots = event["max_participants"] - total_signed_up

    # Fetch comments for this event
    comments_sql = "SELECT id, username, comment, timestamp FROM comments WHERE event_id = ? ORDER BY timestamp DESC"
    comments = db.query(comments_sql, [event_id])

    if request.method == "POST":
        if "username" not in session:
            flash("Sinun täytyy kirjautua sisään!", "danger")
            return redirect(url_for("login"))

        # If the user submitted a group size for sign-up
        if "group_size" in request.form:
            group_size = int(request.form["group_size"])

            if group_size > remaining_spots:
                flash(f"Virhe, liikaa osallistujia. Vapaita paikkoja jäljellä: {remaining_spots}", "danger")
            else:
                sql = "INSERT INTO event_signups (event_id, username, group_size) VALUES (?, ?, ?)"
                db.execute(sql, [event_id, session["username"], group_size])
                flash("Ilmoittautuminen onnistui!", "success")

        # If the user submitted a comment
        elif "comment" in request.form:
            comment_text = request.form["comment"].strip()

            if comment_text:
                insert_comment_sql = "INSERT INTO comments (event_id, username, comment) VALUES (?, ?, ?)"
                db.execute(insert_comment_sql, [event_id, session["username"], comment_text])
                flash("Kommentti lisätty!", "success")
            else:
                flash("Kommentti ei voi olla tyhjä!", "danger")

        return redirect(url_for("event_page", event_id=event_id))

    return render_template("event.html", event=event, total_signed_up=total_signed_up, remaining_spots=remaining_spots, comments=comments)


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()

    if not query:
        flash("Syötä hakusana!", "danger")
        return redirect(url_for("index"))

    sql = """
        SELECT id, title, description, event_start, event_end, event_space, event_type
        FROM events
        WHERE title LIKE ? OR description LIKE ?
    """
    events = db.query(sql, [f"%{query}%", f"%{query}%"])

    return render_template("search_results.html", events=events, query=query)


@app.route("/cancel_signup/<int:event_id>", methods=["POST"])
def cancel_signup(event_id):
    if "username" not in session:
        flash("Sinun täytyy kirjautua sisään peruuttaaksesi ilmoittautumisen.", "danger")
        return redirect(url_for("login"))

    check_csrf()

    sql = "DELETE FROM event_signups WHERE event_id = ? AND username = ?"
    db.execute(sql, [event_id, session["username"]])
    flash("Ilmoittautuminen peruutettu!", "success")
    return redirect(url_for("event_page", event_id=event_id))


@app.route("/delete_comment/<int:comment_id>/<int:event_id>", methods=["POST"])
def delete_comment(comment_id, event_id):
    if "username" not in session:
        flash("Sinun täytyy kirjautua sisään poistaaksesi kommentin.", "danger")
        return redirect(url_for("login"))

    check_csrf()

    sql = "DELETE FROM comments WHERE id = ? AND username = ?"
    db.execute(sql, [comment_id, session["username"]])
    flash("Kommentti poistettu!", "success")

    return redirect(url_for("event_page", event_id=event_id))


@app.route("/profile")
def profile():
    if "username" not in session:
        flash("Sinun täytyy kirjautua sisään nähdäksesi profiilisi!", "danger")
        return redirect(url_for("login"))

    username = session["username"]

    sql_events = "SELECT id, title, event_start, event_end FROM events WHERE username = ?"
    user_events = db.query(sql_events, [username])

    sql_signups = """
        SELECT e.id, e.title, e.event_start, e.event_end, es.group_size
        FROM event_signups es
        JOIN events e ON es.event_id = e.id
        WHERE es.username = ?
    """
    user_signups = db.query(sql_signups, [username])

    sql_comments = """
        SELECT c.comment, c.timestamp, c.username, e.title
        FROM comments c
        JOIN events e ON c.event_id = e.id
        WHERE e.username = ?
        ORDER BY c.timestamp DESC
    """
    received_comments = db.query(sql_comments, [username])

    return render_template(
        "profile.html",
        user_events=user_events,
        user_signups=user_signups,
        received_comments=received_comments
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT username, password_hash FROM users WHERE username = ?"
    user = db.query(sql, [username])

    if not user:  # 🔹 If user list is empty, return an error message
        flash("VIRHE: Käyttäjätunnusta ei löydy!", "danger")
        return redirect(url_for("login"))

    if check_password_hash(user[0]["password_hash"], password):
        session["username"] = user[0]["username"]
        session["csrf_token"] = secrets.token_hex(16)  # Generate new CSRF token
        return redirect("/")
    else:
        flash("VIRHE: Väärä salasana!", "danger")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")
