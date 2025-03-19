# Use an official Python runtime as a base image
FROM python:slim

# Add a /app volume
# VOLUME ["/subito"]

# Set the working directory #rem
WORKDIR /usr/src/app

# Copy req files # . .
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from source to relative path
COPY . ./

# Expose Flask Port
EXPOSE 5000

# Set the command to run the script
CMD ["python", "app.py"]
