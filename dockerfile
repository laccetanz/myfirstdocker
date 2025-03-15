# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

#copy aux files
#COPY searches.tracked .
#COPY telegram_api_credentials .
RUN mkdir -p /app/templates
COPY /templates/index.html /templates 

# Copy the requirements file first (to leverage Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY subito-searcher.py .
COPY app.py .

EXPOSE 5000

# Set the command to run the script
CMD ["python", "app.py"]
