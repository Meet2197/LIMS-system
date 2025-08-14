# Stage 1: Build dependencies
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies for SQLite3
# `libsqlite3-dev` is required to compile the Python `sqlite3` module.
# The `apt-get` commands are combined into a single layer for efficiency.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker's build cache.
# If this file doesn't change, Docker won't re-run this and subsequent steps.
COPY requirements.txt .

# Install Python dependencies. `pip` will use the system libraries where needed.
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.9-slim

WORKDIR /app

# Create a non-root user and group for security best practices.
RUN groupadd -r django && useradd -r -g django django

# Copy dependencies from the builder stage to the final, smaller image.
# This keeps the final image clean of build-time dependencies.
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy the rest of the application code into the image.
COPY . .

# Expose the port the Django application will run on.
EXPOSE 8000

# Set the non-root user to run the application.
USER django

# Define the command to start the Django development server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]