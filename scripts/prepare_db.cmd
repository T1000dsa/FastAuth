@echo off
:: Set localhost for migrations
set DB_HOST=localhost

:: Run migrations
echo Running database migrations...
alembic revision --autogenerate -m "init"
alembic upgrade head

:: Start Docker
echo Starting Docker containers...
docker-compose up --build