from flask import Flask, render_template, request, url_for, session, redirect, jsonify, Response
from bson.objectid import ObjectId
import pymongo
import random
import string
from flask_bcrypt import Bcrypt
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

client = pymongo.MongoClient("mongodb+srv://avyuktballari:AZMKXJeKbOWQpB46@cluster0.qk6ukw8.mongodb.net/?retryWrites=true&w=majority")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'edftyguhiu5tf6guhedrftvgbyhnujidrftgyhujidrftgyhucvgbhnjugybhunjcvgbyh'
db = client.get_database('login-register')
userdb = db.users
blogposts = db.blog_posts
comments = db.comments  # New collection for comments
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    notLogged = ''
    username = None
    latest_post = None

    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        latest_post = blogposts.find_one(sort=[("_id", pymongo.DESCENDING)])
        if user:
            username = user["username"]
    else:
        notLogged = True

    return render_template('index.html', home=True, username=username, title="AdiAvi", notLogged=notLogged, latest_post=latest_post)

@app.route('/posts', methods=['GET', 'POST'])
def post():
    new_post_id = None
    username = None
    is_admin = False
    posted = False
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"]
            is_admin = user.get("admin", False)

    if request.method == 'POST':
        if is_admin:
            title = request.form['title']
            subject = request.form['subject']
            content = request.form['content']
            author = request.form['author']
            if title and subject and content and author:
                current_date = datetime.now().date()
                current_date_str = current_date.isoformat()
                result = blogposts.insert_one({
                    "title": title,
                    "subject": subject,
                    "author": author,
                    "date": current_date_str,
                    "content": content
                })
                new_post_id = str(result.inserted_id)
                return redirect(url_for('view_post', post_id=new_post_id))
                posted = True

    blog_posts = db.blog_posts.find().sort("date", pymongo.DESCENDING)

    # Retrieve comments for each blog post
    post_comments = []
    for post in blog_posts:
        comments_for_post = comments.find({"post_id": post["_id"]})
        post['comments'] = list(comments_for_post)
        post_comments.append(post)

    return render_template('post.html', posts=True, title="AdiAvi Posts", blog_posts=post_comments, username=username, is_admin=is_admin, posted=posted)

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    incorrectCreds = ''
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = userdb.find_one({"username": username})
        
        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            return redirect(url_for("home"))
        else:
            incorrectCreds = True

    return render_template('login.html', nav5=True, title="Login", incorrectCreds=incorrectCreds)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))
    emailSent = False
    verification_error = False
    userExists = ''
    if request.method == "POST":
        username = request.form['username']
        password5 = request.form['password']
        email = request.form['email']

        existing_user = userdb.find_one({"username": username})
        existing_email = userdb.find_one({"email" : email})

        if existing_user or existing_email:
            userExists = True
        else:
            userExists = False
            characters = string.ascii_letters + string.digits + string.punctuation
            random_string = ''.join(random.choice('0123456789') for _ in range(5))

            sender_email = "aviplayz247@gmail.com"
            receiver_email = email
            password = "zywl phmk okxh fkyh"
            subject = "User Verification"
            message = f"Code: {random_string}"

            msg = MIMEText(message)
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = subject

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, msg.as_string())
                emailSent = True

                # Store the random string in the session
                session['random_string'] = random_string
                session['username1'] = username
                session['password1'] = password5
                session['email1'] = email
                # Redirect to the verification page
                return redirect(url_for('verify_email'))
            except Exception as e:
                print(f"Error: {e}")

    return render_template('register.html', regBar=True, emailSent=emailSent, verification_error=verification_error, title="Register", userExists=userExists)

@app.route('/verify', methods=['POST', 'GET'])
def verify_email():
    verification_error = False

    if request.method == 'POST':
        entered_verification_code = request.form['verification_code']
        random_string = session.get('random_string')
        if entered_verification_code != random_string:
            verification_error = True
        else:
            username = session['username1']
            password = session['password1']
            email = session['email1']
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    
            user = {"username": username, "password": hashed_password, "email": email}
            userdb.insert_one(user)
            return redirect(url_for("login"))

    return render_template('verify.html', verification_error=verification_error, title="Verification")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add_comment', methods=['POST'])
def add_comment():
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"]
            post_id = request.form['post_id']
            comment_text = request.form['comment']
   
            comments.insert_one({
                "post_id": ObjectId(post_id),
                "author": username,
                "comment": comment_text,
                "date": datetime.now().isoformat()
            })
   
    return redirect(request.referrer)

@app.route('/delete_post/<post_id>')
def delete_post(post_id):
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user and user.get("admin"):
            # Delete the post from the database
            blogposts.delete_one({"_id": ObjectId(post_id)})

    return redirect(url_for("post"))

@app.route('/about')
def about():
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            if user:
                username = user["username"]
    return render_template('about.html', username=username,about1=True, title="About Us")


@app.route('/post/<post_id>')
def view_post(post_id):
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            if user:
                username = user["username"]
    post = blogposts.find_one({"_id": ObjectId(post_id)})
    post_title = post["title"]
    
    user_has_liked_post = False  # Initialize to False
    
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            liked_posts = user.get("liked_posts", [])
            if post_id in liked_posts:
                user_has_liked_post = True
    
    if post:
        return render_template('view_post.html', post=post, posts=True, title=post_title, user_has_liked_post=user_has_liked_post, username=username)
    else:
        return "Post not found", 404


@app.route('/like_post/<post_id>', methods=['POST'])
def like_post(post_id):
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            # Check if the user has already liked this post to prevent multiple likes
            liked_posts = user.get("liked_posts", [])
            if post_id not in liked_posts:
                # Update the post's likes count in the database
                blogposts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes": 1}})
                # Add the post_id to the user's list of liked posts
                liked_posts.append(post_id)
                userdb.update_one({"_id": user["_id"]}, {"$set": {"liked_posts": liked_posts}})
    return redirect(url_for("view_post", post_id=post_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
