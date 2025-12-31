/**
 * Insurance Group Lookup Crawler
 * Node.js implementation using Puppeteer with stealth plugin
 * Target: confused.com insurance group checker
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

// Apply stealth plugin to avoid detection
puppeteer.use(StealthPlugin());

// Load environment variables
require('dotenv').config();

// Target URL for insurance group lookup - confused.com
const TARGET_URL = 'https://www.confused.com/compare-car-insurance/group-checker';

// User agents for Chrome
const USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
];

// Screen sizes for randomization
const SCREEN_SIZES = [
    [1920, 1080],
    [1366, 768],
    [1536, 864],
    [1440, 900],
    [1680, 1050],
];

/**
 * Add a human-like delay
 * @param {number} minMs - Minimum delay in milliseconds
 * @param {number} maxMs - Maximum delay in milliseconds
 */
async function humanDelay(minMs = 50, maxMs = 150) {
    const delay = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
    await new Promise(resolve => setTimeout(resolve, delay));
}

/**
 * Type text with human-like delays
 * @param {object} page - Puppeteer page object
 * @param {string} selector - CSS selector for the input element
 * @param {string} text - Text to type
 */
async function humanType(page, selector, text) {
    await page.click(selector);
    for (const char of text) {
        await page.type(selector, char, { delay: 0 });
        // Variable delay between keystrokes (50-150ms)
        let delay = Math.floor(Math.random() * 100) + 50;
        // Occasional longer pause (10% chance)
        if (Math.random() < 0.1) {
            delay += Math.floor(Math.random() * 200) + 100;
        }
        await new Promise(resolve => setTimeout(resolve, delay));
    }
}

/**
 * Check if the page is a Cloudflare challenge page
 * @param {object} page - Puppeteer page object
 * @returns {boolean} - True if Cloudflare challenge detected
 */
async function isCloudflareChallenge(page) {
    try {
        const title = await page.title().catch(() => '');
        const bodyText = await page.$eval('body', el => el.innerText.slice(0, 2000)).catch(() => '');
        const cloudflareIndicators = [
            'just a moment',
            'checking your browser',
            'please wait',
            'ddos protection',
            'cloudflare',
            'ray id',
            'enable javascript',
            'attention required',
            'security check',
        ];
        
        const lowerTitle = title.toLowerCase();
        const lowerBody = bodyText.toLowerCase();
        
        return cloudflareIndicators.some(indicator => 
            lowerTitle.includes(indicator) || lowerBody.includes(indicator)
        );
    } catch {
        return false;
    }
}

/**
 * Verify the proxy is working by checking the IP address
 * @param {object} page - Puppeteer page object
 * @param {array} debugInfo - Array to append debug messages
 * @returns {string} - IP address or empty string
 */
async function verifyProxyIp(page, debugInfo) {
    try {
        await page.goto('https://api.ipify.org', { waitUntil: 'networkidle2', timeout: 30000 });
        await new Promise(resolve => setTimeout(resolve, 2000));
        const ip = await page.$eval('body', el => el.innerText.trim());
        if(/^\d+\.\d+\.\d+\.\d+$/.test(ip)) {
            debugInfo.push(`Proxy IP verified: ${ip}`);
            return ip;
        }
        debugInfo.push('Could not parse IP from response');
        return '';
    } catch (e) {
        debugInfo.push(`IP verification failed: ${String(e).slice(0, 50)}`);
        return '';
    }
}

/**
 * Main function to lookup insurance group using Puppeteer
 * @param {string} registration - Vehicle registration number
 * @returns {object} - Result object with success/error and data
 */
