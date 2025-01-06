# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for MySQL client
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc && \
    apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
# COPY . .

# Expose port
EXPOSE 8000

# Set entry point
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000"]
