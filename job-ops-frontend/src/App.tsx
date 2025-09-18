import React, { useState, useEffect } from 'react';
import './App.css';
import JobGrid from './JobGrid';
import Login from './Login';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string>('');

  useEffect(() => {
    // Check if user is already logged in
    const savedToken = localStorage.getItem('jwtToken');
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (jwtToken: string) => {
    setToken(jwtToken);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('jwtToken');
    setToken('');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>Job Application Tracker</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </header>
      <div className="app-content">
        <JobGrid />
      </div>
    </div>
  );
}

export default App;
