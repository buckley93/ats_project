import React from 'react';


function Navbar({ onDashboard, onProfile, onLogout }) {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
      <div className="container-fluid">
        <span className="navbar-brand">ATS Dashboard</span>
        <div>
          <button className="btn btn-light me-2" onClick={onDashboard}>Dashboard</button>
          <button className="btn btn-light me-2" onClick={onProfile}>Profile</button>
          <button className="btn btn-outline-light" onClick={onLogout}>Logout</button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
