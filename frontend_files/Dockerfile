# Use lightweight official Python runtime base image
FROM python:3.10-slim

# Set container working directory
WORKDIR /app

# Copy frontend requirements file to container first to leverage Docker layer caching
COPY requirements.txt .

# Install the necessary python libraries for streamlit frontend
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend application scripts
COPY app.py .

# Expose port 8501 (Streamlit's default port)
EXPOSE 8501

# Execute Streamlit app when container launches
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
