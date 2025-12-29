# Use an official Python runtime as a base image
FROM python:slim

# Add a /app volume
# VOLUME ["/usr/src/app"] # /subito

# Set the working directory #rem
WORKDIR /app

# Copy all files from source to relative path (workdir)
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask Port
EXPOSE 5000

# Set the command to run the script
CMD ["python", "app.py"]
