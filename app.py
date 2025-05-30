from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import os
import cv2
from dotenv import load_dotenv
import io

# Load .env file
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail config (not used here yet)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize DB and mail
db = SQLAlchemy(app)
mail = Mail(app)

# Visitor model
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
    timeentry = db.Column(db.String(100), unique = False, nullable = False)
    timeexit = db.Column(db.String(100), unique=False, nullable=False)
    date = db.Column(db.String(100), unique=False, nullable=False)
    entryexit = db.Column(db.String(100), unique = False, nullable = False)
    photo = db.Column(db.LargeBinary, nullable=True)
    visitorid = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)

class admin(db.Model):
    adminid = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique=True, nullable = False)
    password = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)

@app.route('/')
def visitorform():
    if not session.get('photo_taken'):
        session['photo_taken'] = 0

    phototaken=session['photo_taken']
    return render_template("index.html", phototaken=phototaken)

@app.route('/takephoto', methods=["GET", "POST"])
def takephoto():
    video = cv2.VideoCapture(0)
    ret, frame = video.read()
    video.release()
    cv2.destroyAllWindows()

    if not ret:
        flash("Camera error", "danger")
        return redirect('/')

    # Encode to JPEG in memory
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
    phototaken = session['photo_taken']
    return redirect(url_for("visitorform", phototaken=phototaken))

@app.route('/submitform', methods=["GET", "POST"])
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
        return redirect(url_for("visitorform", phototaken=0))
    filepath = os.path.join('static', 'temp', filename)
    if not os.path.exists(filepath):
        flash("Photo file is missing. Please retake the photo.", "danger")
        return redirect(url_for("visitorform", phototaken=0))

    with open(filepath, 'rb') as f:
        photo_data = f.read()

    os.remove(filepath)  # ✅ Clean up the temp file
    session.pop('photo_filename', None)
    existing_visitor = visitor.query.filter_by(phone=phoneno).first()
    if existing_visitor:
        existing_visitor.noofvisits += 1
        existing_visitor.reasonforvisit = reasonforvisit
        existing_visitor.personofintrest = poi
        existing_visitor.location = location
        db.session.commit()
    else:
        newvisitor = visitor(
            name=firstname,
            lastname=lastname,
            phone=phoneno,
            company=company,
            location=location,
            reasonforvisit=reasonforvisit,
            personofintrest=poi,
            noofvisits=1,
            photo=photo_data
        )
        db.session.add(newvisitor)
        db.session.commit()
    phototaken = session['photo_taken']
    return redirect(url_for("visitorform", phototaken=phototaken))

@app.route('/resetbutton', methods=['POST','GET'])
def resetbutton():
    session['photo_taken'] = 0
    phototaken = session['photo_taken']
    return redirect(url_for("visitorform", phototaken=phototaken))

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host="0.0.0.0", debug=True, port=8000)
