from flask import Flask, render_template, request, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, os, math

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
    posts = Posts.query.filter_by().all()[::-1]
    last = math.ceil(len(posts)/int(params['home_posts']))
    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['home_posts']):(page-1)*int(params['home_posts'])+int(params['home_posts'])] 
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page+1)
    elif page == last:
        prev = "/?page=" + str(page-1)
        next = "#"       
    else:
        prev = "/?page=" + str(page-1)
        next = "/?page=" + str(page+1)    
    return render_template("index.html",params=params,posts=posts,prev=prev,next=next)

@app.route("/about")
def about():
    return render_template("about.html",params=params)

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
    return render_template("contact.html",params=params)

@app.route("/post/<string:post_slug>",methods=["GET"])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params,post=post)

@app.route("/deshboard", methods=["GET","POST"])
def deshboard():
    if 'admin' in session and session['admin'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template("deshboard.html",params=params,posts=posts)
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('pass')
        if username == params['admin_user'] and password == params['admin_pass']:
            session['admin'] = username
            posts = Posts.query.all()    
        return render_template("deshboard.html",params=params,posts=posts)    
    return render_template("login.html",params=params)

@app.route("/edit/<string:sno>",methods=["GET","POST"])
def edit(sno):
    if 'admin' in session and session['admin'] == params['admin_user']:
        if request.method == "POST":
            box_title = request.form.get('title')
            box_tagline = request.form.get('tagline')
            box_slug = request.form.get('slug')
            box_img = request.form.get('img_file')
            box_content = request.form.get('content')
            date = datetime.now()
            if sno=='0':
                post = Posts(title=box_title,datetime=date,tagline=box_tagline,slug=box_slug,img_file=box_img,content=box_content)
                db.session.add(post)
                db.session.commit()
                return redirect("/")
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.tagline = box_tagline
                post.slug = box_slug
                post.img_file = box_img
                post.content = box_content
                post.datetime = date
                db.session.commit()
                return redirect("/deshboard")   
    post = Posts.query.filter_by(sno=sno).first()
    return render_template("edit.html",params=params,sno=sno,post=post)

@app.route("/delete_post/<string:sno>")
def delete_post(sno):
    if 'admin' in session and session['admin'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect("/deshboard")

@app.route("/logout")
def logout():
    session.pop('admin')
    return render_template("login.html",params=params)

app.run(debug=True)