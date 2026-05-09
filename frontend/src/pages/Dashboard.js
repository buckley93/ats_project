import React, { useState } from 'react';
import { deleteAccount } from '../api/user';

function Dashboard() {
  const [error, setError] = useState('');

  const handleDeleteAccount = async (e) => {
    try {
      await deleteAccount();
      setTimeout(() => {
        window.location.href = '/login';
      }, 20000); // 2 seconds delay
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Delete failed.');
      setTimeout(() => {
        window.location.href = '/login';
      }, 1000); // Still redirect after showing error
    }
  };

  return (
    <div className="container mt-5">
      <div className="card shadow p-4 mx-auto" style={{ maxWidth: 600 }}>
        <h2 className="mb-3 text-center">Dashboard</h2>
        <p className="text-center">Welcome to your dashboard!</p>
        <button className="btn btn-danger w-100" onClick={handleDeleteAccount}>Delete Account</button>
        {error && <div className="alert alert-danger mt-3 p-2 text-center">{error}</div>}
      </div>
    </div>
  );
}

export default Dashboard;
