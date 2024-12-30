# Use Node.js as the base image
FROM node:16

# Set the working directory in the container
WORKDIR /app

# Set the environment variable to disable sourcemaps
ENV GENERATE_SOURCEMAP=false

# Copy the package.json and package-lock.json to install dependencies
COPY frontend/package.json frontend/package-lock.json ./

# Install frontend dependencies
RUN npm install

# Copy the rest of the frontend files
COPY frontend /app

# Expose the port the frontend runs on
EXPOSE 3000

# Command to start the React app
CMD ["npm", "start"]
