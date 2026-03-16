FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-worker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy crawler code
COPY crawler.py .
COPY extract_training_data.py .
COPY runpod_handler.py .

# RunPod serverless entry point
ENTRYPOINT ["python", "-u", "runpod_handler.py"]
