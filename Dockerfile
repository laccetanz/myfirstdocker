# Use an official Python runtime as a base image
FROM python:3.10-slim

# Copia il file dei requisiti e installa tutto
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory #rem
WORKDIR /app

# Copy all files from source to relative path (workdir)
COPY . .

# Expose Flask Port
EXPOSE 5000

# Set the command to run the script
CMD ["python", "-u", "app.py"]
