FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=fpl.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY fpl-app/requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire project
COPY fpl-app /app/

# Copy the .env file
COPY .env /app/

# Copy entrypoint.sh
COPY entrypoint.sh /app/

# Copy install.sh
COPY install.sh /app/

# Copy install-scripts directory
COPY install-scripts /app/install-scripts/

# Copy the .pgpass file to the home directory
COPY .pgpass /root/.pgpass

# Make scripts executable
RUN chmod +x /app/entrypoint.sh /app/install.sh

# Set permissions for the .pgpass file
RUN chmod 600 /root/.pgpass

ARG APP_VERSION
ENV APP_VERSION=${APP_VERSION}
# Print the application version to verify
RUN echo "Building with APP_VERSION=${APP_VERSION}"

# Expose the port
EXPOSE 8000

# Use entrypoint.sh as the entry point
ENTRYPOINT ["/app/entrypoint.sh"]
