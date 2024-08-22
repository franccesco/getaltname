# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in pyproject.toml
# If you have a requirements.txt, use that instead.
RUN pip install --upgrade pip
RUN pip install .

# Set the environment variable to force color output
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1

# Make sure gsan is executable globally
ENTRYPOINT ["gsan"]