async function lookupInsuranceGroup(registration) {
    // Get Novada proxy configuration from environment
    const proxyHost = process.env.PROXY_HOST || '';
    const proxyPort = process.env.PROXY_PORT || '';
    const proxyUser = process.env.PROXY_USER || '';
    const proxyPass = process.env.PROXY_PASS || '';
    
    const debugInfo = [];
    // Debug: Log environment variable status
    debugInfo.push(`ENV check - PROXY_HOST: ${proxyHost ? 'SET' : 'EMPTY'}, PROXY_PORT: ${proxyPort ? 'SET' : 'EMPTY'}`);
    let browser = null;
    
    try {
        // Random user agent
        const userAgent = USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
        debugInfo.push(`User-Agent: ${userAgent.slice(0, 50)}...`);
        
        // Random screen size
        const [screenWidth, screenHeight] = SCREEN_SIZES[Math.floor(Math.random() * SCREEN_SIZES.length)];
        // Build launch arguments
        const launchArgs = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            `--window-size=${screenWidth},${screenHeight}`,
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions',
            '--disable-plugins',
            '--lang=en-GB',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--ignore-certificate-errors',
            '--ignore-certificate-errors-spki-list',
        ];
        
        // Add proxy if configured
        if (proxyHost && proxyPort) {
            launchArgs.push(`--proxy-server=http://${proxyHost}:${proxyPort}`);if (proxyUser && proxyPass) {
                debugInfo.push(`Using authenticated proxy: ${proxyHost}:${proxyPort}`);
            } else {
                debugInfo.push(`Using proxy: ${proxyHost}:${proxyPort}`);
            }
        } else {
            debugInfo.push('No proxy configured');
        }
        
        // Launch browser
        browser = await puppeteer.launch({
            headless:'new',
            args: launchArgs,
            executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || undefined,
            timeout: 60000,
        });
        
        const page = await browser.newPage();
        
        // Set user agent
        await page.setUserAgent(userAgent);
        
        // Set viewport
        await page.setViewport({ width: screenWidth, height: screenHeight });
        
        // Set page timeout
        page.setDefaultTimeout(60000);
        
        // Authenticate proxy if credentials provided
        if (proxyHost && proxyPort && proxyUser && proxyPass) {
            await page.authenticate({
                username: proxyUser,
                password: proxyPass,
            });debugInfo.push('Proxy authentication configured');
        }
        
        // Verify proxy if configured
        if (proxyHost && proxyPort) {
            await verifyProxyIp(page, debugInfo);
        }
        
        // Navigate to target URL
        debugInfo.push('Navigating to confused.com...');
        await page.goto(TARGET_URL, { waitUntil: 'networkidle2', timeout: 60000 });
        
        // Wait for page to load (5 seconds)
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Check for Cloudflare challenge
        if (await isCloudflareChallenge(page)) {
            debugInfo.push('Cloudflare challenge detected, waiting8 seconds...');
            await new Promise(resolve => setTimeout(resolve, 8000));
            
            // Wait up to 15 more seconds for Cloudflare to pass
            let cloudflarePassed = false;
            for (let i = 0; i < 15; i++) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                if (!(await isCloudflareChallenge(page))) {
                    debugInfo.push(`Cloudflare passed after ${i + 1}s`);
                    cloudflarePassed = true;
                    break;
                }
            }
            
            if (!cloudflarePassed) {
                debugInfo.push('Cloudflare challenge did not pass');const pageTitle = await page.title().catch(() => '');
                return {
                    success: false,
                    error: 'Blocked by Cloudflare',
                    cloudflare_blocked: true,
                    registration,
                    debug: debugInfo,pageTitle,
                };
            }
        }
        
        debugInfo.push('Page loaded successfully');
        
        // Handle cookie consent for confused.com
        const cookieSelectors = [
            'button.cnf-cookies_save-cookie-prefs',
            '#onetrust-accept-btn-handler',
            'button[id*="accept"]',
            '[data-testid="cookie-accept"]',
        ];
        
        for (const selector of cookieSelectors) {
            try {
                const cookieElement = await page.$(selector);
                if (cookieElement) {
                    await humanDelay(200,400);
                    await cookieElement.click();
                    debugInfo.push('Accepted cookies');
                    await humanDelay(300, 500);
                    break;
                }
            } catch {
                // Continue to next selector
            }
        }
        
        // Find the registration input field for confused.com
        const inputSelectors = [
            'input[name="vrm"]',
            'input[name="registration"]',
            'input[id*="registration"]',
            'input[id*="vrm"]',
            'input[placeholder*="registration" i]',
            'input[placeholder*="reg" i]',
            'input[data-testid*="registration"]',
            'input[data-testid*="vrm"]',
            'input[type="text"]',];
        
        let inputElement = null;
        let usedSelector = null;
        
        for (const selector of inputSelectors) {
            try {
                await page.waitForSelector(selector, { timeout: 3000, visible: true });
                const elements = await page.$$(selector);
                for (const el of elements) {
                    const isVisible = await el.evaluate(elem => {
                        const style = window.getComputedStyle(elem);
                        return style.display !== 'none' && style.visibility !== 'hidden' && elem.offsetParent !== null;
                    });
                    if (isVisible) {
                        inputElement = el;
                        usedSelector = selector;
                        debugInfo.push(`Found input with: ${selector}`);
                        break;
                    }
                }
                if (inputElement) break;
            } catch {
                // Continue to next selector
            }
        }
        
        // Try XPath as fallback
        if (!inputElement) {
            try {
                const xpathInputs = await page.$x("//input[contains(@placeholder, 'reg') or contains(@id, 'reg') or contains(@name, 'vrm')]");
                if (xpathInputs.length > 0) {
                    inputElement = xpathInputs[0];
                    usedSelector = "XPath: registration input";
                    debugInfo.push('Found input with XPath');
                }
            } catch {
                // XPath failed
            }
        }
        
        if (!inputElement) {
            const pageText = await page.$eval('body', el => el.innerText.slice(0, 3000)).catch(() => '');
            const finalUrl = page.url();
            const pageTitle = await page.title().catch(() => '');
            debugInfo.push(`Final URL: ${finalUrl}`);
            debugInfo.push(`Page title: ${pageTitle}`);
            
            // Check if this is actually a Cloudflare block
            if (await isCloudflareChallenge(page)) {
                return {
                    success: false,
                    error: 'Blocked by Cloudflare',
                    cloudflare_blocked: true,
                    registration,
                    debug: debugInfo,
                    pageTitle,
                };
            }
            
            return {
                success: false,
                error: 'Could not find registration input field',
                registration,
                debug: debugInfo,
                pageTextSample: pageText,
                finalUrl,
            };
        }
        
        // Click and type registration
        await humanDelay(100, 200);
        await inputElement.click();
        await humanDelay(50, 100);
        
        // Clear the input
        await inputElement.evaluate(el => el.value = '');
        
        // Type with human-like delays
        for (const char of registration) {
            await inputElement.type(char, { delay: 0 });
            let delay = Math.floor(Math.random() * 100) + 50;
            if (Math.random() < 0.1) {
                delay += Math.floor(Math.random() * 200) + 100;
            }
            await new Promise(resolve => setTimeout(resolve, delay));
        }
        debugInfo.push(`Typed: ${registration}`);
        await humanDelay(200, 400);
        
        // Find and click "Find group" button for confused.com
        const buttonSelectors = [
            'button.btn',
            'button[type="submit"]',
            'button[data-testid*="submit"]',
            'input[type="submit"]',
        ];
        
        const buttonXPaths = [
            "//button[contains(text(), 'Find group')]",
            "//button[contains(text(), 'Find')]",
            "//button[contains(@class, 'btn')]",
        ];
        
        let buttonElement = null;
        
        for (const selector of buttonSelectors) {
            try {
                const btn = await page.$(selector);
                if (btn) {
                    buttonElement = btn;
                    debugInfo.push(`Found button with: ${selector}`);
                    break;
                }
            } catch {
                // Continue to next selector
            }
        }
        
        // Try XPath for buttons
        if (!buttonElement) {
            for (const xpath of buttonXPaths) {
                try {
                    const buttons = await page.$x(xpath);
                    if (buttons.length > 0) {
                        buttonElement = buttons[0];
                        debugInfo.push(`Found button with XPath: ${xpath}`);
                        break;
                    }
                } catch {
                    // Continue to next XPath
                }
            }
        }
        
        if (!buttonElement) {
            // Diagnostic: capture all buttons on page for debugging
            const allButtons = await page.$$eval('button', buttons =>
                buttons.map(b => ({
                    text: b.innerText.slice(0, 50),
                    type: b.getAttribute('type'),
                    testId: b.getAttribute('data-testid'),
                    className: b.className.slice(0, 50),
                }))
            ).catch(() => []);
            debugInfo.push(`Buttons found on page: ${JSON.stringify(allButtons)}`);
            
            const pageTitle = await page.title().catch(() => '');
            const finalUrl = page.url();
            debugInfo.push(`Final URL: ${finalUrl}`);
            debugInfo.push(`Page title: ${pageTitle}`);
            
            return {
                success: false,
                error: 'Could not find submit button',
                registration,
                debug: debugInfo,
                finalUrl,
                pageTitle,
            };
        }
        
        await humanDelay(100, 200);
        await buttonElement.click();
        debugInfo.push('Clicked submit');
        // Wait for results
        const maxWait = 20;
        let resultsLoaded = false;
        
        for (let i = 0; i < maxWait * 2; i++) {
            await new Promise(resolve => setTimeout(resolve, 500));
            const pageText = await page.$eval('body', el => el.innerText).catch(() => '');
            
            // Check for Cloudflare block
            if (await isCloudflareChallenge(page)) {
                return {
                    success: false,
                    error: 'Blocked by Cloudflare',
                    cloudflare_blocked: true,
                    registration,
                    debug: debugInfo,
                };
            }
            
            // Check for results - confused.com shows "Insurance group" and "Group X/50"
            if ((pageText.toLowerCase().includes('insurance group') || pageText.toLowerCase().includes('the car')) &&
                pageText.match(/\d+\s*\/\s*50/)) {
                resultsLoaded = true;
                debugInfo.push(`Results loaded in ${((i + 1) * 0.5).toFixed(1)}s`);
                break;
            }
            
            // Check for not found
            if (pageText.toLowerCase().includes("couldn't find") || 
                pageText.toLowerCase().includes('not found') ||
                pageText.toLowerCase().includes('no results')) {
                debugInfo.push('Vehicle not found');
                break;
            }}
        
        if (!resultsLoaded) {
            const pageText = await page.$eval('body', el => el.innerText).catch(() => '');
            return {
                success: false,
                error: 'Timeout waiting for results',
                registration,
                debug: debugInfo,
                pageTextSample: pageText.slice(0, 1500),
            };
        }
        
        // Extract insurance group from confused.com
        // Format: "9/50" in the result box
        const pageText = await page.$eval('body', el => el.innerText).catch(() => '');
        // Patterns for confused.com format
        const patterns = [
            /(\d+)\s*\/\s*50/,  // e.g., "9/50"
            /Group\s+(\d+)\s*\/\s*(\d+)/i,
            /insurance group[^\d]*(\d+)\s*\/\s*(\d+)/i,];
        
        let groupNum = null;
        let maxGroup = 50; // confused.com uses50 as max
        
        for (const pattern of patterns) {
            const match = pageText.match(pattern);
            if (match) {
                groupNum = parseInt(match[1], 10);
                if (match[2]) {
                    maxGroup = parseInt(match[2], 10);
                }
                break;
            }
        }
        
        // Try to extract car details
        let carDetails = null;
        const carMatch = pageText.match(/The car\s*\n+([^\n]+)/i);
        if (carMatch) {
            carDetails = carMatch[1].trim();
        }
        
        if (groupNum !== null) {
            return {
                success: true,
                registration,
                insuranceGroup: groupNum,
                maxGroup,
                displayText: `Group ${groupNum}/${maxGroup}`,
                carDetails,};
        }
        
        return {
            success: false,
            error: 'Could not find insurance group in response',
            registration,
            debug: debugInfo,
            pageTextSample: pageText.slice(0, 1500),
        };
        
    } catch (e) {
        debugInfo.push(`Exception: ${String(e)}`);
        return {
            success: false,
            error: String(e),
            registration,
            debug: debugInfo,};
    } finally {
        if (browser) {
            try {
                await browser.close();
            } catch {
                // Ignore close errors
            }
        }
    }
}

