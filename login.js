const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');

loginForm.addEventListener('submit', async function(e){
  e.preventDefault();
  const username = this.username.value;
  const password = this.password.value;
  
  // Log the login attempt
  console.log('Attempting to log in with:', { username, password });

  try {
    // --- CORRECTED FETCH URL ---
    // The fetch URL is now a relative path, which the proxy in app.js will handle.
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('token', data.token);
      // Redirect to the dashboard after successful login
      window.location.href = '/dashboard.html';
    } else {
      const errorData = await res.json();
      loginError.textContent = errorData.msg || 'Invalid credentials';
      console.error('Login failed:', res.status, errorData.msg);
    }
  } catch (error) {
    console.error('Network or other login error:', error);
    loginError.textContent = 'An error occurred. Please check your network connection or try again.';
  }
});