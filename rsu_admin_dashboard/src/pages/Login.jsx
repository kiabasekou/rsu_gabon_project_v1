import React, { useState } from 'react';

export default function Login() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    const response = await fetch('http://localhost:8000/api/v1/auth/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      window.location.href = '/';
    }
  };

  return (
    <div style={{ padding: '50px', maxWidth: '400px', margin: 'auto' }}>
      <h2>RSU Gabon - Login</h2>
      <form onSubmit={handleLogin}>
        <input 
          value={username} 
          onChange={e => setUsername(e.target.value)}
          placeholder="Username"
          style={{ display: 'block', width: '100%', margin: '10px 0', padding: '10px' }}
        />
        <input 
          type="password"
          value={password} 
          onChange={e => setPassword(e.target.value)}
          placeholder="Password"
          style={{ display: 'block', width: '100%', margin: '10px 0', padding: '10px' }}
        />
        <button type="submit" style={{ padding: '10px 20px' }}>Login</button>
      </form>
    </div>
  );
}