/**
 * Main entry point with retry logic
 * @param {string} registration - Vehicle registration number
 * @returns {object} - Result object
 */
async function main(registration) {
    const maxRetries = 5;
    let result;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        result = await lookupInsuranceGroup(registration);
        
        if (result.success) {
            return result;
        }
        
        // Check if it's a Cloudflare block - retry
        const isCloudflareBlock = result.cloudflare_blocked || false;
        
        if (isCloudflareBlock && attempt < maxRetries - 1) {
            result.debug = result.debug || [];
            result.debug.push(`Cloudflare blocked, retrying (attempt ${attempt + 2}/${maxRetries})...`);
            await new Promise(resolve => setTimeout(resolve, 2000));
            continue;
        }
        
        // For other errors or last attempt, don't retry
        break;
    }
    
    return result;
}

// Export functions for use as module
module.exports = {
    lookupInsuranceGroup,
    main,
    humanDelay,
    humanType,
    isCloudflareChallenge,
    verifyProxyIp,
    TARGET_URL,
    USER_AGENTS,SCREEN_SIZES,
};

// CLI support - run if called directly
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.log(JSON.stringify({ success: false, error: 'Missing registration argument' }));
        process.exit(1);
    }
    
    const registration = args[0].trim().toUpperCase();
    main(registration).then(result => {
        console.log(JSON.stringify(result));
        process.exit(result.success ? 0 : 1);
    }).catch(err => {
        console.log(JSON.stringify({ success: false, error: String(err) }));
        process.exit(1);
    });
}