# ============================================================================
# Conecta PRO Frontend - Production Dockerfile
# Pre-built version - expects dist folder to exist
# ============================================================================

FROM nginx:alpine AS production

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy pre-built assets
COPY dist /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1:80/health || exit 1

# Create health endpoint
RUN echo '{"status":"healthy","service":"conecta-pro-frontend"}' > /usr/share/nginx/html/health

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
