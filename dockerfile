# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

#copy aux files
COPY searches.tracked .
#COPY telegram_api_credentials .
COPY /templates/index.html .

# Copy the requirements file first (to leverage Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY subito-searcher.py .
COPY app.py .

# Set the command to run the script
CMD ["python", "app.py"]
