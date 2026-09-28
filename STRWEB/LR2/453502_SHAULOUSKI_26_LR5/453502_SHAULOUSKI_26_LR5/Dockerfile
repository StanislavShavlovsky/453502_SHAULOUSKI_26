# ==========================================
# STAGE 1: Builder (Compile dependencies)
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Prevent Python from writing pyc files to disc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Build wheels for application requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# STAGE 2: Final Runtime Environment
# ==========================================
FROM python:3.10-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Install only runtime shared libraries (libpq for PostgreSQL communication)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Copy application source code base
COPY . /app/

# Create a non-privileged system user for secure application execution
RUN useradd -u 8888 django-user && chown -R django-user:django-user /app
USER django-user

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]