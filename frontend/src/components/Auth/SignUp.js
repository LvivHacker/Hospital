import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const SignUp = () => {
  const [formData, setFormData] = useState({
    name: "",
    surname: "",
    username: "",
    password: "",
    email: "",
    role: "patient", // Default role
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:8000/register", formData);
      setMessage("Registration successful. You can now log in.");
      setFormData({ name: "", surname: "", username: "", password: "", email: "", role: "patient" });
      navigate("/")
    } catch (err) {
      setError("Error during registration. Please try again.");
    }
  };

  return (
    <div className="auth-container">
      <h2>Sign Up</h2>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      
      <form onSubmit={handleSubmit}>
          <label>Name</label>
          <input
            name="name"
            placeholder="Name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            required
          />

          <label>Surname</label>
          <input
            name="surname"
            placeholder="Surname"
            type="text"
            value={formData.surname}
            onChange={handleChange}
            required
          />
          
          <label>Username</label>
          <input
            name="username"
            placeholder="Username"
            type="text"
            value={formData.username}
            onChange={handleChange}
            required
          />

          <label>Email</label>
          <input
            name="email"
            type="email"
            placeholder="email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <label>Password</label>
          <input
            name="password"
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <label>Role</label>
          <select name="role" value={formData.role} onChange={handleChange}>
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
          </select>

        <button type="submit">Sign Up</button>
      </form>
    </div>
  );
};

export default SignUp;
