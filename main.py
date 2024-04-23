from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ian:ian@localhost:3306/db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User and MedicalInfo models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class MedicalInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_type = db.Column(db.String(10), nullable=False)
    allergies = db.Column(db.String(255), nullable=False)
    user = db.relationship('User', backref=db.backref('medical_info', lazy=True))

# Create database tables
with app.app_context():
    db.create_all()

# Function to authenticate user
def authenticate_user(username, password):
    user = User.query.filter_by(username=username, password=password).first()
    return user

# Function to add user to the database
def add_user(username, password):
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

# Function to add medical record to the database
def add_medical_record(user_id, name, age, blood_type, allergies):
    new_record = MedicalInfo(user_id=user_id, name=name, age=age, blood_type=blood_type, allergies=allergies)
    db.session.add(new_record)
    db.session.commit()

# Function to update medical record in the database
def update_medical_record(record_id, name, age, blood_type, allergies):
    record = MedicalInfo.query.get(record_id)
    record.name = name
    record.age = age
    record.blood_type = blood_type
    record.allergies = allergies
    db.session.commit()

# Function to retrieve medical record from the database
def get_medical_record(user_id):
    record = MedicalInfo.query.filter_by(user_id=user_id).first()
    return record

# Main route to handle login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = username
            return redirect(url_for('add_record'))
        else:
            return "Invalid username or password."
    return render_template('index.html')

# Route to handle signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        add_user(username, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route to add or edit medical record
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    record = get_medical_record(user_id)
    if record:
        return redirect(url_for('view_record'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_type = request.form['blood_type']
        allergies = request.form['allergies']
        add_medical_record(user_id, name, age, blood_type, allergies)
        return redirect(url_for('view_record'))
    return render_template('add_record.html')

# Route to edit medical record
@app.route('/edit_record', methods=['GET', 'POST'])
def edit_record():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    record = get_medical_record(user_id)
    if not record:
        return redirect(url_for('add_record'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_type = request.form['blood_type']
        allergies = request.form['allergies']
        update_medical_record(record.id, name, age, blood_type, allergies)
        return redirect(url_for('view_record'))
    return render_template('edit_record.html', record=record)

# Route to view medical record
@app.route('/view_record')
def view_record():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    record = get_medical_record(user_id)
    if record:
        return render_template('medical_record.html', record=record)
    else:
        return "No medical record found for this user."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True, ssl_context='adhoc')
