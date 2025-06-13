from flask import Flask, request, render_template, redirect, flash, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os
import cv2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import base64

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)

class visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    reasonforvisit = db.Column(db.String(1000), nullable=False)
    personofintrest = db.Column(db.String(100), nullable=False)
    noofvisits = db.Column(db.Integer, nullable=False)
    photo = db.Column(db.LargeBinary, nullable=True)

class status(db.Model):
    visiters = db.Column(db.Integer, primary_key=True)
    timeentry = db.Column(db.String(100), nullable=False)
    timeexit = db.Column(db.String(100), nullable=True)
    date = db.Column(db.String(100), nullable=False)
    entryexit = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.LargeBinary, nullable=True)
    visitorid = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
    location = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    job = db.Column(db.String(100), nullable=False)

admins = [
    {
        "username": os.getenv("ADMIN1_USERNAME"),
        "password": generate_password_hash(os.getenv("ADMIN1_PASSWORD")),
        "email": os.getenv("ADMIN1_EMAIL"),
        "phone": int(os.getenv("ADMIN1_PHONE")),
        "location": os.getenv("location")
    },
    {
        "username": os.getenv("ADMIN2_USERNAME"),
        "password": generate_password_hash(os.getenv("ADMIN2_PASSWORD")),
        "email": os.getenv("ADMIN2_EMAIL"),
        "phone": int(os.getenv("ADMIN2_PHONE")),
        "location": os.getenv("location")
    }
]

@app.route('/')
def visitorform():
    if not session.get('photo_taken'):
        session['photo_taken'] = 0
    return render_template("index.html", phototaken=session['photo_taken'])

@app.route('/takephoto', methods=["POST"])
def takephoto():
    video = cv2.VideoCapture(0)
    ret, frame = video.read()
    video.release()
    cv2.destroyAllWindows()
    if not ret:
        flash("Camera error", "danger")
        return redirect('/')
    _, buffer = cv2.imencode('.jpg', frame)
    image = buffer.tobytes()
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    temp_folder = os.path.join('static', 'temp')
    os.makedirs(temp_folder, exist_ok=True)
    filepath = os.path.join(temp_folder, filename)
    with open(filepath, 'wb') as f:
        f.write(image)
    session['photo_filename'] = filename
    session['photo_taken'] = 1
    return redirect(url_for("visitorform"))

@app.route('/submitform', methods=["POST"])
def submitform():
    session['photo_taken'] = 0
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    phoneno = request.form["phoneno"]
    company = request.form["company"]
    location = request.form["Branch"]
    reasonforvisit = request.form["reason"]
    poi = request.form["poi"]
    filename = session.get('photo_filename')
    if not filename:
        flash("No photo found. Please take a photo.", "danger")
        return redirect('/')
    filepath = os.path.join('static', 'temp', filename)
    if not os.path.exists(filepath):
        flash("Photo file is missing. Please retake the photo.", "danger")
        return redirect('/')
    with open(filepath, 'rb') as f:
        photo_data = f.read()
    os.remove(filepath)
    session.pop('photo_filename', None)

    existing_visitor = visitor.query.filter_by(phone=phoneno).first()
    now = datetime.now()
    time_now = now.strftime('%H:%M:%S')
    date_now = now.strftime('%Y-%m-%d')

    if existing_visitor:
        existing_visitor.noofvisits += 1
        existing_visitor.reasonforvisit = reasonforvisit
        existing_visitor.personofintrest = poi
        existing_visitor.location = location
        existing_visitor.photo = photo_data

        # Check previous status
        last_status = status.query.filter_by(visitorid=existing_visitor.id).order_by(status.visiters.desc()).first()
        if last_status and last_status.entryexit == 'IN' and not last_status.timeexit:
            last_status.timeexit = time_now
            last_status.entryexit = 'OUT'

        db.session.add(status(visitorid=existing_visitor.id, timeentry=time_now,
                              date=date_now, entryexit='IN', photo=photo_data))

    else:
        newvisitor = visitor(name=firstname, lastname=lastname, phone=phoneno, company=company, location=location,
                             reasonforvisit=reasonforvisit, personofintrest=poi, noofvisits=1, photo=photo_data)
        db.session.add(newvisitor)
        db.session.flush()
        db.session.add(status(visitorid=newvisitor.id, timeentry=time_now,
                              date=date_now, entryexit='IN', photo=photo_data))

    db.session.commit()
    return redirect('/')

@app.route('/resetbutton', methods=['POST'])
def resetbutton():
    session['photo_taken'] = 0
    return redirect('/')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone")
        password = request.form.get("password")
        user = User.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Login successful", "success")
            return redirect(url_for("viewer"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("firstname")
        password = request.form.get("password")
        phone = request.form.get("phone")
        email = request.form.get("email")
        location = request.form.get("location")
        role = request.form.get("role")
        job = request.form.get("job")

        if User.query.filter((User.phone == phone) | (User.email == email) | (User.username == username)).first():
            flash("User already exists", "danger")
        else:
            user = User(username=username, password=generate_password_hash(password), phone=phone,
                        email=email, location=location, role=role, job=job)
            db.session.add(user)
            db.session.commit()
            flash("Signup successful. You can now login.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route('/viewer')
def viewer():
    if session.get('role') not in ['viewer', 'guard']:
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))
    return render_template("viewer.html")

@app.route('/api/live_visitors')
def live_visitors_api():
    active_statuses = status.query.filter_by(entryexit='IN').all()
    output = []
    for s in active_statuses:
        v = visitor.query.get(s.visitorid)
        if v:
            output.append({
                'id': v.id,
                'name': v.name,
                'lastname': v.lastname,
                'phone': v.phone,
                'company': v.company,
                'photo': base64.b64encode(v.photo).decode('utf-8') if v.photo else '',
                'timeentry': s.timeentry,
                'entryexit': s.entryexit
            })
    return jsonify(output)

@app.route('/mark_exit/<int:id>', methods=["POST"])
def mark_exit(id):
    stat = status.query.filter_by(visitorid=id, entryexit='IN').order_by(status.visiters.desc()).first()
    if stat:
        stat.timeexit = datetime.now().strftime('%H:%M:%S')
        stat.entryexit = 'OUT'
        db.session.commit()
    return redirect(url_for("viewer"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        for admin_data in admins:
            if not User.query.filter_by(username=admin_data['username']).first():
                db.session.add(User(**admin_data, role='admin', job='ceo'))
        db.session.commit()
    app.run(debug=True, host="0.0.0.0", port=8000)
