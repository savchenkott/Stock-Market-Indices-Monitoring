# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container to /app
WORKDIR /app

# Copy the local contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd -r -u 1001 youruser

# Set the user
USER youruser

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run main.py when the container launches
CMD ["python3", "main.py"]
