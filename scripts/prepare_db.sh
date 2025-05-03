#!/bin/bash

# Set localhost for migrations (temporarily)
export DB_HOST=localhost

# Run migrations
echo "Running database migrations..."
alembic revision --autogenerate -m "init" && \
alembic upgrade head

# Start Docker with original environment
echo "Starting Docker containers..."
docker-compose up --build