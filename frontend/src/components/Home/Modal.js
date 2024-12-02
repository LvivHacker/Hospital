import React, { useState } from "react";
import "./Modal.css"; // Import custom styles

const Modal = ({ active, handleModal, token, doctors, patientId, role }) => {  
  const [selectedDoctor, setSelectedDoctor] = useState("");
  const [scheduledDate, setScheduledDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState("");

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
  

  return (
    <div className={`modal ${active && "is-active"}`}>
      <div className="modal-background" onClick={handleModal}></div>
      <div className="modal-container">
      {role === "patient" ? (
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
        ) : role === "doctor" ? (
          <form className="modal-form" onSubmit={handleSubmit}>
            <h2>Doctor Notes</h2>
            <div className="form-group">
              <label>Notes *</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                required
                rows={5}
              />
            </div>
            <footer className="modal-card-foot has-background-primary-light">
              <button
                className={`button is-primary ${loading ? "is-loading" : ""}`}
                type="submit"
                disabled={loading}
              >
                Save
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
