# app.py
import os
import secrets
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, flash, url_for
from marshmallow import ValidationError
from passlib.hash import pbkdf2_sha256
from flask_mail import Mail, Message

from models import db, User
from schemas import RegisterSchema, LoginSchema, ForgotSchema, ResetSchema

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "super-secret-key")

# Use a single DB file in project root (avoids instance path issues)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "Task.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Flask-Mail configuration (read from environment; set these before running)
# For Gmail use:
#   MAIL_SERVER=smtp.gmail.com
#   MAIL_PORT=587
#   MAIL_USE_TLS=True
#   MAIL_USERNAME=<your-email>
#   MAIL_PASSWORD=<app-password>
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL", "False") == "True"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"])

mail = Mail(app)
db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- Register (server-side form) ----------------
@app.route("/test-mail")
def test_mail():
    from flask_mail import Message
    msg = Message(
        subject="Test Email From Flask",
        recipients=["modansaif786@gmail.com"],
        body="If you receive this email, Flask-Mail is working correctly."
    )
    mail.send(msg)
    return "Mail sent successfully"

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            data = RegisterSchema().load(request.form)
        except ValidationError as err:
            for v in err.messages.values():
                flash(", ".join(v))
            return redirect(url_for("register"))

        # Unique checks
        if User.query.filter_by(username=data["username"]).first():
            flash("Username already exists")
            return redirect(url_for("register"))
        if User.query.filter_by(email=data["email"]).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=pbkdf2_sha256.hash(data["password"])
        )
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully. You can now login.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- Login (server-side form) ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            data = LoginSchema().load(request.form)
        except ValidationError as err:
            for v in err.messages.values():
                flash(", ".join(v))
            return redirect(url_for("login"))

        user = User.query.filter_by(username=data["username"]).first()
        if not user or not pbkdf2_sha256.verify(data["password"], user.password_hash):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        flash("Login successful (demo).")
        # In a real app set a session or JWT here
        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- Forgot (send email) ----------------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        try:
            data = ForgotSchema().load(request.form)
        except ValidationError as err:
            for v in err.messages.values():
                flash(", ".join(v))
            return redirect(url_for("forgot"))

        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            flash("If the email exists, a reset link will be sent.")  # don't reveal
            return redirect(url_for("forgot"))

        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.token_expiry = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()

        reset_url = url_for("reset", token=token, _external=True)

        # Send email
        try:
            msg = Message("Password reset request", recipients=[user.email])
            msg.body = f"Hello {user.username},\n\nUse the link below to reset your password (valid for 30 minutes):\n\n{reset_url}\n\nIf you didn't request this, you can ignore this email."
            mail.send(msg)
            flash("Reset link sent to your email.")
        except Exception as e:
            # In development, it's useful to show the link if mail fails
            flash("Failed to send email. (Check mail config).")
            flash(f"Reset link (for dev): {reset_url}")

        return redirect(url_for("forgot"))

    return render_template("forgot.html")


# ---------------- Reset (form via token) ----------------
@app.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return "Invalid or expired token", 400

    if user.token_expiry is None or user.token_expiry < datetime.utcnow():
        return "Token expired", 400

    if request.method == "POST":
        try:
            data = ResetSchema().load(request.form)
        except ValidationError as err:
            for v in err.messages.values():
                flash(", ".join(v))
            return redirect(request.url)

        user.password_hash = pbkdf2_sha256.hash(data["password"])
        user.reset_token = None
        user.token_expiry = None
        db.session.commit()

        flash("Password reset successful. You can login now.")
        return redirect(url_for("login"))

    return render_template("reset.html")

if __name__ == "__main__":
    app.run(debug=True)
