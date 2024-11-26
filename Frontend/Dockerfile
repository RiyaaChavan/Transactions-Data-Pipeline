# Use an Nginx image to serve static files
FROM nginx:alpine

# Set the working directory
WORKDIR /usr/share/nginx/html

# Copy your static files into the container
COPY . .

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
