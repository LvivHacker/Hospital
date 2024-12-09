import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const DoctorUpdate = ({ token }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [doctorData, setDoctorData] = useState({
    username: "",
    email: "",
    password: "",
    name: "",
    surname: "",
    role: "doctor"
  });

  useEffect(() => {
    const fetchDoctor = async () => {
      const response = await fetch(`http://localhost:8000/user/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setDoctorData(data);
      } else {
        alert("Failed to fetch doctor data.");
      }
    };
    fetchDoctor();
  }, [id, token]);

  const handleSave = async (e) => {
    e.preventDefault();
    const response = await fetch(`http://localhost:8000/user/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(doctorData),
    });
    if (response.ok) {
      alert("Doctor updated successfully.");
      navigate("/home"); // Redirect to the home page
    } else {
      alert("Failed to update doctor.");
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
            value={doctorData.name}
            onChange={(e) =>
              setDoctorData({ ...doctorData, name: e.target.value })
            }
          />
        </label>
        <label>
          Surname:
          <input
            type="text"
            value={doctorData.surname}
            onChange={(e) =>
                setDoctorData({ ...doctorData, surname: e.target.value })
            }
          />
        </label>
        <label>
          Username:
          <input
            type="username"
            value={doctorData.username}
            onChange={(e) =>
                setDoctorData({ ...doctorData, username: e.target.value })
            }
          />
        </label>
        <label>
          Email:
          <input
            type="email"
            value={doctorData.email}
            onChange={(e) =>
                setDoctorData({ ...doctorData, email: e.target.value })
            }
          />
        </label>
        <label>
          Password:
          <input
            type="password"
            value={doctorData.password || ""}
            onChange={(e) =>
                setDoctorData({ ...doctorData, password: e.target.value })
            }
          />
        </label>
        <button type="submit">Save</button>
      </form>
    </div>
  );
};

export default DoctorUpdate;
