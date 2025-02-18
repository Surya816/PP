from flask import Flask, request, jsonify, redirect, url_for,render_template
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime


app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['PP']  # Database name
users_collection = db['users']  # Collection for users
consent_collection = db["inpatient_consent"]
medical_history_collection = db["medical_history"]
inpatients_admission_collection = db["inpatients_admission"]  # Collection name


# Routes
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/ooo')
def login_paage():
    return render_template('add-patient.html')

@app.route('/select-patient')
def select_patient():
    return render_template('select_patient.html')

@app.route('/appointments')
def inpatient_outpatient():
    return render_template('inpatient_outpatient.html')

@app.route('/in-patient')
def in_patient():
    return render_template('inpatient.html')

@app.route('/inpatient-consent-form')
def inpatient_consent_form():
    return render_template('inpatient_consent_form.html')

@app.route('/inpatient-medical-history')
def inpatient_medical_history():
    return render_template('inpatient_medical_history.html')

@app.route('/inpatient-admission')
def inpatient_admission():
    return render_template('inpatient_admission.html')

# @app.route('/inpatient-billing')
# def inpatient_billing():
#     return render_template('inpatient_exists.html')

@app.route('/inpatient-discharge')
def inpatient_discharge():
    return render_template('discharge.html')

@app.route('/inpatient-treatment')
def inpatient_treatment():
    return render_template('treatment.html')

@app.route('/inpatient-billing')
def inpatient_billing():
    return render_template('billing.html')

@app.route('/out-patient')
def outpatient():
    return render_template('outpatient.html')

@app.route('/surgeries')
def surgeries():
    return render_template('surgeries.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/special-visits')
def special_visits():
    return render_template('special_visits.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/pharmacy')
def pharmacy():
    return render_template('pharmacy.html')

@app.route('/staff-attendance')
def staffattendance():
    return render_template('staff_attendence.html')

@app.route('/inventory')
def inventory():
    return render_template(('inventory.html'))

@app.route("/submit_admission", methods=["POST"])
def submit_admission():
    data = request.form.to_dict()
    
    # Auto-generate patient ID based on timestamp
    data["patient_id"] = f"PAT-{int(datetime.utcnow().timestamp())}"
    
    # Convert date strings to proper date format
    if "dob" in data:
        data["dob"] = datetime.strptime(data["dob"], "%Y-%m-%d")
    if "admission_date" in data:
        data["admission_date"] = datetime.strptime(data["admission_date"], "%Y-%m-%d")
    
    # Insert into MongoDB
    result = inpatients_admission_collection.insert_one(data)
    
    return jsonify({"message": "Admission submitted successfully", "patient_id": data["patient_id"]}), 201


@app.route('/submit_consent', methods=['POST'])
def submit_consent():
    # Get form data
    patient_id = request.form.get('patient_id')
    full_name = request.form.get('full_name')
    procedure_details = request.form.get('procedure_details')
    consent = request.form.get('consent')  # This will be 'on' if checked
    signature = request.form.get('signature')
    date_str = request.form.get('date')  # Date as string from the form

    # Convert date string to a Date object
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Convert to datetime object
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400

    # Save the consent form data to MongoDB
    consent_data = {
        'patient_id': patient_id,
        'full_name': full_name,
        'procedure_details': procedure_details,
        'consent_given': True if consent == 'on' else False,  # Convert checkbox value to boolean
        'signature': signature,
        'date': date_obj,  # Save as Date object
        'submitted_at': datetime.utcnow()  # Add a timestamp for when the form was submitted
    }

    # Insert into MongoDB
    consent_collection.insert_one(consent_data)

    # Return a success message
    return jsonify({'message': 'Consent form submitted successfully!'}), 201

@app.route("/submit_medical_history", methods=["POST"])
def submit_medical_history():
    try:
        form_data = {
            "patient_id": request.form.get("patient_id"),
            "allergies": request.form.get("allergies"),
            "past_conditions": request.form.get("past_conditions"),
            "current_medications": request.form.get("current_medications"),
            "family_history": request.form.get("family_history"),
            "surgical_history": request.form.get("surgical_history"),
            "smoking": request.form.get("smoking"),
            "alcohol": request.form.get("alcohol")
        }

        # Insert into MongoDB
        medical_history_collection.insert_one(form_data)
        
        return jsonify({"message": "Medical history submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('pswd')

    # Find user in MongoDB
    user = users_collection.find_one({'email': email})

    if user and check_password_hash(user['password'], password):
        return jsonify({'message': 'Login successful', 'redirect': url_for('select_patient')}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401
    

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    username = data.get('txt')
    email = data.get('email')
    password = data.get('pswd')
    auth_token = data.get('auth')

    # Check if user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists'}), 400

    # Hash password
    hashed_password = generate_password_hash(password)

    # Assign role based on email
    if email == 'admin@gmail.com' and password == 'admin':
        role = 'admin'
    else:
        role = 'user'

    # Insert new user into MongoDB
    user_data = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'auth_token': auth_token,
        'role': role  # Add role field
    }
    users_collection.insert_one(user_data)

    return jsonify({'message': 'Signup successful', 'role': role}), 201

# Run the app
if __name__ == '__main__':
    app.run(debug=True,port = 5001)