# Use a Node.js image to run the server
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
# This allows for a more efficient Docker cache
COPY package.json .

# Install Node.js dependencies
RUN npm install

# Copy all the files from your repository into the container's app directory
# The `.` ensures all files are copied from the context of the build
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["node", "server.js"]