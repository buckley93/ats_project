import React from 'react';


function Landing({ onLogin, onRegister }) {
  return (
    <div className="container d-flex flex-column justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
      <div className="card shadow p-4" style={{ maxWidth: 400, width: '100%' }}>
        <h1 className="mb-3 text-center">Welcome to the ATS Project</h1>
        <p className="text-center">Please choose an option:</p>
        <div className="d-flex justify-content-center gap-3 mt-3">
          <button className="btn btn-primary px-4" onClick={onLogin}>Login</button>
          <button className="btn btn-outline-primary px-4" onClick={onRegister}>Register</button>
        </div>
      </div>
    </div>
  );
}

export default Landing;
