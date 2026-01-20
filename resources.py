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

from functools import wraps
from models import User


from schemas import RegisterSchema, LoginSchema, ForgotPasswordSchema, ResetPasswordSchema


from marshmallow import ValidationError
# from .schemas import (
#     RegisterSchema,
#     LoginSchema,
#     ForgotPasswordSchema,
#     ResetPasswordSchema
# )


# --- PASTE THIS FUNCTION ABOVE YOUR CLASSES ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if token is in headers (Authorization: Bearer <token>)
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return {'message': 'Token format is invalid. Use Bearer <token>'}, 401
        
        if not token:
            return {'message': 'Token is missing!'}, 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Token is invalid'}, 401
            
        # Pass the current_user to the function
        return f(current_user=current_user, *args, **kwargs)

    return decorated


def generate_filename(original_filename):
    chars = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(8))
    ext = os.path.splitext(original_filename)[1]
    return f"pr_{random_part}{ext}"


class Register(Resource):
    def post(self):
        try:
            data = RegisterSchema().load(request.form)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        img = request.files.get("image")

        if User.query.filter_by(username=data["username"]).first():
            return {"message": "Username already exists"}, 409

        filename = None
        if img:
            filename = generate_filename(img.filename)
            img.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=pbkdf2_sha256.hash(data["password"]),
            profile_image=filename
        )

        db.session.add(user)
        db.session.commit()

        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        return {"message": "User registered", "token": token}, 201


class Login(Resource):
    def post(self):
        try:
            data = LoginSchema().load(
                request.form if request.form else request.args
            )
        except ValidationError as err:
            return {"errors": err.messages}, 400

        user = User.query.filter_by(username=data["username"]).first()
        if not user or not pbkdf2_sha256.verify(
            data["password"], user.password_hash
        ):
            return {"message": "Invalid credentials"}, 401

        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        return {"token": token}, 200


class AddTask(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        # CHANGE IS HERE: force=True ignores the missing header error
        data = request.get_json(force=True) 

        if not data:
            return {"message": "JSON data required"}, 400

        title = data.get("title")
        description = data.get("description")

        if not title:
            return {"message": "Task title is required"}, 400

        # Check for Duplicate Task
        existing_task = Task.query.filter_by(user_id=current_user.id, title=title).first()
        if existing_task:
            return {"message": f"Task '{title}' already exists in your list."}, 409

        # Add Task
        task = Task(title=title, description=description, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()

        return {"message": "Task added successfully"}, 201
    
class TaskList(Resource):
    def get(self):
        tasks = Task.query.all()

        result = []
        for task in tasks:
            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.description
            })

        return {
            "tasks": result
        }, 200


class UpdateTask(Resource):
    def put(self, task_id):
        data = request.get_json()

        task = Task.query.get(task_id)

        if not task:
            return {"message": "Task not found"}, 404
        
        title = data.get("title")
        description = data.get("description")

        if title:
            task.title = title

        if description:
            task.description = description

        db.session.commit()

        return {
            "message": "Task updated successfully",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description
            }
        }, 200

class DeleteTask(Resource):
    def delete(self,task_id):
        task = Task.query.get(task_id)

        if not task:
            return {"message":"Task Not Found"}, 404
        db.session.delete(task)
        db.session.commit()
        
        return{
            "message" : "Task Deleted Successfully"
        },200

class ForgotPassword(Resource):
    def post(self):
        try:
            data = ForgotPasswordSchema().load(request.form)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            return {"message": "Email not found"}, 404

        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.token_expiry = datetime.utcnow() + timedelta(minutes=15)

        db.session.commit()

        return {
            "message": "Reset link generated",
            "reset_link": f"http://127.0.0.1:5000/reset/{token}"
        }

class ResetPassword(Resource):
    def post(self, token):
        try:
            data = ResetPasswordSchema().load(request.form)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        user = User.query.filter_by(reset_token=token).first()
        if not user or user.token_expiry < datetime.utcnow():
            return {"message": "Invalid or expired token"}, 400

        user.password_hash = pbkdf2_sha256.hash(data["password"])
        user.reset_token = None
        user.token_expiry = None
        db.session.commit()

        return {"message": "Password reset successful"}
