#!/bin/bash

# Apply any pending migrations (if needed)
alembic upgrade head

# Start the app
exec "$@"