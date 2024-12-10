import React, { useContext, useState } from "react";
import { UserContext } from "../../context/UserContext";
import { useNavigate } from "react-router-dom";
import Modal from "./Modal";
import "./Home.css";

const HomePage = () => {
  const [token, userRole, userName, userId] = useContext(UserContext);

  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [requests, setRequests] = useState([]);
  const [medicalRecords, setMedicalRecords] = useState([]);

  const [showPatients, setShowPatients] = useState(false);
  const [showDoctors, setShowDoctors] = useState(false);
  const [showRequests, setShowRequests] = useState(false);
  const [showMedicalRecords, setShowMedicalRecords] = useState(false);

  const [modalType, setModalType] = useState(null);
  const [modalData, setModalData] = useState(null);
  const [isModalActive, setIsModalActive] = useState(false);
  const navigate = useNavigate();

  //################################################################################
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

  const fetchPatients= async () => {
    try {
      const response = await fetch("http://localhost:8000/patients", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setPatients(data);
        setShowPatients(true); // Show doctors list after fetching data
      } else {
        console.error("Failed to fetch doctors list.");
      }
    } catch (error) {
      console.error("Error fetching doctors:", error);
    }
  };

  //################################################################################
  const fetchPatientRequests = async () => {
    try {
      const response = await fetch("http://localhost:8000/patient_requests", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setRequests(data);
        setShowRequests(true); // Show requests after fetching
      } else {
        console.error("Failed to fetch requests.");
      }
    } catch (error) {
      console.error("Error fetching requests:", error);
    }
  };

  const fetchDoctorRequests = async () => {
    try {
      const response = await fetch("http://localhost:8000/doctor_requests", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setRequests(data);
        setShowRequests(true); // Show requests after fetching
        setShowMedicalRecords(false)
      } else {
        console.error("Failed to fetch requests.");
      }
    } catch (error) {
      console.error("Error fetching requests:", error);
    }
  };

  //################################################################################
  const handleDoctorsListClick = () => {
    if (!token) {
      navigate("http://localhost:3000/");
    } else {
      fetchDoctors();
      setShowPatients(false); // Hide the patients list
      setShowRequests(false); // Hide the requests list
    }
  };

  const handlePatientsListClick = () => {
    if (!token) {
      navigate("http://localhost:3000/");
    } else {
      fetchPatients();
      setShowDoctors(false); // Hide the patients list
    }
  };

  //################################################################################
  const handleMakeRequest = () => {
    if (!doctors.length) {
      fetchDoctors(); // Fetch doctors only if the list is empty
    }
    setIsModalActive(true); // Show modal
  };

  const handlePatientRequests = () => {
    if (!token) {
      navigate("http://localhost:3000/");
    } else {
      fetchPatientRequests();
      setShowDoctors(false); // Hide the doctors list
    }
  };
  
  const handleDoctorRequests = () => {
    if (!token) {
      navigate("http://localhost:3000/");
    } else {
      fetchDoctorRequests();
    }
  };

    //################################################################################
  const handleDelete = async (meetingId) => {
    try {
      const response = await fetch(`http://localhost:8000/meetings/${meetingId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (response.ok) {
        // Remove the deleted request from the state
        setRequests((prevRequests) => prevRequests.filter((req) => req.id !== meetingId));
        console.log(`Meeting ${meetingId} deleted successfully.`);
      } else {
        const errorData = await response.json();
        console.error(`Failed to delete meeting: ${errorData.detail}`);
      }
    } catch (error) {
      console.error("Error deleting meeting:", error);
    }
  };

  const handleDoctorDelete = async (doctorId) => {
    try {
      const response = await fetch(`http://localhost:8000/user/${doctorId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (response.ok) {
        // Remove the deleted request from the state
        setDoctors((prevDoctors) => prevDoctors.filter((doc) => doc.id !== doctorId));
        console.log(`Doctor ${doctorId} deleted successfully.`);
      } else {
        const errorData = await response.json();
        console.error(`Failed to delete doctor: ${errorData.detail}`);
      }
    } catch (error) {
      console.error("Error deleting meeting:", error);
    }
  };

  const handlePatientDelete = async (patientId) => {
    try {
      const response = await fetch(`http://localhost:8000/user/${patientId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (response.ok) {
        // Remove the deleted request from the state
        setPatients((prevPatients) => prevPatients.filter((pat) => pat.id !== patientId));
        console.log(`Patient ${patientId} deleted successfully.`);
      } else {
        const errorData = await response.json();
        console.error(`Failed to delete patient: ${errorData.detail}`);
      }
    } catch (error) {
      console.error("Error deleting meeting:", error);
    }
  };

  const handleConfirmDoctor = async (doctorId) => {
    try {
      const response = await fetch(`http://localhost:8000/doctors/${doctorId}/confirm`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        alert("Doctor confirmed successfully.");
        setDoctors((prevDoctors) =>
          prevDoctors.map((doctor) =>
            doctor.id === doctorId ? { ...doctor, is_confirmed: true } : doctor
          )
        );
      } else {
        alert("Failed to confirm doctor.");
        const errorDetails = await response.json();
        console.error("Error details:", errorDetails);
      }
    } catch (error) {
      console.error("Error confirming doctor:", error);
    }
  };
  

  const handleUpdate = async (type, id) => {
    const pathMap = {
      patient: `/update/patient/${id}`,
      doctor: `/update/doctor/${id}`,
      request: `/update/request/${id}`,
      record: `/update/record/${id}`,
    };
  
    navigate(pathMap[type], { state: { token } });
  };
  
  //################################################################################

  const handleConfirmRequest = async (meetingId, status) => {
    try {
      console.log(status)
      const response = await fetch(`http://localhost:8000/meetings/${meetingId}/${status}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (response.ok) {
        alert(status === 2 ? "Meeting confirmed!" : "Meeting rejected.");
        // Update the local state to reflect the changes
        setRequests((prevMeetings) =>
          prevMeetings.filter((meeting) => meeting.id !== meetingId) // Remove confirmed/rejected meeting
        );
        fetchDoctorRequests();
      } else {
        const errorDetails = await response.json();
        console.error("Error details:", errorDetails);
        alert("Failed to update meeting status.");
      }
    } catch (error) {
      console.error("Error updating meeting status:", error);
    }
  };

  const fetchMedicalRecords = async () => {
    try {
      const response = await fetch("http://localhost:8000/medical_records", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMedicalRecords(data);
        setShowMedicalRecords(true); // Show the medical records list
        // setShowDoctors(false);
        // setShowPatients(false);
        setShowRequests(false);
      } else {
        console.error("Failed to fetch medical records.");
      }
    } catch (error) {
      console.error("Error fetching medical records:", error);
    }
  };

  const handleDeleteMedicalRecord = async (recordId) => {
    try {
      const response = await fetch(`http://localhost:8000/medical_records/${recordId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (response.ok) {
        setMedicalRecords((prev) => prev.filter((record) => record.id !== recordId));
        alert("Medical record deleted successfully.");
      } else {
        alert("Failed to delete medical record.");
      }
    } catch (error) {
      console.error("Error deleting medical record:", error);
    }
  };

  const openDetailsModal = (data) => {
    setModalType("viewDetails");
    setModalData(data);
    setIsModalActive(true);
  };

  //################################################################################
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
            <button 
              onClick={handlePatientRequests}
              style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Requests List
            </button>
          </>
        )}
        {userRole === "doctor" && (
          <>
            <button 
              onClick={handleDoctorRequests}
              style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Requests List
            </button>
            <button 
              // onClick={handleMedicalRecords}
              onClick={fetchMedicalRecords}
              style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Medical Records
            </button>
          </>
        )}
        {userRole === "admin" && (
          <>
            <button 
              onClick={handleDoctorsListClick} 
              style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Doctors List
            </button>
            <button 
              onClick={handlePatientsListClick} 
              style={{ padding: "10px 20px", backgroundColor: "#007BFF", color: "#fff", border: "none", borderRadius: "5px" }}>
              Patients List
            </button>
          </>
        )}
      </div>

      {/* Doctors List */}
      {showDoctors && doctors.length > 0 && (
        <div className="requests-container">
        {doctors.map((doctor) => (
          <div className="request-card" key={doctor.id}>
            <h2>Doctor {doctor.id}</h2>
            <p>
              <strong>Name:</strong> {doctor.name}
            </p>
            <p>
              <strong>Surname:</strong> {doctor.surname}
            </p>
            <p>
              <strong>Email:</strong> {doctor.email}
            </p>
            <p>
              <strong>Status:</strong> {doctor.is_confirmed}
            </p>
            {userRole === "admin" && (
              <div className="card-buttons">
                <button className="update-btn" onClick={() => handleUpdate(doctor.role, doctor.id)}>
                  Update
                </button>
                <button className="delete-btn" onClick={() => handleDoctorDelete(doctor.id)}>
                  Delete
                </button>
                <button className="confirm-btn" onClick={() => handleConfirmDoctor(doctor.id)}>
                  Confirm
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      
      )}

      {/* Message if no doctors are found */}
      {showDoctors && doctors.length === 0 && (
        <div style={{ marginTop: "20px", color: "red" }}>
          <h2>No Doctors Found</h2>
        </div>
      )}

      {/* Patients List */}
      {showPatients && patients.length > 0 && (
        <div className="requests-container">
        {patients.map((patient) => (
          <div className="request-card" key={patient.id}>
            <h2>Patient {patient.id}</h2>
            <p>
              <strong>Name:</strong> {patient.name}
            </p>
            <p>
              <strong>Surname:</strong> {patient.surname}
            </p>
            <p>
              <strong>Email:</strong> {patient.email}
            </p>
            {userRole === "admin" && (
              <div className="card-buttons">
                <button className="update-btn" onClick={() => handleUpdate(patient.role, patient.id)}>
                  Update
                </button>
                <button className="delete-btn" onClick={() => handlePatientDelete(patient.id)}>
                  Delete
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      
      )}
      
      {/* Message if no doctors are found */}
      {showPatients && patients.length === 0 && (
        <div style={{ marginTop: "20px", color: "red" }}>
          <h2>No Patients Found</h2>
        </div>
      )}

      {/* Requests List */}
      {showRequests && requests.length > 0 && (
        <div className="requests-container">
          {requests.map((request) => (
            <div className="request-card" key={request.id}>
              <h2>Request {request.id}</h2>
              <p>
                <strong>Patient:</strong> {request.patient_id}
              </p>
              <p>
                <strong>Doctor:</strong> {request.doctor_id}
              </p>
              <p>
                <strong>Date:</strong> {request.scheduled_date}
              </p>
              <p>
                <strong>Status:</strong> {request.status}
              </p>
              <button 
                className="view-details-btn" 
                onClick={() => openDetailsModal(request)}
              >
                View Details
              </button>
              {userRole === "patient" | userRole === "doctor" ? (
                <div className="card-buttons">
                  {/* Show "Update" and "Delete" only if the request is not rejected */}
                  {request.status !== "Reject" && (
                    <>
                      <button className="update-btn" onClick={() => handleUpdate("request", request.id)}>
                        Update
                      </button>
                      <button className="delete-btn" onClick={() => handleDelete(request.id)}>
                        Delete
                      </button>
                    </>
                  )}
                  {/* Doctor-specific actions */}
                  {userRole === "doctor" && (
                    <select 
                      name="status" 
                      value={request.status || 0} // Default to 0 if status is not set
                      onChange={(e) => handleConfirmRequest(request.id, parseInt(e.target.value))}
                    >
                      <option value={0}>Select Status</option>
                      <option value={1}>Reject</option>
                      <option value={2}>Confirmed</option>
                    </select>
                  )}
                </div>
              ) : null}
            </div>
          ))}
        </div>
      )}

      {showRequests && requests.length === 0 && (
        <div style={{ marginTop: "20px", color: "red" }}>
          <h2>No Requests Found</h2>
        </div>
      )}


      {/* Medical Records List */}
      {showMedicalRecords && medicalRecords.length > 0 && (
        <div className="requests-container">
          {medicalRecords.map((record) => (
            <div className="request-card" key={record.id}>
              <h2>Medical Record {record.id}</h2>
              <p>
                <strong>Meeting:</strong> {record.meeting_id}
              </p>
              <p>
                <strong>Description:</strong> {record.description}
              </p>
              <p>
                <strong>Created At:</strong> {new Date(record.created_at).toLocaleString()}
              </p>
              <div className="card-buttons">
                <button
                  className="update-btn"
                  onClick={() => handleUpdate("record", record.id)}
                >
                  Update
                </button>
                <button
                  className="delete-btn"
                  onClick={() => handleDeleteMedicalRecord(record.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}


      {showMedicalRecords && medicalRecords.length === 0 && (
        <div style={{ marginTop: "20px", color: "red" }}>
          <h2>No Medical Records Found</h2>
        </div>
      )}

      {isModalActive && (
        <Modal
          active={isModalActive}
          handleModal={() => setIsModalActive(false)}
          modalType={modalType}
          modalData={modalData}
          token={token}
          doctors={doctors}
          patientId={userId}
          role={userRole}
        />
      )}
    </div>
  );
};

export default HomePage;

