FROM redis:7-alpine

# Install additional tools
RUN apk add --no-cache bash

# Create necessary directories
RUN mkdir -p /var/log/redis /var/lib/redis

# Set permissions
RUN chown -R redis:redis /var/log/redis /var/lib/redis

# Copy custom entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Switch to redis user
USER redis

# Expose ports
EXPOSE 6379 26379

# Use custom entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
