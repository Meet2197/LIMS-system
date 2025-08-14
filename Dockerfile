# Stage 1: Build dependencies
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies, specifically for SQLite3
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker's build cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.9-slim

WORKDIR /app

# Create a non-root user and group
RUN groupadd -r django && useradd -r -g django django

# Copy dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Set user to run the application
USER django

# Define the command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
