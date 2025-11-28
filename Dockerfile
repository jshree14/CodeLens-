# Multi-language code execution environment
FROM python:3.11-slim

# Install all compilers and runtimes
RUN apt-get update && apt-get install -y \
    default-jdk \
    nodejs \
    npm \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend code
COPY backend/ ./backend/

# Install Python dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Set working directory to backend
WORKDIR /app/backend

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
