# Laboratory Information Management System (LIMS)

A web-based Laboratory Information Management System built with a Node.js backend and a simple, responsive HTML/JavaScript frontend. This application provides a centralized platform for managing various laboratory data entities, including users, materials, plates, and analysis data.

## Features

User Authentication: Secure login system with username and password.

## Dashboard: A central dashboard with navigation to different data management sections.

Data Management: CRUD (Create, Read, Update, Delete) functionality for multiple data entities (users, materials, gels, plates, analysis, methods, proteomes).

SQLite Database: A lightweight, file-based database for persistence.

RESTful API: A well-defined API for frontend-backend communication.

Docker Support: Containerized setup for easy deployment and development environment consistency.

## Prerequisites : 

To run this project, you need to have the following software installed on your machine:

Node.js (v18.x or later)

npm (usually comes with Node.js)

Docker (optional, but highly recommended)

## Installation and Setup : 

There are two recommended ways to set up and run this project:

Method 1: Using Docker (Recommended)

Docker simplifies the setup process by handling all dependencies and environment configurations.

Clone the repository:

```bash
git clone [(https://github.com/Meet2197/LIMS-system)]
cd LIMS-system
```

Build and run the Docker containers:

```bash
docker-compose up --build
```

This command will build the Docker image, set up the container, and start both the frontend and backend servers.

Once the containers are running, the application will be available at ```bash http://localhost:3000```.

Method 2: Manual Setup

If you prefer to run the application directly on your machine, follow these steps.

Clone the repository:

```bash
git clone [https://github.com/Meet2197/LIMS-system]
cd LIMS-system
```
Install frontend dependencies:
The frontend app.js uses http-proxy-middleware.

```bash
npm install
```

This will install the necessary packages listed in package.json.

Start the backend server:
Open a new terminal window and run the backend server.

```bash
node server.js
```

The backend server will run on port 5000.

Start the frontend server:
Open another terminal window and run the frontend server.

```bash
node app.js
```

The frontend server will run on port 3000 and proxy requests to the backend on 5000.

Access the application by navigating to ```bash http://localhost:3000 ``` in your web browser.

Usage
Access the application through your web browser at ```bash http://localhost:3000 ```

Default Login Credentials:

```bash
Username: admin

Password: admin123
```

These credentials are pre-seeded into the database to allow you to log in and begin managing your lab data immediately.

# File Structure

app.js: The frontend server, which serves static files and proxies API requests.

server.js: The backend server, which handles API routes and database interactions.

login.html, dashboard.html: Core HTML files for the user interface.

package.json: Manages the Node.js project's dependencies and scripts.

database.db: The SQLite database file.

Dockerfile: Defines the Docker image for the application.

# Dependencies

express: Web framework for Node.js.

sqlite3: SQLite database driver.

bcrypt: Library for hashing passwords.

jsonwebtoken: Library for creating and verifying JSON Web Tokens (JWT).

http-proxy-middleware: Middleware for proxying HTTP requests.

# License : 

This project is licensed under the MIT License.