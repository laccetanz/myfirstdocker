# Use an official Python runtime as a base image
FROM python:3.11-slim

# Add a /app volume
# VOLUME ["/app"]

# Set the working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask Port
EXPOSE 5000

# Set the command to run the script
CMD ["python", "app.py"]
