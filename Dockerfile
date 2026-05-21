# Mini ERPNext - Docker Container
# Python 3.12 with Tkinter support for GUI

FROM python:3.12-slim

# Install system dependencies for Tkinter and GUI support
RUN apt-get update && apt-get install -y \
    python3-tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    libxft2 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/ ./apps/
COPY controllers/ ./controllers/
COPY core/ ./core/
COPY data/ ./data/
COPY migrations/ ./migrations/
COPY modules/ ./modules/
COPY scripts/ ./scripts/
COPY ui/ ./ui/
COPY utils/ ./utils/
COPY *.py ./
COPY *.ini ./

# Create directories for persistent data
RUN mkdir -p /app/logs /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

# Entry point
CMD ["python", "run_desk.py"]
