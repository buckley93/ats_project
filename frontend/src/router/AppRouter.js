import React, { useState } from 'react';

import Login from '../pages/Login';
import Register from '../pages/Register';
import Dashboard from '../pages/Dashboard';
import Profile from '../pages/Profile';
import Navbar from '../components/Navbar';
import Landing from '../pages/Landing';


function AppRouter() {
  const [page, setPage] = useState('landing');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
    setPage('dashboard');
  };
  const handleRegister = () => {
    setPage('login');
  };
  const goToProfile = () => setPage('profile');
  const goToDashboard = () => setPage('dashboard');
  const handleLogout = () => {
    setIsAuthenticated(false);
    setPage('landing');
  };

  if (!isAuthenticated) {
    if (page === 'login') {
      return <Login onLogin={handleLogin} onGoToRegister={() => setPage('register')} />;
    }
    if (page === 'register') {
      return <Register onRegister={handleRegister} onGoToLogin={() => setPage('login')} />;
    }
    // Default: Landing page
    return <Landing onLogin={() => setPage('login')} onRegister={() => setPage('register')} />;
  }

  return (
    <div>
      <Navbar onDashboard={goToDashboard} onProfile={goToProfile} onLogout={handleLogout} />
      {page === 'dashboard' && <Dashboard />}
      {page === 'profile' && <Profile />}
    </div>
  );
}

export default AppRouter;
