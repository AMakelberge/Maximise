# Use an official Ubuntu 20.04 LTS image as the base
FROM ubuntu:20.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update apt-get and install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    # Install Maxima from the Ubuntu repositories.
    # Note: The version available here may not be 5.47.0.
    maxima \
    # Install Python 3 and pip
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy your requirements file first (for better layer caching)
COPY requirements.txt /app/

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copy the rest of your application code
COPY . /app

# Expose the port Heroku will use. (Heroku sets the PORT env variable.)
EXPOSE 5000

# Set the entrypoint to run your app using gunicorn with the GeventWebSocketWorker.
CMD ["gunicorn", "app:app", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "--bind", "0.0.0.0:$PORT"]