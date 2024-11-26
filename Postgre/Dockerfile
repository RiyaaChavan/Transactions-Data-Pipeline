# Use the official TimescaleDB image as the base
FROM timescale/timescaledb:latest-pg14

# Set environment variables for PostgreSQL
ENV POSTGRES_DB=financial_transactions
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=password

# Copy the initialization script into the container
COPY init.sql /docker-entrypoint-initdb.d/initdb.sql

# (Optional) If you need to run additional scripts or configurations, add them here
# For example, copying a custom entrypoint script:
# COPY init-timescaledb.sh /init-timescaledb.sh
# RUN chmod +x /init-timescaledb.sh
# ENTRYPOINT ["/init-timescaledb.sh"]

# The default command is already set to "postgres", so no need to specify CMD