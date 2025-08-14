document.getElementById('loginForm').addEventListener('submit', async function(e){
  e.preventDefault();
  const u = this.username.value, p = this.password.value;
  const res = await fetch('/api/login', {
    method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:u,password:p})
  });
  if(res.ok){
    const data = await res.json();
    localStorage.setItem('token', data.token);
    window.location.href = '/dashboard.html';
  } else {
    document.getElementById('loginError').textContent = 'Invalid credentials';
  }
});
