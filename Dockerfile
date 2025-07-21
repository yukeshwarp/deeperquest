FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies first for better cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the environment file and application code
COPY .env .env
COPY secmcp.py .

# Expose the port
EXPOSE 8052

# Run the app
CMD ["python", "secmcp.py"]
 