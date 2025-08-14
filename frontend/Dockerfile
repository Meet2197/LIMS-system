# Use Node 20 LTS
FROM node:20-slim

WORKDIR /app

# Copy frontend files
COPY . /app

# Install dependencies
RUN npm install

# Expose frontend port
EXPOSE 3000

# Start frontend directly
CMD ["npm", "start"]
