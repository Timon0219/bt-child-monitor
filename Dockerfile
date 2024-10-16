# Use the official Python image from the Docker Hub
FROM python:3.12.5-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Define the entrypoint and default command
ENTRYPOINT ["python", "main.py"]
CMD ["--interval", "3600", "config.yaml"]

# docker run myimage --interval 7200 custom_config.yaml