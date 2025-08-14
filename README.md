LIMS Full Stack Ready (with full CRUD)

Run locally:
1. Install Python deps: pip install -r requirements.txt
2. Start app: python app.py
3. Open http://localhost:5000/login.html
 - Default login: admin / password
 - You can create users via Users form after login.

Docker:
docker build -t lims-app .
docker run -p 5000:5000 lims-app
