import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const PatientUpdate = ({ token }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patientData, setPatientData] = useState({
    username: "",
    email: "",
    password: "",
    name: "",
    surname: "",
    role: "patient"
  });

  useEffect(() => {
    const fetchPatient = async () => {
      const response = await fetch(`http://localhost:8000/user/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setPatientData(data);
      } else {
        alert("Failed to fetch patient data.");
      }
    };
    fetchPatient();
  }, [id, token]);

  const handleSave = async (e) => {
    e.preventDefault();
    const response = await fetch(`http://localhost:8000/user/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(patientData),
    });
    if (response.ok) {
      alert("Patient updated successfully.");
      navigate("/home"); // Redirect to the home page
    } else {
      alert("Failed to update patient.");
    }
  };

  return (
    <div>
      <h1>Update Patient</h1>
      <form onSubmit={handleSave}>
        <label>
          Name:
          <input
            type="text"
            value={patientData.name}
            onChange={(e) =>
              setPatientData({ ...patientData, name: e.target.value })
            }
          />
        </label>
        <label>
          Surname:
          <input
            type="text"
            value={patientData.surname}
            onChange={(e) =>
              setPatientData({ ...patientData, surname: e.target.value })
            }
          />
        </label>
        <label>
          Username:
          <input
            type="username"
            value={patientData.username}
            onChange={(e) =>
              setPatientData({ ...patientData, username: e.target.value })
            }
          />
        </label>
        <label>
          Email:
          <input
            type="email"
            value={patientData.email}
            onChange={(e) =>
              setPatientData({ ...patientData, email: e.target.value })
            }
          />
        </label>
        <label>
          Password:
          <input
            type="password"
            value={patientData.password || ""}
            onChange={(e) =>
              setPatientData({ ...patientData, password: e.target.value })
            }
          />
        </label>
        <button type="submit">Save</button>
      </form>
    </div>
  );
};

export default PatientUpdate;
