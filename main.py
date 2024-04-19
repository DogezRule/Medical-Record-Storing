from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Define paths for CSV files
USERS_CSV = 'users.csv'
MEDICAL_INFO_CSV = 'medical_info.csv'


# Function to create CSV files if they don't exist
def create_csv_files():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='') as csvfile:
            fieldnames = ['id', 'username', 'password']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    
    if not os.path.exists(MEDICAL_INFO_CSV):
        with open(MEDICAL_INFO_CSV, 'w', newline='') as csvfile:
            fieldnames = ['id', 'user_id', 'name', 'age', 'blood_type', 'allergies']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

# Function to authenticate user
def authenticate_user(username, password):
    with open(USERS_CSV, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return row
    return None

# Function to add user to the CSV file
def add_user(username, password):
    with open(USERS_CSV, 'a', newline='') as csvfile:
        fieldnames = ['id', 'username', 'password']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'id': get_next_id(USERS_CSV), 'username': username, 'password': password})

# Function to add medical record to the CSV file
def add_medical_record(user_id, name, age, blood_type, allergies):
    with open(MEDICAL_INFO_CSV, 'a', newline='') as csvfile:
        fieldnames = ['id', 'user_id', 'name', 'age', 'blood_type', 'allergies']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'id': get_next_id(MEDICAL_INFO_CSV), 'user_id': user_id, 'name': name, 'age': age, 'blood_type': blood_type, 'allergies': allergies})


# Function to update medical record in the CSV file
def update_medical_record(record_id, name, age, blood_type, allergies):
    rows = []
    with open(MEDICAL_INFO_CSV, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['id'] == record_id:
                row['name'] = name
                row['age'] = age
                row['blood_type'] = blood_type
                row['allergies'] = allergies
            rows.append(row)
    with open(MEDICAL_INFO_CSV, 'w', newline='') as csvfile:
        fieldnames = ['id', 'user_id', 'name', 'age', 'blood_type', 'allergies']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# Function to retrieve medical record from the CSV file
def get_medical_record(user_id):
    with open(MEDICAL_INFO_CSV, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] == user_id:
                return row
    return None

def get_next_id(csv_file):
    try:
        with open(csv_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            max_id = 0
            if any(reader):
                max_id = max(int(row['id']) for row in reader)
        return max_id + 1
    except FileNotFoundError:
        return 1




# Main route to handle login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
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
        update_medical_record(record['id'], name, age, blood_type, allergies)
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
    create_csv_files()
    app.run(debug=True)
