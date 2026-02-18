from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory.db"
app.secret_key = "panda"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(12), nullable=False)

class Task(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    task = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey("user.id"))

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("role"):
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


def is_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper



@app.route("/")
def home():
    return "<h1>Home Page</h1>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        user = User.query.filter(User.username == session.get("user")).first()

        if not user:
            session.pop("user", None)
            return redirect(url_for("login"))

        if user and user.role == "admin":
            return render_template("user/adminPage.html", error="", username = session["user"])
        else:
            return render_template("user/userPage.html", error="", username = session["user"])

    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        user = User.query.filter(User.username == str(name).lower()).first()
        if user:
            if user.role == "admin":
                if user.username == str(name).lower() and user.password == password:
                    session["user"] = str(name).lower()
                    session["role"] = "admin"
                    return render_template("user/adminPage.html", error="", username = session["user"])
                else:
                    return render_template("user/login.html", error="Invalid Username or Password")
            else:
                if user.username == str(name).lower() and user.password == password:
                    session["user"] = str(name).lower()
                    session["role"] = "user"
                    return render_template("user/userPage.html", error="", username = session["user"])
                else:
                    return render_template("user/login.html", error="Invalid Username or Password")
        else:
            return render_template("user/login.html", error="Unauthorized User")
        
    return render_template("user/login.html", error="")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/user/add_user", methods=["GET", "POST"])
@admin_required
def add_user():

    if request.method == "POST":    
        name = request.form.get("name")
        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter(User.username == str(name).lower()).first()
        if not user:
            user = User()
            user.username = str(name).lower()
            user.role = str(role).lower()
            user.email = str(email)
            user.password = str(password)

            db.session.add(user)
            db.session.commit()
            return render_template("/user/userAdd.html", error="", message="User added successfully")
        else:
            return render_template("/user/userAdd.html", error="User already exists", message="")
    return render_template("/user/userAdd.html", error="", message="")
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)