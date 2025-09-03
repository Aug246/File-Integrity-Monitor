# File Integrity Monitor Docker Image
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash fimuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/fimuser/.local

# Copy application code
COPY fim/ ./fim/
COPY fim.yml .
COPY requirements.txt .

# Set PATH to include user's local bin
ENV PATH=/home/fimuser/.local/bin:$PATH

# Create necessary directories
RUN mkdir -p /var/log/fim /var/lib/fim /etc/fim && \
    chown -R fimuser:fimuser /var/log/fim /var/lib/fim /etc/fim /app

# Switch to non-root user
USER fimuser

# Create volume mount points
VOLUME ["/var/lib/fim", "/var/log/fim", "/etc/fim"]

# Set environment variables
ENV FIM_DB_PATH=/var/lib/fim/fim.db
ENV FIM_CONFIG_PATH=/etc/fim/fim.yml
ENV FIM_LOG_PATH=/var/log/fim/fim.log
ENV FIM_AGENT_ID=docker-fim-agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('$FIM_DB_PATH')" || exit 1

# Default command
CMD ["fim", "start", "--config", "/etc/fim/fim.yml", "--foreground"]
