const registerForm = document.getElementById('registerForm');
const registerError = document.getElementById('registerError');
const successModal = new bootstrap.Modal(document.getElementById('successModal'));

registerForm.addEventListener('submit', async function(e){
  e.preventDefault();
  registerError.textContent = '';

  const firstname = this.firstname.value;
  const lastname = this.lastname.value;
  const email = this.email.value;
  const username = this.username.value;
  const password = this.password.value;
  
  try {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ firstname, lastname, email, username, password })
    });

    const data = await res.json();
    if (res.ok) {
      successModal.show();
      // Redirect to login page after the modal is closed
      document.getElementById('successModal').addEventListener('hidden.bs.modal', () => {
          window.location.href = '/login.html';
      }, { once: true });
    } else {
      registerError.textContent = data.msg || 'Registration failed';
      console.error('Registration failed:', res.status, data.msg);
    }
  } catch (error) {
    console.error('Network or other registration error:', error);
    registerError.textContent = 'An error occurred. Please check your network connection or try again.';
  }
});
