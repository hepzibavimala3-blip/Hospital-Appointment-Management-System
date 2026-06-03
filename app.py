from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="hospital_db"
    )


@app.route("/")
def home():
    return jsonify({"message": "Backend connected to MySQL"})


@app.route("/appointments", methods=["GET"])
def get_appointments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM appointments ORDER BY id DESC")
    appointments = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(appointments)


@app.route("/appointments", methods=["POST"])
def add_appointment():
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO appointments
        (patientName, phone, doctorName, department, date, time, reason, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data["patientName"],
        data["phone"],
        data["doctorName"],
        data["department"],
        data["date"],
        data["time"],
        data.get("reason", ""),
        "Scheduled"
    )

    cursor.execute(sql, values)
    conn.commit()

    new_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "id": new_id,
        "patientName": data["patientName"],
        "phone": data["phone"],
        "doctorName": data["doctorName"],
        "department": data["department"],
        "date": data["date"],
        "time": data["time"],
        "reason": data.get("reason", ""),
        "status": "Scheduled"
    }), 201


@app.route("/appointments/<int:appointment_id>", methods=["PATCH"])
def update_appointment(appointment_id):
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE appointments SET status = %s WHERE id = %s",
        (data["status"], appointment_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Appointment updated"})


@app.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Appointment deleted"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
