# Base image with Spark
FROM bitnami/spark:latest

# Set environment variables for Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
USER root
ENV PATH="${JAVA_HOME}/bin:${PATH}"
# Ensure apt lists and cache are cleaned and directories exist
RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/lib/apt/lists/partial \
    && apt-get update -y \
    && apt-get install -y \
    openjdk-17-jdk-headless \
    curl \
    vim \
    libpq-dev \
    && apt-get clean

# Install Python and required libraries
RUN apt-get update && apt-get install -y python3 python3-pip

# Install necessary Python libraries
COPY kafka-server/requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Set the working directory
WORKDIR /app

# Copy the Kafka consumer script
COPY kafka-server/spark-worker.py /app/spark-worker.py

# Command to run the Spark consumer job
CMD ["python3", "/app/spark-worker.py"]
