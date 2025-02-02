import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash
import db
from werkzeug.security import check_password_hash
import config
import events
from datetime import datetime

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    weekday = ["maanantai", "tiistai", "keskiviikko", "torstai", "perjantai", "lauantai", "sunnuntai"]

    # Fetch events from database
    sql = "SELECT title, event_start, event_end, event_space FROM events"
    event_list = db.query(sql)  # Assuming db.query() returns a list of tuples

    # Organizing events by space
    events_by_space = {
        "Auditorio": [],
        "Kellari": [],
        "Päälava": []
    }

    for event in event_list:
        title, start, end, space = event
        start_time = datetime.strptime(start, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end, "%Y-%m-%dT%H:%M")

        event_data = {
            "title": title,
            "start": start_time.hour,
            "end": end_time.hour,
            "day": start_time.strftime('%A').lower(),  # Store lowercase weekday for template use
        }

        # Assign event to the correct space
        if space == "space1":
            events_by_space["Auditorio"].append(event_data)
        elif space == "space2":
            events_by_space["Kellari"].append(event_data)
        elif space == "space3":
            events_by_space["Päälava"].append(event_data)

    return render_template("index.html", events_by_space=events_by_space, weekday=weekday)


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

        start_hour = int(event_start.split("T")[1].split(":")[0])
        end_hour = int(event_end.split("T")[1].split(":")[0])

        if start_hour < 8 or end_hour > 22:
            flash("Tapahtuman täytyy olla välillä 08:00 - 22:00.", "danger")
            return redirect(url_for("new_event"))

        if events.check_event_space_availability(event_start, event_end, event_space):
            events.add_event(title, description, event_start, event_end, event_space)
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
