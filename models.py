import sqlite3

import os

from datetime import datetime


DATABASE = 'attendance.db'


def init_db():

    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS students (

                    id INTEGER PRIMARY KEY,

                    name TEXT NOT NULL,

                    roll_no TEXT UNIQUE NOT NULL,

                    face_encoding BLOB

                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (

                    id INTEGER PRIMARY KEY,

                    student_id INTEGER,

                    subject TEXT,

                    date TEXT,

                    time TEXT,

                    verification_type TEXT,  -- 'gate' or 'classroom'

                    FOREIGN KEY (student_id) REFERENCES students (id)

                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admins (

                    id INTEGER PRIMARY KEY,

                    username TEXT UNIQUE NOT NULL,

                    password TEXT NOT NULL

                )''')

    # Insert default admin

    c.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)", ('admin', 'password'))

    conn.commit()

    conn.close()


def add_student(name, roll_no, face_encoding=None):

    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()

    c.execute("INSERT INTO students (name, roll_no, face_encoding) VALUES (?, ?, ?)",

              (name, roll_no, face_encoding))

    student_id = c.lastrowid

    conn.commit()

    conn.close()

    return student_id


def remove_student(student_id):

    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id = ?", (student_id,))

    c.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))

    conn.commit()

    conn.close()


def get_students():

    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()

    c.execute("SELECT id, name, roll_no FROM students")

    students = c.fetchall()

    conn.close()

    return students


def get_student_by_roll_no(roll_no):

    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()

    c.execute("SELECT id, name, face_encoding FROM students WHERE roll_no = ?", (roll_no,))

    student = c.fetchone()

    conn.close()

    return student


def mark_attendance(student_id, subject, verification_type):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")

    time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()

    c.execute("INSERT INTO attendance (student_id, subject, date, time, verification_type) VALUES (?, ?, ?, ?, ?)",

              (student_id, subject, date, time, verification_type))

    conn.commit()

    conn.close()


def get_attendance():

    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()

    c.execute("""

        SELECT s.name, s.roll_no, a.subject, a.date, a.time, a.verification_type

        FROM attendance a

        JOIN students s ON a.student_id = s.id

        ORDER BY a.date DESC, a.time DESC

    """)

    attendance = c.fetchall()

    conn.close()

    return attendance


def verify_admin(username, password):

    conn = sqlite3.connect(DATABASE)

    c = conn.cursor()

    c.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))

    admin = c.fetchone()

    conn.close()

    return admin is not None


