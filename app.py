from flask import Flask
from flask_restful import Api

from models import db
from resources import Register, Login, AddTask

app = Flask(__name__)
app.config["SECRET_KEY"] = "Millionaire"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Task.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/"
db.init_app(app)

api = Api(app)
api.add_resource(Register, "/register")
api.add_resource(Login, "/login")
api.add_resource(AddTask, "/add-task")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
