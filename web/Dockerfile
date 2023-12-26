# Use the official Node.js 18 image as a base
FROM node:18

# Install Python 3.10 and pip3
RUN apt-get update && apt-get -y upgrade && apt-get install -y python3.10
RUN apt-get install -y python3-pip && apt install -y ffmpeg

# Set the working directory to /app
WORKDIR /web

# Copy the package.json and package-lock.json files to the container
COPY package*.json ./

# Copy the rest of the application files to the container
COPY . .

# Install the Python dependencies
RUN pip3 install --break-system-packages -r requirements.txt

RUN npm install -g npm@9.7.1

# Set the PORT environment variable
ENV PORT 8080

# Expose the port
EXPOSE 8080

# Install the Node.js dependencies
RUN npm install

# Start the application
CMD ["npm", "start"]