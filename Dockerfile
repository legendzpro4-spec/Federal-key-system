# syntax=docker/dockerfile:1
FROM node:18-alpine

# Install Lua 5.3
RUN apk add --no-cache lua5.3 lua5.3-dev

WORKDIR /app

# Copy package files first → better caching
COPY package*.json ./

# Install production dependencies only
RUN npm ci --omit=dev --ignore-scripts

# Copy application code
COPY . .

# Create temp directory with relaxed permissions (Railway ephemeral fs)
RUN mkdir -p /tmp/lua-dumper && chmod 1777 /tmp/lua-dumper

# Health check endpoint Railway can ping
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT:-3000}/api/health || exit 1

# Start the server (Railway will provide PORT)
CMD ["node", "server.js"]
