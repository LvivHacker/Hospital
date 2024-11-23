import React, { useContext, useState, useEffect } from "react";
import { UserContext } from "../../context/UserContext";
import { useNavigate } from "react-router-dom";

const Header = ({ title }) => {
  const [token, , , , setToken] = useContext(UserContext);
  const [remainingTime, setRemainingTime] = useState(null);
  const navigate = useNavigate();

  // Decode the token to get the expiration time
  const decodeToken = (token) => {
    try {
      const payloadBase64 = token.split(".")[1];
      const decodedPayload = JSON.parse(atob(payloadBase64));
      return decodedPayload.exp ? decodedPayload.exp * 1000 : null; // Convert exp to ms
    } catch (error) {
      console.error("Failed to decode token:", error);
      return null;
    }
  };

  useEffect(() => {
    let intervalId;

    const updateRemainingTime = () => {
      const expTime = decodeToken(token);
      if (expTime) {
        const currentTime = Date.now();
        const timeLeft = expTime - currentTime;
        if (timeLeft > 0) {
          setRemainingTime(timeLeft);
        } else {
          handleLogout(); // Logout when token expires
        }
      } else {
        setRemainingTime(null);
      }
    };

    if (token) {
      updateRemainingTime(); // Initial calculation

      // Update every second
      intervalId = setInterval(updateRemainingTime, 1000);
    } else {
      setRemainingTime(null);
    }

    return () => clearInterval(intervalId); // Cleanup on component unmount
  }, [token]);

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem("token");
    navigate("/")
  };

  // Helper function to format time remaining in HH:MM:SS
  const formatTime = (milliseconds) => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  };

  return (
    <header>
      <div className="has-text-centered m-6">
        <h1 className="title">{title}</h1>
        {remainingTime !== null && (
          <p className="is-size-6 has-text-grey">
            Token expires in: {formatTime(remainingTime)}
          </p>
        )}
      </div>

      {/* Logout button */}
      {token ? (
        <div className="has-text-centered mb-1">
          <button className="button is-danger logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      ) : (
        <></>
      )}
    </header>
  );
};

export default Header;