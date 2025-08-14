# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite3 (should already be in Python, but ensure CLI available)
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Expose backend port
EXPOSE 5000

# Run database migrations and seed
CMD ["bash", "-c", "python db_manage.py && python app.py"]
