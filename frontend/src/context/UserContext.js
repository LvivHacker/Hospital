import React, { createContext, useEffect, useState } from "react";

// Create the UserContext
export const UserContext = createContext();

// UserProvider component
export const UserProvider = (props) => {
    const [token, setToken] = useState(localStorage.getItem("token"));
    const [userRole, setUserRole] = useState(null);
    const [userName, setUserName] = useState(null);
    const [userId, setUserId] = useState(null);
    const [exp, setExp] = useState(null);

    // Decode JWT token to extract user details
    const decodeToken = (token) => {
        try {
            const payloadBase64 = token.split(".")[1];
            const decodedPayload = JSON.parse(atob(payloadBase64));
            return {
                userId: decodedPayload.id,
                userName: decodedPayload.sub,
                userRole: decodedPayload.role,
                exp: decodedPayload.exp,
            };
        } catch (error) {
            console.error("Failed to decode token:", error);
            return null;
        }
    };

    // Logout function to clear context and localStorage
    const handleLogout = () => {
        setToken(null);
        setUserRole(null);
        setUserName(null);
        setUserId(null);
        setExp(null);
        localStorage.removeItem("token");
    };

    // Verify token validity with server
    const verifyToken = async (token) => {
        try {
            const response = await fetch(`http://localhost:8000/verify-token/${token}`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setToken(data.access_token);
                localStorage.setItem("token", data.access_token);

                const decoded = decodeToken(data.access_token);
                if (decoded) {
                    setUserRole(decoded.userRole);
                    setUserName(decoded.userName);
                    setUserId(decoded.userId);
                    setExp(decoded.exp);
                }
            } else {
                handleLogout();
            }
        } catch (error) {
            console.error("Failed to verify token:", error);
            handleLogout();
        }
    };

    // Refresh token before expiration
    const refreshToken = async () => {
        try {
            const response = await fetch(`http://localhost:8000/refresh-token`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setToken(data.access_token);
                localStorage.setItem("token", data.access_token);

                const decoded = decodeToken(data.access_token);
                if (decoded) {
                    setExp(decoded.exp);
                }
            } else {
                handleLogout();
            }
        } catch (error) {
            console.error("Failed to refresh token:", error);
            handleLogout();
        }
    };

    // Effect to handle token verification and refresh
    useEffect(() => {
        if (token) {
            verifyToken(token);
        }

        const intervalId = token
            ? setInterval(() => {
                  if (exp && Date.now() >= exp * 1000 - 60 * 1000) {
                      refreshToken();
                  }
              }, 60 * 1000)
            : null;

        const handleStorageChange = (event) => {
            if (event.key === "token" && !event.newValue) {
                handleLogout();
            }
        };

        window.addEventListener("storage", handleStorageChange);

        return () => {
            clearInterval(intervalId);
            window.removeEventListener("storage", handleStorageChange);
        };
    }, [token, exp]);

    // Context Provider to pass state and functions
    return (
        <UserContext.Provider
            value={[
                token,
                userRole,
                userName,
                userId,
                setToken 
            ]}
        >
            {props.children}
        </UserContext.Provider>
    );
};
