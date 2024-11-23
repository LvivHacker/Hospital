import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import SignIn from "./components/Auth/SignIn";
import SignUp from "./components/Auth/SignUp";
import Home from "./components/Home/Home";
import Header from "./components/Shared/Header"

const App = () => {
  return (
    <Router>
      <Header title={"Hospital System"} />
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/home" element={<Home />} />
        <Route path="*" element={<Navigate to="/"/>} />
        {/* <Route path="/create-request" element={<CreateRequest />} /> */}
        {/* <Route path="/admin" element={<AdminDashboard />} /> */}
      </Routes>
    </Router>
  );
};

export default App;
