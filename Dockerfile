# Minimal Node.js + Puppeteer Dockerfile
# Converted from Python selenium-wire to Node.js Puppeteer

FROM node:20-bookworm

# Install Chrome/Chromium dependencies
RUN apt-get update && apt-get install -y \
    # Core browser dependencies
    chromium \
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
    libpangocairo-1.0-0 \
    libcairo2 \
    # GTK libraries
    libgtk-3-0 \
    # X11 libraries
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxss1 \
    libxtst6 \
    # Fonts
    fonts-liberation \
    fonts-noto \
    fonts-noto-color-emoji \
    fontconfig \
    # SSL/Networking
    ca-certificates \
    # Utilities
    wget \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Update font cache
RUN fc-cache -f -v

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install Node.js dependencies
# Skip Chromium download since we use system Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
RUN npm ci --only=production

# Copy application files
COPY server.js ./
COPY crawler.js ./
COPY public ./public/

# Expose the port
EXPOSE 3001

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3001
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
# Locale settings
ENV LANG=en_GB.UTF-8
ENV LANGUAGE=en_GB:en
ENV LC_ALL=C.UTF-8
# Timezone
ENV TZ=Europe/London

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1

# Start the server
CMD ["node", "server.js"]