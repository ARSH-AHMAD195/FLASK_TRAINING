from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory.db"
app.secret_key = "panda"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    password = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(50), nullable = False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), nullable = False)
    content = db.Column(db.Text, nullable = False)
    userid = db.Column(db.String(50), db.ForeignKey("user.id"))

@app.route("/")
def home():
    return "<h1>Home Page</h1>"

@app.route("/user/register", methods=["GET","POST"])
def add_user():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter(User.name==name).first()
        if not user:
            user = User()
            user.name = str(name).lower()
            user.email = str(email)
            user.password = str(password)

            db.session.add(user)
            db.session.commit()
            return redirect(url_for("fetch_user"))
        else:
            return render_template("/user/userRegister.html", error="User already exists!")
    return render_template("/user/userRegister.html", error="")

@app.get("/user/show")
def fetch_user():
    users = User.query.all()
    return render_template("user/userShow.html",users = users)

@app.route("/user/login", methods=["GET", "POST"])
def login():
    allowed_user = {"arsh ahmad": "admin"}

    if "user" in session:
        user = User.query.filter(User.name == str(session["user"]).lower()).first()

        if not user:
            session.pop("user", None)
            return redirect(url_for("login"))

        posts = Post.query.filter(Post.userid == user.id).all()

        if allowed_user.get(session["user"].lower()) == "admin":
            return render_template("dashboard.html", uname=session["user"])
        else:
            return render_template("userPage.html", uname=session["user"], posts=posts)

    if request.method == "POST":
        uname = request.form.get("name")
        password = request.form.get("password")

        
        user = User.query.filter(User.name == str(uname).lower()).first()

        
        if user:
            if str(uname).lower() in allowed_user and allowed_user[str(uname).lower()] == "admin":
                if user and user.password == password:
                    session["user"] = uname
                    return render_template("dashboard.html", uname=session["user"], error="")
                else:
                    return render_template("user/userLogin.html", error="Invalid credentials")
            else:
                if user and user.password == password:
                    session["user"] = uname
                    return render_template("userPage.html", uname=session["user"], error="")
                else:
                    return render_template("user/userLogin.html", error="Invalid credentials")
        return render_template("user/userLogin.html", error="Unauthorized user")
    return render_template("user/userLogin.html", error="")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.post("/post/add/submit")
def add_post_submit():
    name = request.form.get('name')
    user = User.query.filter(User.name == str(name).lower()).first()
    
    if user:
        title = request.form.get('title')
        content = request.form.get('content')   
        if not title or not content:
            return {"error": "Title and content are required"}, 400

        post = Post()
        post.title = title
        post.content = content
        post.userid = user.id

        db.session.add(post)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("user/userLogin.html", error="Not registerd user")

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)  