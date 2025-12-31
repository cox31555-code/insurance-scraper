# Use Node.js LTS with Debian base for better compatibility
FROM node:20-bookworm-slim

# Install Python 3, pip, and dependencies needed for Playwright
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    # Additional utilities
    wget \
    ca-certificates \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Create symlink so 'python' command works (points to python3)
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Copy Python requirements and install them
# Using --break-system-packages since we're in a container
RUN pip3 install --break-system-packages \
    playwright \
    playwright-stealth \
    python-dotenv

# Install Playwright browsers (Chromium only to save space)
RUN python3 -m playwright install chromium
RUN python3 -m playwright install-deps chromium

# Copy application files
COPY server.js ./
COPY crawler.py ./
COPY public ./public/

# Expose the port
EXPOSE 3001

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3001
ENV PYTHON_BIN=python3

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1

# Start the server
CMD ["node", "server.js"]