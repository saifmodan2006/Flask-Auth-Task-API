from flask import Flask
from flask_restful import Api
from flask import render_template
from models import db
from resources import Register, Login, AddTask , UpdateTask , DeleteTask , TaskList , ResetPassword , ForgotPassword

app = Flask(__name__)
app.config["SECRET_KEY"] = "Millionaire"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Task.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/"
db.init_app(app)
print(app.url_map)


api = Api(app)
api.add_resource(Register, "/register")
api.add_resource(Login, "/login")
api.add_resource(AddTask, "/add-task")
api.add_resource(TaskList, "/task-list")
# api.add_resource(UpdateTask, "/update-task")
# api.add_resource(DeleteTask, "/delete-task")
# api.add_resource(DeleteTask, "/forget-password")

# api.add_resource(ForgotPassword, "/forgot-password")
# api.add_resource(ResetPassword, "/reset-password/<token>")


api.add_resource(UpdateTask, "/update-task/<int:task_id>")
api.add_resource(DeleteTask, "/delete-task/<int:task_id>")


api.add_resource(ForgotPassword, "/forgot-password")
api.add_resource(ResetPassword, "/reset-password/<string:token>")



@app.route("/")
def home():
    return render_template("register.html")

@app.route("/login-page")
def login_page():
    return render_template("login.html")


@app.route("/forgot")
def forgot_page():
    return render_template("forgot.html")

@app.route("/reset/<token>")
def reset_page(token):
    return render_template("reset.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)



