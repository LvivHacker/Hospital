import React, { useState, useEffect } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

const RecordsUpdatePage = () => {
  const navigate = useNavigate();
  const { id: medicalRecordId } = useParams(); // Medical Record ID from the URL params
  const { state } = useLocation(); // Retrieve the data passed via navigate
  const token = state?.token; // Extract token from state

  const [recordDescription, setRecordDescription] = useState("");
  const [medicines, setMedicines] = useState([]); // List of medicines
  const [selectedMedicine, setSelectedMedicine] = useState(null); // Selected medicine for actions
  const [medicineName, setMedicineName] = useState("");
  const [medicineDosage, setMedicineDosage] = useState("");
  const [medicineFrequency, setMedicineFrequency] = useState("");

  useEffect(() => {
    if (!token) {
      alert("You must be logged in to access this page.");
      navigate("/home");
      return;
    }

    // Fetch medical record details, including medicines
    const fetchMedicalRecordDetails = async () => {
      try {
        const response = await fetch(`http://localhost:8000/medical_records/${medicalRecordId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setRecordDescription(data.description);
          setMedicines(data.medicines || []);
        } else {
          console.error("Failed to fetch medical record details.");
        }
      } catch (error) {
        console.error("Error fetching medical record details:", error);
      }
    };

    fetchMedicalRecordDetails();
  }, [token, navigate, medicalRecordId]);

  const handleUpdateMedicalRecord = async () => {
    try {
      const response = await fetch(`http://localhost:8000/medical_records/${medicalRecordId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ description: recordDescription }),
      });

      if (response.ok) {
        alert("Medical record updated successfully!");
      } else {
        const errorDetails = await response.json();
        console.error("Error updating medical record:", errorDetails);
        alert("Failed to update medical record.");
      }
    } catch (error) {
      console.error("Error updating medical record:", error);
      alert("Error updating medical record.");
    }
  };

  const handleSelectMedicine = (medicineId) => {
    const selected = medicines.find((medicine) => medicine.id === medicineId);
    setSelectedMedicine(selected);
    setMedicineName(selected?.name || "");
    setMedicineDosage(selected?.dosage || "");
    setMedicineFrequency(selected?.frequency || "");
  };

  const handleAddOrUpdateMedicine = async () => {
    if (!medicineName || !medicineDosage || !medicineFrequency) {
      alert("Please fill in all fields for the medicine.");
      return;
    }
  
    const url = selectedMedicine
      ? `http://localhost:8000/medicines/${selectedMedicine.id}`
      : `http://localhost:8000/medical_records/${medicalRecordId}/medicines`;
    const method = selectedMedicine ? "PUT" : "POST";
  
    const medicineUpdatePayload = {
      id: selectedMedicine?.id || undefined, // Include ID only for PUT requests
      medical_record_id: medicalRecordId, // Always include medical record ID
      name: medicineName,
      dosage: parseFloat(medicineDosage), // Ensure dosage is a number
      frequency: medicineFrequency,
    };
  
    try {
      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(medicineUpdatePayload),
      });
  
      if (response.ok) {
        alert(selectedMedicine ? "Medicine updated successfully!" : "Medicine added successfully!");
        setMedicineName("");
        setMedicineDosage("");
        setMedicineFrequency("");
        setSelectedMedicine(null);
  
        // Refresh medicines list
        const updatedRecord = await response.json();
        setMedicines(updatedRecord.medicines);
      } else {
        const errorDetails = await response.json();
        console.error("Error saving medicine:", errorDetails);
        alert("Failed to save medicine.");
      }
    } catch (error) {
      console.error("Error saving medicine:", error);
      alert("Error saving medicine.");
    }
  };  

  const handleDeleteMedicine = async () => {
    if (!selectedMedicine) {
      alert("Please select a medicine to delete.");
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/medicines/${selectedMedicine.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        alert("Medicine deleted successfully!");
        setMedicines(medicines.filter((medicine) => medicine.id !== selectedMedicine.id));
        setSelectedMedicine(null);
        setMedicineName("");
        setMedicineDosage("");
        setMedicineFrequency("");
      } else {
        const errorDetails = await response.json();
        console.error("Error deleting medicine:", errorDetails);
        alert("Failed to delete medicine.");
      }
    } catch (error) {
      console.error("Error deleting medicine:", error);
      alert("Error deleting medicine.");
    }
  };

  return (
    <div>
      {/* Update Medical Record */}
      <section>
        <h2>Update Medical Record</h2>
        <textarea
          value={recordDescription}
          onChange={(e) => setRecordDescription(e.target.value)}
          placeholder="Enter record description"
          rows="4"
          cols="50"
        />
        <button onClick={handleUpdateMedicalRecord}>Save</button>
      </section>

      {/* Add or Update Medication */}
      <section>
        <h2>{selectedMedicine ? "Edit Medicine" : "Add Medicine"}</h2>
        <select
          value={selectedMedicine?.id || ""}
          onChange={(e) => handleSelectMedicine(parseInt(e.target.value))}
        >
          <option value="" disabled>
            Select a Medicine
          </option>
          {medicines.map((medicine) => (
            <option key={medicine.id} value={medicine.id}>
              {medicine.name} - {medicine.dosage} - {medicine.frequency}
            </option>
          ))}
        </select>
        <input
          type="text"
          value={medicineName}
          onChange={(e) => setMedicineName(e.target.value)}
          placeholder="Medicine Name"
        />
        <input
          type="text"
          value={medicineDosage}
          onChange={(e) => setMedicineDosage(e.target.value)}
          placeholder="Dosage"
        />
        <input
          type="text"
          value={medicineFrequency}
          onChange={(e) => setMedicineFrequency(e.target.value)}
          placeholder="Frequency"
        />
        <button onClick={handleAddOrUpdateMedicine}>
          {selectedMedicine ? "Update Medicine" : "Add Medicine"}
        </button>
        {selectedMedicine && <button onClick={handleDeleteMedicine}>Delete Medicine</button>}
      </section>
    </div>
  );
};

export default RecordsUpdatePage;
