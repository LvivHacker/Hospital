import React, {useState, useEffect, useContext} from "react";
import "./Modal.css"; // Import custom styles
import { UserContext } from "../../context/UserContext";


const Modal = ({
  active,
  handleModal,
  doctorData,
  selectedEntity,
  handleSave
}) => {
    const [token, userRole,,userId,] = useContext(UserContext);
    const [name, setName] = useState(selectedEntity ? selectedEntity.name : '');
    const [surname, setSurname] = useState(selectedEntity ? selectedEntity.surname : '');
    const [email, setEmail] = useState(selectedEntity ? selectedEntity.email : '');
    const [username, setUsername] = useState(selectedEntity ? selectedEntity.username : '');
    const [role,setRole] = useState(selectedEntity ? selectedEntity.role : 'patient');
    const [status,setStatus] = useState(selectedEntity ? selectedEntity.status: false);
    const [patients,setPatients] = useState(null);
    const [doctors,setDoctors] = useState(doctorData);


  // Existing states for appointment functionality
  const [selectedDoctor, setSelectedDoctor] = useState("");
  const [scheduledDate, setScheduledDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState("");

  useEffect(() => {
     if (role === 'patient') {
        fetch('http://localhost:8000/users', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        }})
        .then(response => response.json())
        .then(data => {
          const patientsList = data.filter(user => user.role === 'patient');
          setPatients(patientsList);
          console.log(patientsList);
        })
        .catch(error => alert(`Error fetching trainers: ${error.message}`));
     }else{
         fetch('http://localhost:8000/users', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        }})
        .then(response => response.json())
        .then(data => {
          const doctorsList = data.filter(user => user.role === 'doctor');
          setDoctors(doctorsList);
          console.log(doctorsList);
        })
        .catch(error => alert(`Error fetching trainers: ${error.message}`));
     }
  }, [token]);
  
  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    if (name === '') {
      alert('Name is required');
      return;
    }
    if (surname === '') {
      alert('Surname is required');
      return;
    }
    if (username === '') {
      alert('Username is required');
      return;
    }
    if (email === '') {
      alert('Email is required');
      return;
    }
    if (status === '') {
      alert('Status is required');
      return;
    }
    const requestOptions = {
      method: selectedEntity?.id ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
          name,
          surname,
          email,
          username,
          password: selectedEntity.password,
          role,
          status,
      }),
    };
    const url = selectedEntity?.id
      ? `http://localhost:8000/user/${selectedEntity.id}`
      : 'http://localhost:8000/user';
    try {
      const response = await fetch(url, requestOptions);
      if (!response.ok) {
        const error = await response.json();
        alert("Failed to update: " + (error.detail || error));
      } else {
        const updatedEntity = await response.json();
        alert("Details updated successfully!");
        handleSave(updatedEntity); // Call parent callback to update state
        handleModal(); // Close modal
      }
    } catch (error) {
      console.error("Error updating details:", error);
      alert("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Existing handleSubmit logic for requesting appointments
  const handleAppointmentSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    if (!selectedDoctor || !scheduledDate) {
      alert("Please select a doctor and a valid date.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/patients/${userId}/appointments/${selectedDoctor}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
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
        handleModal(); // Close modal
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
        {/* Existing appointment functionality */}
        {role === "patient" && !selectedEntity && (
          <form className="modal-form" onSubmit={handleAppointmentSubmit}>
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
                {doctors &&
                  doctors.map((doctor) => (
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
        )}
                {/* New editing functionality */}
                {selectedEntity && (
          <form className="modal-form" onSubmit={handleEditSubmit}>
            <h2>Edit {role === "doctor" ? "Doctor" : "Patient"} Details</h2>
            <div className="form-group">
              <label>Name *</label>
              <input
                type="text"
                name="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Surname *</label>
              <input
                type="text"
                name="surname"
                value={surname}
                onChange={(e) => setSurname(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                name="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            {role === "doctor" && (
              <div className="form-group">
                <label>Status *</label>
                <select
                  name="status"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  required
                >
                  <option value="" disabled>
                    Choose status
                  </option>
                  <option value="confirmed">Confirmed</option>
                  <option value="unconfirmed">Unconfirmed</option>
                </select>
              </div>
            )}
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
        )}
      </div>
    </div>
  );
};

export default Modal;