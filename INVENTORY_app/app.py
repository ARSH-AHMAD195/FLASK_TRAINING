from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
db = SQLAlchemy(app)

class Product(db.Model):
    pid = db.Column(db.Integer, primary_key = True)
    pname = db.Column(db.String(50), nullable = False)
    price = db.Column(db.Float(12,2), nullable = False)
    qty = db.Column(db.Integer, nullable = False)


@app.route("/")
def home():
    return "<p>Home</p>"

@app.get("/product/add")
def add_user():
    return render_template("productAdd.html")

@app.post("/product/add/submit")
def user_add_submit_action():
    pname = request.form.get('pname')
    price = request.form.get('price')
    qty = request.form.get('qty')

    if not pname or not price:
        return {"error": "Product name and price are required"}, 400

    product = Product()
    product.pname = pname
    product.price = float(price)
    product.qty = qty

    db.session.add(product)
    db.session.commit()

    return fetch_products()

@app.route("/product/show")
def fetch_products():
    products = Product.query.all()

    return render_template("productShow.html",products = products)


# @app.route("/user/update/<int:id>")
# def update_user(id):
#     user = db.session.get(User, id)

#     if not user:
#         return "<p>ERROR: User not found</p>", 404

#     name = request.args.get("name", default="", type=str)
#     role = request.args.get("role", default="", type=str)

#     if name:
#         user.name = name

#     if role:
#         user.role = role

#     db.session.commit()
#     return f"<p>MESSAGE: User {user.name} updated successfully</p>"


# @app.route("/user/delete/<int:id>")
# def delete_user(id):
#     user = db.session.get(User, id)
    
#     if not user:
#         return "<p>ERROR: User not found</p>", 404

#     db.session.delete(user)
#     db.session.commit()
#     return f"<p>MESSAGE: User {user.name} deleted successfully</p>"

# @app.get("/post/add")
# def add_post():
#     return render_template("post/postAdd.html")

    
# @app.post("/post/add/submit")
# def add_post_submit():
#     name = request.form.get('name')
#     user = User.query.filter(User.name == name).first()
    
#     if user:
#         title = request.form.get('title')
#         content = request.form.get('content')   
#         if not title or not content:
#             return {"error": "Title and content are required"}, 400

#         post = Post()
#         post.title = title
#         post.content = content
#         post.userid = user.id

#         db.session.add(post)
#         db.session.commit()
#         return {"post":f"Added {post.title}"}

#     else:
#         return {"error": "Not registerd user"}, 400
    

# # @app.get("/post/show")
# # def show_post():
# #     posts = db.session.query(User, Post).join(User,Post.userid == User.id).all()

    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)   