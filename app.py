from flask import Flask, request, jsonify, send_file

from flask_cors import CORS

import xml.etree.ElementTree as ET

from datetime import datetime

import io

import base64

import numpy as np

import models

import face_recognition_utils


app = Flask(__name__)

CORS(app)


# Initialize database

models.init_db()


# Team info

TEAM_MEMBERS = [

    "Team Hii_tech"

]


@app.route("/api/admin/login", methods=["POST"])

def admin_login():

    data = request.json

    username = data.get("username")

    password = data.get("password")

    if models.verify_admin(username, password):

        return jsonify({"message": "Login successful"})

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/students", methods=["GET"])

def get_students():

    students = models.get_students()

    return jsonify(students)


@app.route("/api/students", methods=["POST"])

def add_student():

    data = request.json

    name = data.get("name")

    roll_no = data.get("roll_no")

    face_image = data.get("face_image")  # base64

    face_encoding = face_recognition_utils.encode_face(face_image) if face_image else None

    if not name or not roll_no:

        return jsonify({"error": "Name and roll number required"}), 400

    try:

        student_id = models.add_student(name, roll_no, face_encoding)

        return jsonify({"message": "Student added", "id": student_id})

    except Exception as e:

        return jsonify({"error": str(e)}), 500


@app.route("/api/students/<int:student_id>", methods=["DELETE"])

def remove_student(student_id):

    models.remove_student(student_id)

    return jsonify({"message": "Student removed"})


@app.route("/api/verify/gate", methods=["POST"])

def verify_gate():

    data = request.json

    face_image = data.get("face_image")

    if not face_image:

        return jsonify({"error": "Face image required"}), 400

    students = models.get_students()

    known_encodings = []

    student_ids = []

    for student in students:

        if student[3]:  # face_encoding

            known_encodings.append(np.frombuffer(student[3], dtype=np.float64))

            student_ids.append(student[0])

    if not known_encodings:

        return jsonify({"error": "No registered faces"}), 400

    match_index = face_recognition_utils.recognize_face(face_image, known_encodings)

    if match_index is not None:

        student_id = student_ids[match_index]

        models.mark_attendance(student_id, "Gate", "gate")

        return jsonify({"message": "Gate verification successful", "student_id": student_id})

    return jsonify({"error": "Face not recognized"}), 400


@app.route("/api/verify/classroom", methods=["POST"])

def verify_classroom():

    data = request.json

    face_image = data.get("face_image")

    subject = data.get("subject")

    if not face_image or not subject:

        return jsonify({"error": "Face image and subject required"}), 400

    students = models.get_students()

    known_encodings = []

    student_ids = []

    for student in students:

        if student[3]:  # face_encoding

            known_encodings.append(np.frombuffer(student[3], dtype=np.float64))

            student_ids.append(student[0])

    if not known_encodings:

        return jsonify({"error": "No registered faces"}), 400

    match_index = face_recognition_utils.recognize_face(face_image, known_encodings)

    if match_index is not None:

        student_id = student_ids[match_index]

        models.mark_attendance(student_id, subject, "classroom")

        return jsonify({"message": "Classroom verification successful", "student_id": student_id})

    return jsonify({"error": "Face not recognized"}), 400


@app.route("/api/attendance", methods=["GET"])

def get_attendance():

    attendance = models.get_attendance()

    return jsonify(attendance)


@app.route("/api/attendance/export", methods=["GET"])

def export_attendance():

    attendance = models.get_attendance()

    root = ET.Element("Attendance")

    for record in attendance:

        entry = ET.SubElement(root, "Entry")

        ET.SubElement(entry, "Name").text = record[0]

        ET.SubElement(entry, "RollNo").text = record[1]

        ET.SubElement(entry, "Subject").text = record[2]

        ET.SubElement(entry, "Date").text = record[3]

        ET.SubElement(entry, "Time").text = record[4]

        ET.SubElement(entry, "VerificationType").text = record[5]

    tree = ET.ElementTree(root)

    xml_buffer = io.BytesIO()

    tree.write(xml_buffer, encoding='utf-8', xml_declaration=True)

    xml_buffer.seek(0)

    return send_file(

        xml_buffer,

        mimetype="application/xml",

        as_attachment=True,

        download_name="attendance.xml"

    )


@app.route("/api/team", methods=["GET"])

def get_team():

    return jsonify({"team": TEAM_MEMBERS})


if __name__ == "__main__":

    app.run(debug=True)


