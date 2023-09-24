from flask import Flask, render_template, request, url_for, session, redirect
from flask_socketio import SocketIO, send
from bson.objectid import ObjectId
import pymongo
import random
import string
import smtplib
from email.mime.text import MIMEText
from flask_bcrypt import Bcrypt

client = pymongo.MongoClient("mongodb+srv://avyuktballari:AZMKXJeKbOWQpB46@cluster0.qk6ukw8.mongodb.net/?retryWrites=true&w=majority")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'edftyguhiu5tf6guhedrftvgbyhnujidrftgyhujidrftgyhucvgbhnjugybhunjcvgbyh'
db = client.get_database('login-register')
userdb = db.users
socketio = SocketIO(app)
bcrypt = Bcrypt(app)


@app.route('/')
def home():
    username = None  
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"]  
    return render_template('index.html', home=True, username=username)

@app.route('/posts')
def post():
    username = None  
    if "user_id" in session:
        user = userdb.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"]  
    return render_template('post.html', posts=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = userdb.find_one({"username": username})
        
        if user and bcrypt.check_password_hash(user["password"], password):
    
            session["user_id"] = str(user["_id"])
            return redirect(url_for("home"))

    return render_template('login.html', nav5=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    emailSent = False
    verification_error = False

    if request.method == "POST":
        username = request.form['username']
        password5 = request.form['password']
        email = request.form['email']

        characters = string.ascii_letters + string.digits + string.punctuation
        random_string = ''.join(random.choice(characters) for _ in range(5))

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

    return render_template('register.html', regBar=True, emailSent=emailSent, verification_error=verification_error)

@app.route('/verify', methods=['POST', 'GET'])
def verify_email():
    verification_error = False

    if request.method == 'POST':
        entered_verification_code = request.form['verification_code']
        # Assuming you have stored the generated random_string in session['random_string']
        random_string = session.get('random_string')
        print(random_string)
        if entered_verification_code != random_string:
            verification_error = True
        else:
            username = session['username1']
            password = session['password1']
            email = session['email1']
            print(username, password, email)
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    
            user = {"username": username, "password": hashed_password, "email": email}
            userdb.insert_one(user)
            return redirect(url_for("login"))

    return render_template('verify.html', verification_error=verification_error)

@app.route('/logout')
def logout():
    # Clear the user's session to log them out
    session.clear()
    # Redirect the user to a login page or another page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
