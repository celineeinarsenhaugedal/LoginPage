from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import json
import os

app = Flask(__name__)
app.secret_key = "super-hemmelig-nokkel"

# Innlogging varer i 30 dager
app.permanent_session_lifetime = timedelta(days=30)

# Riktig path til users.json i mappen "data"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "users.json")


# -------------------------
# Hjelpefunksjoner
# -------------------------

def load_users():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def find_user(username):
    users = load_users()
    for user in users:
        if user["username"].lower() == username.lower():
            return user
    return None


# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def login_page():
    if session.get("user"):
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = find_user(username)

    if not user or not check_password_hash(user["password"], password):
        flash("Feil brukernavn eller passord.")
        return redirect(url_for("login_page"))

    session.permanent = True
    session["user"] = user["username"]
    return redirect(url_for("home"))


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    firstname = request.form.get("firstname", "").strip()
    lastname = request.form.get("lastname", "").strip()
    email = request.form.get("email", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if find_user(username):
        flash("Brukernavn finnes allerede.")
        return redirect(url_for("register_page"))

    users = load_users()

    users.append({
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "username": username,
        "password": generate_password_hash(password)
    })

    save_users(users)

    session.permanent = True
    session["user"] = username
    return redirect(url_for("home"))


@app.route("/home")
def home():
    if not session.get("user"):
        return redirect(url_for("login_page"))
    return render_template("home.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)