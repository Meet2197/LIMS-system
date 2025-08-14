
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');

loginForm.addEventListener('submit', async function(e){
  e.preventDefault();
  const username = this.username.value;
  const password = this.password.value;
  
  // Added console log to see what the client is sending
  console.log('Attempting to log in with:', { username, password });

  try {
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
      // Get the error message from the backend response
      const errorData = await res.json();
      loginError.textContent = errorData.msg || 'Invalid credentials';
      // Added a more detailed console log for failed responses
      console.error('Login failed:', res.status, errorData.msg);
    }
  } catch (error) {
    // Catch any network or other errors and log them
    console.error('Network or other login error:', error);
    loginError.textContent = 'An error occurred. Please check your network connection or try again.';
  }
});
