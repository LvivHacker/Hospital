import React, { useState } from "react";
import "./Modal.css"; // Import custom styles

const Modal = ({ 
  active, 
  handleModal, 
  token, 
  doctors, 
  patientId, 
  role,
  modalType, 
  modalData  
}) => {  
  const [selectedDoctor, setSelectedDoctor] = useState("");
  const [scheduledDate, setScheduledDate] = useState("");
  const [loading, setLoading] = useState(false);

  const [selectedRecordId, setSelectedRecordId] = useState(
    modalData?.medical_records?.[0]?.id || null
  );

  const selectedRecord = modalData?.medical_records?.find(
    (record) => record.id === selectedRecordId
  );

  // Get current date and time in YYYY-MM-DDTHH:mm format
  const getCurrentDateTime = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const minDateTime = getCurrentDateTime();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
  
    if (!selectedDoctor || !scheduledDate) {
      alert("Please select a doctor and a valid date.");
      setLoading(false);
      return;
    }
  
    try {
      const response = await fetch(
        `http://localhost:8000/patients/${patientId}/appointments/${selectedDoctor}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`, // Pass the JWT token
          },
          body: JSON.stringify({
            scheduled_date: scheduledDate,
          }),
        }
      );
  
      if (!response.ok) {
        const error = await response.json();
        alert("Failed to request meeting: " + (error.detail || error));
      } else {
        const data = await response.json();
        alert("Appointment requested successfully! Awaiting doctor review.");
        console.log("Appointment created:", data);
        handleModal(); // Close the modal after successful submission
      }
    } catch (error) {
      console.error("Error requesting appointment:", error);
      alert("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  if (!active) return null;

  return (
    <div className={`modal ${active && "is-active"}`}>
      <div className="modal-background" onClick={handleModal}></div>
      <div className="modal-container">
        {role === "patient" && modalType !== "viewDetails" ? (
          <form className="modal-form" onSubmit={handleSubmit}>
            <h2>Request a Meeting</h2>
            <div className="form-group">
              <label>Select Doctor *</label>
              <select
                value={selectedDoctor}
                onChange={(e) => setSelectedDoctor(e.target.value)}
                required
              >
                <option value="" disabled>
                  Choose a doctor
                </option>
                {doctors.map((doctor) => (
                  <option key={doctor.id} value={doctor.id}>
                    {doctor.name} {doctor.surname}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Scheduled Date *</label>
              <input
                type="datetime-local"
                value={scheduledDate}
                onChange={(e) => setScheduledDate(e.target.value)}
                min={minDateTime} // Restrict past dates and times
                required
              />
            </div>
            
            <footer className="modal-card-foot has-background-primary-light">
              <button
                className={`button is-primary ${loading ? "is-loading" : ""}`}
                type="submit"
                disabled={loading}
              >
                Submit
              </button>
              <button
                className="button"
                onClick={() => handleModal()}
                style={{ marginLeft: "10px" }}
              >
                Cancel
              </button>
            </footer>
          </form>
        ) : modalType === "viewDetails" && modalData ? (
          <div className="modal-content">
            <h2>Medical Record Details</h2>

            {/* Dropdown for selecting a medical record */}
            {modalData.medical_records?.length > 0 ? (
              <>
                <label htmlFor="recordSelect" style={{ marginBottom: "10px", display: "block" }}>
                  Select a Record:
                </label>
                <select
                  id="recordSelect"
                  value={selectedRecordId}
                  onChange={(e) => setSelectedRecordId(parseInt(e.target.value))}
                  style={{ marginBottom: "20px", padding: "5px", width: "100%" }}
                >
                  {modalData.medical_records.map((record) => (
                    <option key={record.id} value={record.id}>
                      {record.description} (Created: {new Date(record.created_at).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </>
            ) : (
              <p>No medical records available.</p>
            )}

            {/* Display details for the selected record */}
            {selectedRecord ? (
              <>
                <p><strong>Description:</strong> {selectedRecord.description}</p>
                <p><strong>Created At:</strong> {new Date(selectedRecord.created_at).toLocaleString()}</p>
                <h3>Prescribed Medications</h3>
                <ul>
                  {selectedRecord.medicines?.map((med, index) => (
                    <li key={index}>
                      <p><strong>Name:</strong> {med.name}</p>
                      <p><strong>Dosage:</strong> {med.dosage}</p>
                      <p><strong>Frequency:</strong> {med.frequency}</p>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p>No medical record selected.</p>
            )}
            <button className="button" onClick={handleModal}>Close</button>
          </div>
        ) : (
          <div className="modal-content">
            <p>Invalid role. Please contact support.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Modal;
