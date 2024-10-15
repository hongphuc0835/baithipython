from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from dateutil import parser

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Kết nối Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Hàm thêm bệnh nhân
def add_patients():
    patients = []
    for i in range(3):
        full_name = input(f"Enter full name for patient {i+1}: ")
        date_of_birth = input(f"Enter date of birth (YYYY-MM-DD) for patient {i+1}: ")
        gender = input(f"Enter gender for patient {i+1} (Male/Female): ")
        address = input(f"Enter address for patient {i+1}: ")
        patient_data = {
            "full_name": full_name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "address": address
        }
        patients.append(patient_data)
        db.collection('patients').add(patient_data)
    return patients

# Hàm thêm bác sĩ
def add_doctors():
    doctors = []
    for i in range(5):
        full_name = input(f"Enter full name for doctor {i+1}: ")
        specialization = input(f"Enter specialization for doctor {i+1}: ")
        phone_number = input(f"Enter phone number for doctor {i+1}: ")
        email = input(f"Enter email for doctor {i+1}: ")
        years_of_experience = int(input(f"Enter years of experience for doctor {i+1}: "))
        doctor_data = {
            "full_name": full_name,
            "specialization": specialization,
            "phone_number": phone_number,
            "email": email,
            "years_of_experience": years_of_experience
        }
        doctors.append(doctor_data)
        db.collection('doctors').add(doctor_data)
    return doctors

# Hàm thêm lịch hẹn
def add_appointments():
    appointments = []
    for i in range(3):
        patient_id = input(f"Enter patient ID for appointment {i+1}: ")
        doctor_id = input(f"Enter doctor ID for appointment {i+1}: ")
        appointment_date = input(f"Enter appointment date and time (YYYY-MM-DD HH:MM): ")
        reason = input(f"Enter reason for appointment {i+1}: ")
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_date": parser.parse(appointment_date),
            "reason": reason,
            "status": "pending"
        }
        appointments.append(appointment_data)
        db.collection('appointments').add(appointment_data)
    return appointments

# Tạo báo cáo các lịch hẹn
@app.route('/generate_report', methods=['GET'])
def generate_report():
    appointments_ref = db.collection('appointments')
    patients_ref = db.collection('patients')
    doctors_ref = db.collection('doctors')

    appointments = appointments_ref.stream()
    report = []
    for appointment in appointments:
        appointment_data = appointment.to_dict()
        patient = patients_ref.document(appointment_data['patient_id']).get().to_dict()
        doctor = doctors_ref.document(appointment_data['doctor_id']).get().to_dict()
        
        report.append({
            "patient_name": patient['full_name'],
            "birthday": patient['date_of_birth'],
            "gender": patient['gender'],
            "address": patient['address'],
            "doctor_name": doctor['full_name'],
            "reason": appointment_data.get('reason'),
            "date": appointment_data['appointment_date'].strftime('%Y-%m-%d %H:%M')
        })

    return jsonify(report), 200

# Lấy tất cả các lịch hẹn trong ngày hôm nay
@app.route('/get_today_appointments', methods=['GET'])
def get_today_appointments():
    today = datetime.now().date()
    appointments_ref = db.collection('appointments')
    patients_ref = db.collection('patients')
    doctors_ref = db.collection('doctors')

    appointments = appointments_ref.where('appointment_date', '>=', today).stream()
    today_appointments = []
    for appointment in appointments:
        appointment_data = appointment.to_dict()
        patient = patients_ref.document(appointment_data['patient_id']).get().to_dict()
        doctor = doctors_ref.document(appointment_data['doctor_id']).get().to_dict()

        today_appointments.append({
            "address": patient['address'],
            "patient_name": patient['full_name'],
            "birthday": patient['date_of_birth'],
            "gender": patient['gender'],
            "doctor_name": doctor['full_name'],
            "status": appointment_data.get('status', 'pending')
        })

    return jsonify(today_appointments), 200

# Chạy Flask server
if __name__ == "__main__":
    print("Adding patients...")
    add_patients()
    print("Adding doctors...")
    add_doctors()
    print("Adding appointments...")
    add_appointments()
    app.run(debug=True)
