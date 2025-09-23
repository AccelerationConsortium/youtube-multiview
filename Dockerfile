# Dockerfile for Hugging Face Spaces Docker deployment
FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements-gradio.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements-gradio.txt

# Copy application files
COPY gradio_app.py .
COPY streams.json* ./

# Expose port
EXPOSE 7860

# Set environment variables for HF Spaces
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run the application
CMD ["python", "gradio_app.py"]