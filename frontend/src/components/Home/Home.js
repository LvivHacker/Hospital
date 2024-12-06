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
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [isModalActive, setIsModalActive] = useState(false);

  const [activeSection, setActiveSection] = useState(null); // Tracks active section: "patients", "doctors", or "requests"
  const navigate = useNavigate();

  const fetchData = async (endpoint, setter, successMessage) => {
    try {
      const response = await fetch(`http://localhost:8000/${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log("Patient Requests Response:", response);
      if (response.ok) {
        const data = await response.json();
        setter(data);
        console.log(successMessage);
      } else {
        console.error(`Failed to fetch ${endpoint}`);
      }
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
    }
  };

  const handleFetch = (section) => {
    if (!token) {
      navigate("http://localhost:3000/");
      return;
    }

    setActiveSection(section);
    switch (section) {
      case "patients":
        fetchData("patients", setPatients, "Patients fetched successfully.");
        break;
      case "doctors":
        fetchData("doctors", setDoctors, "Doctors fetched successfully.");
        break;
      case "patient_requests":
        fetchData("patient_requests", setRequests, "Patient requests fetched successfully.");
        break;
      case "doctor_requests":
        fetchData("doctor_requests", setRequests, "Doctor requests fetched successfully.");
        break;
      default:
        break;
    }
  };

  const handleDelete = async (endpoint, id, setter) => {
    try {
      const response = await fetch(`http://localhost:8000/${endpoint}/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        setter((prev) => prev.filter((item) => item.id !== id));
        console.log(`Deleted ${endpoint} ${id} successfully.`);
      } else {
        const errorData = await response.json();
        console.error(`Failed to delete ${endpoint}: ${errorData.detail}`);
      }
    } catch (error) {
      console.error(`Error deleting ${endpoint}:`, error);
    }
  };

  const handleEdit = (entity) => {
    setSelectedEntity(entity);
    setIsModalActive(true);
  };

  const handleSave = (updatedEntity) => {
    const { role, id } = updatedEntity;
    if (role === "doctor") {
      setDoctors((prev) => prev.map((doc) => (doc.id === id ? updatedEntity : doc)));
    } else if (role === "patient") {
      setPatients((prev) => prev.map((pat) => (pat.id === id ? updatedEntity : pat)));
    }
  };

  const renderList = (list, deleteHandler, role) => (
    <div className="requests-container">
      {list.map((item) => (
        <div className="request-card" key={item.id}>
          <h2>{`${role.charAt(0).toUpperCase() + role.slice(1)} ${item.id}`}</h2>
          <p>
            <strong>Name:</strong> {item.name}
          </p>
          <p>
            <strong>Surname:</strong> {item.surname}
          </p>
          <p>
            <strong>Email:</strong> {item.email}
          </p>
          {role === "doctor" && (
            <p>
              <strong>Status:</strong> {item.is_confirmed ? "Confirmed" : "Unconfirmed"}
            </p>
          )}
          <div className="card-buttons">
            <button className="update-btn" onClick={() => handleEdit(item)}>
              Update
            </button>
            <button className="delete-btn" onClick={() => deleteHandler(item.id)}>
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Welcome {userRole} {userName}</h1>
      <div style={{ display: "flex", gap: "15px", marginTop: "20px" }}>
        {userRole === "patient" && (
          <>
            <button onClick={() => handleFetch("doctors")}>Doctors List</button>
            <button onClick={() => setIsModalActive(true)}>Make Request</button>
            <button onClick={() => handleFetch("patient_requests")}>Requests List</button>
          </>
        )}
        {userRole === "doctor" && (
          <button onClick={() => handleFetch("doctor_requests")}>Requests List</button>
        )}
        {userRole === "admin" && (
          <>
            <button onClick={() => handleFetch("doctors")}>Doctors List</button>
            <button onClick={() => handleFetch("patients")}>Patients List</button>
          </>
        )}
      </div>

      {/* Render lists dynamically */}
      {activeSection === "doctors" && renderList(doctors, (id) => handleDelete("user", id, setDoctors), "doctor")}
      {activeSection === "patients" && renderList(patients, (id) => handleDelete("user", id, setPatients), "patient")}
      {activeSection === "requests" && renderList(requests, (id) => handleDelete("meetings", id, setRequests), "request")}

      {/* No data found message */}
      {activeSection && !(
        (activeSection === "doctors" && doctors.length) ||
        (activeSection === "patients" && patients.length) ||
        (activeSection === "requests" && requests.length)
      ) && <div style={{ marginTop: "20px", color: "red" }}><h2>No {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)} Found</h2></div>}

      {isModalActive && (
        <Modal
          active={isModalActive}
          handleModal={() => setIsModalActive(false)}
          token={token}
          doctors={doctors}
          patientId={userId}
          role={userRole}
          selectedEntity={selectedEntity}
          handleSave={handleSave}
        />
      )}
    </div>
  );
};

export default HomePage;

