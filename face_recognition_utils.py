import React, { useState, useEffect } from 'react';

import axios from 'axios';

import Webcam from 'react-webcam';

import './App.css';


function App() {

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [username, setUsername] = useState('');

  const [password, setPassword] = useState('');

  const [students, setStudents] = useState([]);

  const [attendance, setAttendance] = useState([]);

  const [newStudent, setNewStudent] = useState({ name: '', rollNo: '' });

  const [verificationType, setVerificationType] = useState('gate'); // 'gate' or 'classroom'

  const [subject, setSubject] = useState('');

  const [message, setMessage] = useState('');

  const [capturing, setCapturing] = useState(false);

  const webcamRef = React.useRef(null);


  useEffect(() => {

    if (isLoggedIn) {

      fetchStudents();

      fetchAttendance();

    }

  }, [isLoggedIn]);


  const handleLogin = async () => {

    try {

      const response = await axios.post('http://localhost:5000/api/admin_login', { username, password });

      if (response.data.success) {

        setIsLoggedIn(true);

        setMessage('Login successful');

      } else {

        setMessage('Invalid credentials');

      }

    } catch (error) {

      setMessage('Login failed');

    }

  };


  const fetchStudents = async () => {

    try {

      const response = await axios.get('http://localhost:5000/api/students');

      setStudents(response.data);

    } catch (error) {

      console.error('Error fetching students:', error);

    }

  };


  const fetchAttendance = async () => {

    try {

      const response = await axios.get('http://localhost:5000/api/attendance');

      setAttendance(response.data);

    } catch (error) {

      console.error('Error fetching attendance:', error);

    }

  };


  const addStudent = async () => {

    try {

      const response = await axios.post('http://localhost:5000/api/add_student', newStudent);

      if (response.data.success) {

        setMessage('Student added successfully');

        fetchStudents();

        setNewStudent({ name: '', rollNo: '' });

      } else {

        setMessage('Failed to add student');

      }

    } catch (error) {

      setMessage('Error adding student');

    }

  };


  const removeStudent = async (rollNo) => {

    try {

      const response = await axios.post('http://localhost:5000/api/remove_student', { rollNo });

      if (response.data.success) {

        setMessage('Student removed successfully');

        fetchStudents();

      } else {

        setMessage('Failed to remove student');

      }

    } catch (error) {

      setMessage('Error removing student');

    }

  };


  const captureAndVerify = async () => {

    setCapturing(true);

    const imageSrc = webcamRef.current.getScreenshot();

    try {

      const response = await axios.post('http://localhost:5000/api/verify', {

        image: imageSrc,

        type: verificationType,

        subject: verificationType === 'classroom' ? subject : null

      });

      if (response.data.success) {

        setMessage(`Attendance marked for ${response.data.student.name} at ${verificationType}`);

        fetchAttendance();

      } else {

        setMessage('Face not recognized');

      }

    } catch (error) {

      setMessage('Verification failed');

    }

    setCapturing(false);

  };


  const exportAttendance = async () => {

    try {

      const response = await axios.get('http://localhost:5000/api/export_attendance', { responseType: 'blob' });

      const url = window.URL.createObjectURL(new Blob([response.data]));

      const link = document.createElement('a');

      link.href = url;

      link.setAttribute('download', 'attendance.xml');

      document.body.appendChild(link);

      link.click();

    } catch (error) {

      setMessage('Export failed');

    }

  };


  if (!isLoggedIn) {

    return (

      <div className="App">

        <h1>Hii_Tech A.I Attendance System</h1>

        <div className="login-form">

          <h2>Admin Login</h2>

          <input

            type="text"

            placeholder="Username"

            value={username}

            onChange={(e) => setUsername(e.target.value)}

          />

          <input

            type="password"

            placeholder="Password"

            value={password}

            onChange={(e) => setPassword(e.target.value)}

          />

          <button onClick={handleLogin}>Login</button>

          <p>{message}</p>

        </div>

      </div>

    );

  }


  return (

    <div className="App">

      <h1>Hii_Tech A.I Attendance System</h1>

      <button onClick={() => setIsLoggedIn(false)}>Logout</button>


      <div className="section">

        <h2>Student Management</h2>

        <div className="add-student">

          <input

            type="text"

            placeholder="Name"

            value={newStudent.name}

            onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })}

          />

          <input

            type="text"

            placeholder="Roll No"

            value={newStudent.rollNo}

            onChange={(e) => setNewStudent({ ...newStudent, rollNo: e.target.value })}

          />

          <button onClick={addStudent}>Add Student</button>

        </div>

        <ul>

          {students.map(student => (

            <li key={student.roll_no}>

              {student.name} ({student.roll_no})

              <button onClick={() => removeStudent(student.roll_no)}>Remove</button>

            </li>

          ))}

        </ul>

      </div>


      <div className="section">

        <h2>Face Verification</h2>

        <select value={verificationType} onChange={(e) => setVerificationType(e.target.value)}>

          <option value="gate">Gate Verification</option>

          <option value="classroom">Classroom Verification</option>

        </select>

        {verificationType === 'classroom' && (

          <input

            type="text"

            placeholder="Subject"

            value={subject}

            onChange={(e) => setSubject(e.target.value)}

          />

        )}

        <Webcam

          audio={false}

          ref={webcamRef}

          screenshotFormat="image/jpeg"

          width={320}

          height={240}

        />

        <button onClick={captureAndVerify} disabled={capturing}>

          {capturing ? 'Verifying...' : 'Capture & Verify'}

        </button>

      </div>


      <div className="section">

        <h2>Attendance Records</h2>

        <button onClick={exportAttendance}>Export to XML</button>

        <ul>

          {attendance.map(record => (

            <li key={record.id}>

              {record.student_name} - {record.subject || 'Gate'} - {record.date} {record.time}

            </li>

          ))}

        </ul>

      </div>


      <p>{message}</p>

    </div>

  );

}


export default App;


