from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Kết nối Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

# Route để thêm bệnh nhân
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')

        patient_data = {
            "full_name": full_name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "address": address,
            "phone_number": phone_number,
            "email": email
        }
        
        # Lưu bệnh nhân vào Firestore và lấy ID
        patient_ref = db.collection('patients').add(patient_data)
        patient_id = patient_ref.id  # Lấy ID của bệnh nhân vừa tạo

        return redirect(url_for('index'))

    return render_template('add_patient.html')

# Route để thêm bác sĩ
@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        specialization = request.form.get('specialization')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        years_of_experience = request.form.get('years_of_experience')

        doctor_data = {
            "full_name": full_name,
            "specialization": specialization,
            "phone_number": phone_number,
            "email": email,
            "years_of_experience": int(years_of_experience)
        }
        
        # Lưu bác sĩ vào Firestore và lấy ID
        doctor_ref = db.collection('doctors').add(doctor_data)
        doctor_id = doctor_ref.id  # Lấy ID của bác sĩ vừa tạo

        return redirect(url_for('index'))

    return render_template('add_doctor.html')

# Route để thêm cuộc hẹn
@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    # Lấy danh sách bệnh nhân và bác sĩ từ Firestore
    patients_ref = db.collection('patients').stream()
    doctors_ref = db.collection('doctors').stream()

    # Tạo danh sách bệnh nhân
    patients = [{"id": patient.id, **patient.to_dict()} for patient in patients_ref]
    # Tạo danh sách bác sĩ
    doctors = [{"id": doctor.id, **doctor.to_dict()} for doctor in doctors_ref]

    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        reason = request.form.get('reason')

        if not all([patient_id, doctor_id, appointment_date, reason]):
            return "Please provide all required fields."

        try:
            # Convert appointment_date from string to datetime object
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            return "Invalid date format. Please use 'YYYY-MM-DDTHH:MM'"

        # Prepare the data to insert into Firestore
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_date": appointment_date.strftime('%Y-%m-%d %H:%M'),  # Convert to string
            "reason": reason,
            "status": "pending"
        }

        # Add appointment data to Firestore
        db.collection('appointments').add(appointment_data)
        return redirect(url_for('index'))

    return render_template('add_appointment.html', patients=patients, doctors=doctors)


# Route để tạo báo cáo
@app.route('/report')
def report():
    appointments_ref = db.collection('appointments')
    patients_ref = db.collection('patients')
    doctors_ref = db.collection('doctors')

    appointments = appointments_ref.stream()
    report = []

    for appointment in appointments:
        appointment_data = appointment.to_dict()
        patient_doc = patients_ref.document(appointment_data['patient_id']).get()
        doctor_doc = doctors_ref.document(appointment_data['doctor_id']).get()

        patient = patient_doc.to_dict() if patient_doc.exists else None
        doctor = doctor_doc.to_dict() if doctor_doc.exists else None

        if patient and doctor:
            report.append({
                "patient_name": patient['full_name'],
                "birthday": patient['date_of_birth'],
                "gender": patient['gender'],
                "address": patient['address'],
                "doctor_name": doctor['full_name'],
                "reason": appointment_data['reason'],
                "date": appointment_data['appointment_date']
            })

    return render_template('report.html', report=report)

if __name__ == '__main__':
    app.run(debug=True)
