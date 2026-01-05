from flask import request
from flask_restful import Resource
from passlib.hash import pbkdf2_sha256
import jwt
import secrets
import os
import string
from datetime import datetime, timedelta

from models import db, User, Task
from flask import current_app


def generate_filename(original_filename):
    chars = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(8))
    ext = os.path.splitext(original_filename)[1]
    return f"pr_{random_part}{ext}"


class Register(Resource):
    def post(self):
        args = request.form
        img = request.files.get("image")

        username = args.get("username")
        email = args.get("email")
        password = args.get("password")

        if not username or not email or not password:
            return {"message": "All fields are required"}, 400

        if User.query.filter_by(username=username).first():
            return {"message": "username already exists"}, 409

        filename = None
        if img:
            filename = generate_filename(img.filename)
            img.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

        password_hash = pbkdf2_sha256.hash(password)

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            profile_image=filename
        )

        db.session.add(user)
        db.session.commit()

        return {
            "message": "user created successfully",
            "username": user.username,
            "profile_image": filename
        }, 201


class Login(Resource):
    def post(self):
        username = request.args.get("username")
        password = request.args.get("password")

        if not username or not password:
            return {"message": "username and password are required"}, 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return {"message": "User not found"}, 404

        if not pbkdf2_sha256.verify(password, user.password_hash):
            return {"message": "Invalid credentials"}, 400

        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        return {"token": token}, 200


class AddTask(Resource):
    def post(self):
        data = request.get_json()

        if not data:
            return {"message": "JSON data required"}, 400

        title = data.get("title")
        description = data.get("description")

        if not title:
            return {"message": "Task title is required"}, 400

        task = Task(title=title, description=description)
        db.session.add(task)
        db.session.commit()

        return {"message": "Task added successfully"}, 201

class UpdateTask(Resource):
    def post(self):
        pass
