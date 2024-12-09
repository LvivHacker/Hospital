import React, { useState, useEffect } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { jwtDecode } from 'jwt-decode'

const RequestUpdatePage = () => {
  const navigate = useNavigate();
  const { id: meetingId } = useParams(); // Meeting ID from the URL params
  const { state } = useLocation(); // Retrieve the data passed via navigate
  const token = state?.token; // Extract token from state

  const [updatedDate, setUpdatedDate] = useState("");
  const [recordDescription, setRecordDescription] = useState("");
  const [medicalRecordId, setMedicalRecordId] = useState("");

  const user = jwtDecode(token);

  useEffect(() => {
    if (!token) {
      alert("You must be logged in to access this page.");
      navigate("/home");
    }
  }, [token, navigate]);

  const handleUpdateAppointment = async () => {
    try {
      const response = await fetch(`http://localhost:8000/meetings/${meetingId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ scheduled_date: updatedDate }),
      });

      if (response.ok) {
        alert("Appointment updated successfully!");
        navigate("/home")
      } else {
        const errorDetails = await response.json();
        console.error("Error updating appointment:", errorDetails);
        alert("Failed to update appointment.");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error updating appointment.");
    }
  };

  const handleCreateMedicalRecord = async () => {
    try {
      const response = await fetch(`http://localhost:8000/meetings/${meetingId}/records`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ description: recordDescription }),
      });

      if (response.ok) {
        const data = await response.json();
        setMedicalRecordId(data.id);
        alert("Medical record created successfully!");
      } else {
        const errorDetails = await response.json();
        console.error("Error creating medical record:", errorDetails);
        alert("Failed to create medical record.");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error creating medical record.");
    }
  };

  return (
    <div>
      <h1>Update Request</h1>

      {/* Update Appointment */}
      <section>
        <h2>Update Appointment</h2>
        <input
          type="datetime-local"
          value={updatedDate}
          onChange={(e) => setUpdatedDate(e.target.value)}
        />
        <button onClick={handleUpdateAppointment}>Update Appointment</button>
      </section>

      {/* Create Medical Record */}
      {user.role === "doctor" && (
        <section>
          <h2>Create Medical Record</h2>
          <textarea
            value={recordDescription}
            onChange={(e) => setRecordDescription(e.target.value)}
            placeholder="Enter record description"
          />
          <button onClick={handleCreateMedicalRecord}>Create Record</button>
        </section>
      )}
    </div>
  );
};

export default RequestUpdatePage;
