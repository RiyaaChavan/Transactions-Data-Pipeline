# #!/bin/bash
# set -e
# echo "Initializing TimescaleDB extension..."
# # Start the original PostgreSQL entrypoint script in the background
# docker-entrypoint.sh postgres &

# # Wait until PostgreSQL is ready to accept connections
# until pg_isready -h localhost -p 5432 -U "$POSTGRES_USER" >/dev/null 2>&1; do
#   echo "Waiting for PostgreSQL to be ready..."
#   sleep 2
# done

# # Execute the initialization SQL script
# psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/initdb.sql

# # Wait for the PostgreSQL process to keep the container running
# wait

#!/bin/bash
set -e

echo "Initializing TimescaleDB extension..."

# Start PostgreSQL process in the background
docker-entrypoint.sh postgres &

# Wait until PostgreSQL is ready
until pg_isready -h localhost -p 5432 -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Run the initialization SQL
if [ -f /docker-entrypoint-initdb.d/init.sql ]; then
  echo "Executing init.sql..."
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init.sql
else
  echo "No init.sql found, skipping..."
fi

# Keep the container running
wait
