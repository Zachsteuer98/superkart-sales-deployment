# Use lightweight official Python runtime base image
FROM python:3.10-slim

# Set container working directory
WORKDIR /app

# Copy requirements file first to optimize build caching
COPY requirements.txt .

# Install required python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy flask script and serialized champion model into workdir
COPY app.py .
COPY superkart_model.joblib .

# Expose port 7860 for Flask API network traffic
EXPOSE 7860

# Execute backend server
CMD ["python", "app.py"]
