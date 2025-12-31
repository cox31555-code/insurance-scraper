# Use Node.js LTS with full Debian (not slim) for maximum compatibility
FROM node:20-bookworm

# Install Python 3, pip, and ALL dependencies needed for a real browser experience
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # ============================================
    # CORE BROWSER DEPENDENCIES
    # ============================================
    libnss3 \
    libnss3-tools \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libdbus-glib-1-2 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libasound2-plugins \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libcairo-gobject2 \
    # ============================================
    # GTK AND GUI LIBRARIES
    # ============================================
    libgdk-pixbuf-2.0-0 \
    libgtk-3-0 \
    libgtk-3-common \
    libglib2.0-0 \
    libglib2.0-data \
    # ============================================
    # X11 AND DISPLAY LIBRARIES
    # ============================================
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-dri3-0 \
    libxcb-shm0 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcomposite1 \
    libxcursor1 \
    libxext6 \
    libxi6 \
    libxinerama1 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libxshmfence1 \
    x11-utils \
    xvfb \
    # ============================================
    # COMPREHENSIVE FONT PACKAGES
    # ============================================
    fonts-liberation \
    fonts-liberation2 \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-noto-mono \
    fonts-freefont-ttf \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-droid-fallback \
    fonts-roboto \
    fonts-opensymbol \
    fonts-symbola \
    fontconfig \
    fontconfig-config \
    # ============================================
    # LOCALE AND TIMEZONE SUPPORT
    # ============================================
    locales \
    locales-all \
    tzdata \
    # ============================================
    # MEDIA AND CODEC LIBRARIES
    # ============================================
    libavcodec-extra \
    libavformat59 \
    libavutil57 \
    libegl1 \
    libgl1 \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    libgles2 \
    libopengl0 \
    libvulkan1 \
    mesa-vulkan-drivers \
    # ============================================
    # NETWORKING AND SSL
    # ============================================
    ca-certificates \
    openssl \
    libssl3 \
    # ============================================
    # D-BUS AND SYSTEM INTEGRATION
    # ============================================
    dbus \
    dbus-x11 \
    at-spi2-core \
    # ============================================
    # ADDITIONAL UTILITIES
    # ============================================
    wget \
    curl \
    xdg-utils \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Configure locales
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    sed -i '/en_GB.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

# Set timezone
RUN ln -snf /usr/share/zoneinfo/Europe/London /etc/localtime && echo "Europe/London" > /etc/timezone

# Update font cache
RUN fc-cache -f -v

# Create symlink so 'python' command works (points to python3)
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Install Python packages
RUN pip3 install --break-system-packages \
    playwright \
    playwright-stealth \
    python-dotenv

# Install Playwright Firefox browser with all dependencies
RUN python3 -m playwright install firefox
RUN python3 -m playwright install-deps firefox

# Copy application files
COPY server.js ./
COPY crawler.py ./
COPY public ./public/

# Expose the port
EXPOSE 3001

# Set comprehensive environment variables
ENV NODE_ENV=production
ENV PORT=3001
ENV PYTHON_BIN=python3
# Locale settings
ENV LANG=en_GB.UTF-8
ENV LANGUAGE=en_GB:en
ENV LC_ALL=en_GB.UTF-8
ENV LC_CTYPE=en_GB.UTF-8
# Timezone
ENV TZ=Europe/London
# Playwright settings
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
# Display settings for headless browser
ENV DISPLAY=:99
# Additional browser settings
ENV FONTCONFIG_PATH=/etc/fonts
ENV XDG_CONFIG_HOME=/root/.config
ENV XDG_DATA_HOME=/root/.local/share
ENV XDG_CACHE_HOME=/root/.cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1

# Create startup script that starts Xvfb and then the server
RUN printf '#!/bin/bash\n\
# Start Xvfb in the background\n\
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &\n\
XVFB_PID=$!\n\
sleep 2\n\
# Verify Xvfb is running\n\
if ! kill -0 $XVFB_PID 2>/dev/null; then\n\
    echo "Warning: Xvfb failed to start, continuing anyway..."\n\
fi\n\
# Start D-Bus\n\
mkdir -p /run/dbus\n\
dbus-daemon --system --fork 2>/dev/null || true\n\
# Start the Node.js server\n\
exec node server.js\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start the server with Xvfb
CMD ["/bin/bash", "/app/start.sh"]