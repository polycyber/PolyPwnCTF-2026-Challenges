# Use a lightweight Python image
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn

# Copy the API code
COPY main.py .

# Expose the port
EXPOSE 8000

# Start the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]