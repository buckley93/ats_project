import React, { useState } from 'react';
import { register as registerApi } from '../api/auth';

function Register({ onRegister, onGoToLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const data = await registerApi(username, password);
      setSuccess(data.message || 'Registration successful!');
      setTimeout(() => {
        onRegister();
      }, 1000);
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed.');
    }
  };

  return (
    <div className="container d-flex flex-column justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
      <div className="card shadow p-4" style={{ maxWidth: 400, width: '100%' }}>
        <h2 className="mb-3 text-center">Register</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <input
              type="text"
              className="form-control"
              placeholder="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="mb-3">
            <input
              type="password"
              className="form-control"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary w-100 mb-2">Register</button>
        </form>
        <button className="btn btn-link w-100" type="button" onClick={onGoToLogin}>Already have an account? Login</button>
        {error && <div className="alert alert-danger mt-3 p-2 text-center">{error}</div>}
        {success && <div className="alert alert-success mt-3 p-2 text-center">{success}</div>}
      </div>
    </div>
  );
}

export default Register;
