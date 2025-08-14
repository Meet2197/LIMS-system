# Use Node 20 LTS
FROM node:20-slim

# Set the working directory
WORKDIR /app

# Copy frontend files (relative to the ./frontend context)
COPY package*.json ./
# Install dependencies
RUN npm install
# Copy all other frontend files
COPY . .

# Expose frontend port
EXPOSE 3000

# Start frontend directly
CMD ["npm", "start"]
