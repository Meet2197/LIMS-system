# Use a slim Python image to keep the final image size small.
FROM python:3.9-slim

# Set the working directory inside the container.
WORKDIR /app/backend

# Install build dependencies for SQLite3.
# The `libsqlite3-dev` package is required to compile the Python sqlite3 module.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
# The context is ./backend, so this is the correct path.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the backend port
EXPOSE 5000

# Set the command to run the Flask application
CMD ["python", "app.py"]
