import React, { useState, useContext } from "react";
import './Auth.css';
import { useNavigate } from "react-router-dom";
import { UserContext } from "../../context/UserContext"

const SignIn = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [,,,,setToken] = useContext(UserContext);
  const navigate = useNavigate();

  const submitLogin = async () => {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: username,
        password: password,
      }),
    };

    const response = await fetch("http://localhost:8000/token", requestOptions);
    const data = await response.json();

    if (!response.ok) {
      setErrorMessage(data.detail, "error");
    } else {
      setToken(data.access_token);
      localStorage.setItem("token", data.access_token);
      navigate("/home")
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    submitLogin();
  };

  return (
    <div className="auth-container">
      <h2>Sign In</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username:</label>
          <input
            name="username"
            placeholder="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            name="password"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Sign In</button>
        <div className="switch-auth">
          Don't have an account? <a href="/signup">Signup</a>
        </div>
      </form>
      {errorMessage && <p className="error">{errorMessage}</p>}
    </div>
  );
};

export default SignIn;