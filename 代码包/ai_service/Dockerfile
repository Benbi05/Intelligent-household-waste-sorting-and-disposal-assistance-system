FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Recognition service on 8081, LLM service on 8083
EXPOSE 8081 8083

# Default: start recognition service
CMD ["python", "-m", "ai_service.recognition.app"]
