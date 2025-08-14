# LIMS System
This repository contains a professional Laboratory Information Management System (LIMS) built using the Django framework. The application provides a robust and scalable solution for managing laboratory data, samples, and workflows.

# 📝 Features
Sample Management: Track samples from intake to disposal, with detailed information on type, origin, and status.

User and Role Management: Define different user roles with specific permissions to ensure data security and integrity.

Workflow Automation: Manage and track laboratory processes and experimental workflows.

Data Reporting: Generate comprehensive reports on laboratory activities and results.

Scalable Architecture: Built on Django, a reliable and secure framework, ready for production use.

# ⚙️ Prerequisites
Before you begin, ensure you have the following software installed on your machine:

Git: For cloning the repository.

Docker & Docker CLI: To build and run the application and its database in separate containers.

# 🚀 Getting Started
Follow these steps to get the LIMS application running on your local machine using Docker.

## 1. Clone the Repository
Clone the project from GitHub and navigate into the project directory.

```Bash

git clone https://github.com/Meet2197/LIMS-system.git
cd LIMS-system
```

## 2. Configure the Database
The application uses PostgreSQL as its database. You will run it in a separate Docker container.

First, start a new PostgreSQL container. We'll use a container named lims-db and set the database name, user, and password using environment variables.

```Bash

docker run --name lims-db \
-e POSTGRES_DB=lims_db \
-e POSTGRES_USER=lims_user \
-e POSTGRES_PASSWORD=lims_password \
-p 5432:5432 \
-d postgres:13
```

This command starts a PostgreSQL 13 container in detached mode (-d), mapping its port 5432 to the same port on your host machine.

## 3. Update Django Settings
The Django backend needs to be configured to connect to the PostgreSQL database container. Navigate to LIMS/settings.py and modify the DATABASES setting to match the credentials you used above.

```Bash
 LIMS/settings.py
```
... (other settings) ...

```Bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lims_db',
        'USER': 'lims_user',
        'PASSWORD': 'lims_password',
        'HOST': 'lims-db', # This is the Docker container name
        'PORT': '5432',
    }
}
```
... (rest of the file) ...
Note on Frontend: This is a Django application, which means the frontend (HTML templates, CSS, and JavaScript) is served by the backend. There is no direct database connection from the frontend files themselves, as this is a fundamental design principle for web security. All data requests are handled through the Django backend.

## 4. Build and Run the Backend
Now, build the Docker image for the Django application and run it. The Dockerfile in this repository handles all the necessary setup, including installing dependencies from requirements.txt.

Build the Docker image with a tag, for example, lims-backend:

```Bash
docker build -t lims-backend .
```
After the image is built, run the container and link it to the database container using the --link flag.


```Bash
docker run --name lims-backend \
--link lims-db:db \
-p 8000:8000 \
-d lims-backend
```

The --link lims-db:db command creates an alias db inside the lims-backend container that points to the lims-db container. This is crucial for the Django application to find and connect to the database.

## 5. Run Migrations and Create a Superuser
With both the database and backend running, you can now set up the database schema and create an administrative user. You will use docker exec to run commands inside the lims-backend container.

Run database migrations:

```Bash

docker exec lims-backend python manage.py makemigrations
docker exec lims-backend python manage.py migrate
```

Create an administrative superuser:

``` Bash
docker exec -it lims-backend python manage.py createsuperuser
```
Follow the prompts to enter a username, email, and password.


The LIMS application should now be fully operational. You can access it at http://localhost:8000 in your web browser.

# 📂 Project Structure

/: The root directory containing the Dockerfile and this README.md file.

LIMS/: The main Django project directory. Contains settings.py, urls.py, and other core project configuration files.

app/: The Django application code. This is where you'll find models, views, templates, and other application-specific logic.

requirements.txt: A list of all Python dependencies required by the project.

.env.example: A template for environment variables used by the application.