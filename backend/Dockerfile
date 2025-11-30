FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including PostgreSQL client)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 devora && chown -R devora:devora /app
USER devora

# Expose port 4521
EXPOSE 4521

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:4521/api/ || exit 1

# Run with uvicorn on port 4521
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "4521"]
