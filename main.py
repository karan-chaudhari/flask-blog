from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json,os

with open('config.json','r') as f:
    params = json.load(f)['params']

local_server = True

app = Flask(__name__)
app.secret_key = "my-secret-key"
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]    
db = SQLAlchemy(app)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=False, nullable=False)
    datetime = db.Column(db.String(20), unique=False, nullable=True)
    tagline = db.Column(db.String(50), unique=False, nullable=False)
    slug = db.Column(db.String(50), unique=False, nullable=False)
    img_file = db.Column(db.String(50), unique=False, nullable=False)
    content = db.Column(db.String(1000), unique=False, nullable=False)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=False, nullable=False)
    phone_num = db.Column(db.String(15), unique=False, nullable=False)
    message = db.Column(db.String(500), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    return render_template("index.html",posts=posts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        msg = request.form.get("message")
        entry = Contacts(name=name,email=email,phone_num=phone,message=msg,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        flash("Thanks for submitting your detail. We will get back to you soon.","success")
    return render_template("contact.html")

@app.route("/post/<string:post_slug>",methods=["GET"])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",post=post)

app.run(debug=True)