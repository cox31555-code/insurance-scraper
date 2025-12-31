# Insurance Group Lookup Scraper

A web scraper that looks up UK vehicle insurance groups from MoneySupermarket using Puppeteer with stealth capabilities.

## Features

- **Stealth Browsing**: Uses `puppeteer-extra-plugin-stealth` to avoid bot detection
- **Proxy Support**: Authenticated rotating proxy support via environment variables
- **Human-like Behavior**: Random delays, typing simulation, and randomized user agents/screen sizes
- **Cloudflare Bypass**: Detection and waiting logic for Cloudflare challenges
- **Retry Logic**: Automatic retries (5 attempts) for Cloudflare blocks
- **REST API**: Express server with `/lookup` endpoint
- **Terminal UI**: Built-in web-based terminal interface

## Requirements

- Node.js 18+ 
- Chrome/Chromium browser (for Puppeteer)

## Installation

```bash
# Install dependencies
npm install

# Copy environment template (if needed)
cp .env.example .env
```

## Configuration

Create a `.env` file with the following variables:

```env
# Server Configuration
PORT=3001
HOST=0.0.0.0

# Proxy Configuration (Optional - for rotating residential proxy)
PROXY_HOST=your-proxy-host.com
PROXY_PORT=7777
PROXY_USER=your-username
PROXY_PASS=your-password

# Puppeteer Configuration (Optional)
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
```

## Usage

### Start the Server

```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm start
```

### API Endpoints

#### Health Check
```bash
GET /health
```
Response: `{ "ok": true }`

#### Lookup Insurance Group
```bash
POST /lookup
Content-Type: application/json

{"registration": "AB12CDE"
}
```

**Success Response:**
```json
{
  "success": true,
  "registration": "AB12CDE",
  "insuranceGroup": 15,
  "maxGroup": 50,
  "displayText": "Group 15/50"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "registration": "AB12CDE",
  "debug": ["Debug message 1", "Debug message 2"]
}
```

### Command Line Usage

```bash
# Run crawler directly
node crawler.js AB12CDE

# Or use npm script
npm run crawler -- AB12CDE
```

### Web Interface

Open `http://localhost:3001` in your browser to use the terminal-style web interface.

## Docker

### Build and Run

```bash
# Build the image
docker build -t insurance-scraper .

# Run the container
docker run -p 3001:3001 --env-file .env insurance-scraper
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  scraper:
    build: .
    ports:
      - "3001:3001"
    env_file:
      - .env
    restart: unless-stopped
```

## Testing

```bash
# Run unit tests
npm test

# Run with verbose output
npm run test:verbose

# Run integration tests (requires browser)
RUN_INTEGRATION_TESTS=true npm test
```

## Project Structure

```
├── server.js           # Express API server
├── crawler.js          # Puppeteer-based web scraper
├── package.json        # Node.js dependencies
├── Dockerfile          # Docker configuration
├── .env                # Environment variables (not in git)
├── .dockerignore       # Docker ignore rules
├── public/
│   └── index.html      # Terminal-style web interface
├── test/
│   └── crawler.test.js # Jest test suite
└── README.md           # This file
```

## Migration from Python

This project was converted from a Python implementation using `selenium-wire` and `undetected-chromedriver` to Node.js using `puppeteer-extra` with the stealth plugin.

### Key Changes

| Component | Python (Before) | Node.js (After) |
|-----------|-----------------|-----------------|
| Browser Automation | selenium-wire + undetected-chromedriver | puppeteer-extra + stealth plugin |
| Server Integration | Subprocess spawn | Direct module import |
| Proxy Auth | selenium-wire proxy config | page.authenticate() |
| Dependencies | Python + Node.js | Node.js only |
| Docker Image | ~2GB (Python + Chrome) | ~1GB (Node.js + Chromium) |

### Cleanup Python Files

After verifying the Node.js implementation works correctly:

```bash
# Make the cleanup script executable
chmod +x cleanup-python.sh

# Run the cleanup script
./cleanup-python.sh
```

Or manually remove:
- `crawler.py`
- `__pycache__/`

## Troubleshooting

### Cloudflare Blocking

If you're getting blocked by Cloudflare:
1. Ensure proxy is configured correctly
2. Try a different proxy/IP
3. The scraper will automatically retry up to 5 times

### Browser Not Found

If Puppeteer can't find Chrome:
```bash
# Set the executable path
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Or in .env
PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome
```

### Docker Issues

If the container fails to start:
1. Check logs: `docker logs <container-id>`
2. Ensure all dependencies are installed
3. Verify the Chromium path is correct

## License

ISC

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `npm test`
5. Submit a pull request