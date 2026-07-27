# Use an official lightweight Python runtime optimized for server deployments
FROM python:3.11-slim

# Set system-level configurations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for data processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependency blueprint first to leverage Docker's caching layer
COPY requirements.txt .

# Install Python packages cleanly without caching temporary data
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your actual script code into the container image
COPY ClickUpDB.py .

# Expose the standard Streamlit runtime port
EXPOSE 8501

# Add a health check to let the server monitor if the dashboard is running smoothly
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Automatically launch the dashboard on container startup
ENTRYPOINT ["python", "-m", "streamlit", "run", "ClickUpDB.py", "--server.port=8501", "--server.address=0.0.0.0"]