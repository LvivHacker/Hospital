import React, { useContext, useState } from "react";
import { UserContext } from "../../context/UserContext";
import { useNavigate } from "react-router-dom";
import Modal from "./Modal"

const HomePage = () => {
  const [token, userRole, userName, userId] = useContext(UserContext);
  
  console.log("Token:", token);
  console.log("UserId from UserContext:", userId);
  
  const [doctors, setDoctors] = useState([]);
  const [showDoctors, setShowDoctors] = useState(false);
  const [isModalActive, setIsModalActive] = useState(false);
  const navigate = useNavigate();

  const fetchDoctors = async () => {
    try {
      const response = await fetch("http://localhost:8000/doctors", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setDoctors(data);
        setShowDoctors(true); // Show doctors list after fetching data
      } else {
        console.error("Failed to fetch doctors list.");
      }
    } catch (error) {
      console.error("Error fetching doctors:", error);
    }
  };

  const handleDoctorsListClick = () => {
    if (!token) {
      navigate("http://localhost:3000/");
    } else {
      fetchDoctors();
    }
  };

  const handleMakeRequest = () => {
    if (!doctors.length) {
      fetchDoctors(); // Fetch doctors only if the list is empty
    }
    setIsModalActive(true); // Show modal
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Welcome {userRole} {userName}</h1>
      <div style={{ display: "flex", gap: "15px", marginTop: "20px" }}>
        {userRole === "patient" && (
          <>
            <button 
              onClick={handleDoctorsListClick} 
              style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Doctors List
            </button>
            <button 
              onClick={handleMakeRequest}
              style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Make Request
            </button>
            <button style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Requests List
            </button>
          </>
        )}
        {userRole === "doctor" && (
          <>
            <button style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Requests List
            </button>
          </>
        )}
      </div>

      {/* Conditionally display doctors list */}
      {showDoctors && doctors.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h2>Doctors List</h2>
          <ul>
            {doctors.map((doctor) => (
              <li key={doctor.id}>{doctor.name}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Message if no doctors are found */}
      {showDoctors && doctors.length === 0 && (
        <div style={{ marginTop: "20px", color: "red" }}>
          <h2>No Doctors Found</h2>
        </div>
      )}

      {isModalActive && (
        <Modal
          active={isModalActive}
          handleModal={() => setIsModalActive(false)}
          token={token}
          doctors={doctors}
          patientId={userId}
        />
      )}
    </div>
    
  );
};

export default HomePage;
