# Use official Python 3.10.11 slim image
FROM python:3.10.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Run FastAPI backend using Uvicorn, binding to all interfaces
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
