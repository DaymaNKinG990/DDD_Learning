# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Make migration script executable
RUN chmod +x scripts/migrate_db.py

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Running database migrations..."\n\
uv run python scripts/migrate_db.py --action migrate --retries 5 --delay 10\n\
if [ $? -eq 0 ]; then\n\
    echo "Migrations completed successfully, starting service..."\n\
    exec uv run uvicorn main:app --host 0.0.0.0 --port 8003\n\
else\n\
    echo "Migrations failed, exiting..."\n\
    exit 1\n\
fi' > /app/start.sh && chmod +x /app/start.sh

# Run the application with migrations
CMD ["/app/start.sh"] 