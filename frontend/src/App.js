import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import SignIn from "./components/Auth/SignIn";
import SignUp from "./components/Auth/SignUp";
import Home from "./components/Home/Home";
import Header from "./components/Shared/Header"
import DoctorUpdate from "./components/Pages/DoctorUpdate";
import PatientUpdate from "./components/Pages/PatientUpdate";
import RequestUpdate from "./components/Pages/RequestUpdate"
import RecordsUpdate from "./components/Pages/RecordsUpdate"

const App = () => {
  return (
    <Router>
      <Header title={"Hospital System"} />
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/home" element={<Home />} />
        <Route path="/update/patient/:id" element={<PatientUpdate />} />
        <Route path="/update/doctor/:id" element={<DoctorUpdate />} />
        <Route path="/update/request/:id" element={<RequestUpdate />} />
        <Route path="/update/record/:id" element={<RecordsUpdate />} />

        <Route path="*" element={<Navigate to="/"/>} />
      </Routes>
    </Router>
  );
};

export default App;
