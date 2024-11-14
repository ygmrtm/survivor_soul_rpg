# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables for Python and Flask
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set a working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Define the command to run the application with a production-ready WSGI server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]