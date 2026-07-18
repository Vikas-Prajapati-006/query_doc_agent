FROM python:3.10-slim

WORKDIR /app

# Security Patch: Keep system packages updated and install essential tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Layer Optimization: First install requirements to utilize cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code (excluding files explicitly blocked in .dockerignore)
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run application securely without exposing credentials in command args
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]