# Set localhost for migrations
$env:DB_HOST = "localhost"

# Run migrations
Write-Host "Running database migrations..."
alembic revision --autogenerate -m "init"
alembic upgrade head

# Start Docker
Write-Host "Starting Docker containers..."
docker-compose up --build