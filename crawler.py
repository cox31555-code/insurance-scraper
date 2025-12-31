import sys
import json
import asyncio
import os
import re
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Load environment variables from .env file
load_dotenv()

TARGET_URL = "https://www.moneysupermarket.com/car-insurance/car-insurance-group-checker-tool/"

USER_AGENTS = [
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "platform": "Linux x86_64", "os": "Linux"},
    {"ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36", "platform": "Linux x86_64", "os": "Linux"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0; rv:121.0) Gecko/20100101 Firefox/121.0", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0", "platform": "Linux x86_64", "os": "Linux"},
    {"ua": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0", "platform": "Linux x86_64", "os": "Linux"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15", "platform": "MacIntel", "os": "macOS"},
]

SCREEN_CONFIGS = [
    {"width": 1920, "height": 1080, "device_scale_factor": 1},
    {"width": 1920, "height": 1080, "device_scale_factor": 1.25},
    {"width": 1920, "height": 1080, "device_scale_factor": 1.5},
    {"width": 1366, "height": 768, "device_scale_factor": 1},
    {"width": 1536, "height": 864, "device_scale_factor": 1.25},
    {"width": 1440, "height": 900, "device_scale_factor": 1},
    {"width": 1680, "height": 1050, "device_scale_factor": 1},
    {"width": 2560, "height": 1440, "device_scale_factor": 1},
    {"width": 2560, "height": 1440, "device_scale_factor": 1.25},
    {"width": 1280, "height": 720, "device_scale_factor": 1},
    {"width": 1600, "height": 900, "device_scale_factor": 1},
    {"width": 1280, "height": 800, "device_scale_factor": 1},
    {"width": 1280, "height": 1024, "device_scale_factor": 1},
    {"width": 1400, "height": 1050, "device_scale_factor": 1},
    {"width": 1920, "height": 1200, "device_scale_factor": 1},
    {"width": 2560, "height": 1600, "device_scale_factor": 1},
    {"width": 3840, "height": 2160, "device_scale_factor": 2},
    {"width": 1504, "height": 1003, "device_scale_factor": 2},
    {"width": 1728, "height": 1117, "device_scale_factor": 2},
    {"width": 1800, "height": 1169, "device_scale_factor": 2},
]

LOCALE_CONFIGS = [
    {"locale": "en-GB", "timezone": "Europe/London"},
    {"locale": "en-GB", "timezone": "Europe/London"},
    {"locale": "en-US", "timezone": "Europe/London"},
]

ACCEPT_LANGUAGES = ["en-GB,en;q=0.9", "en-GB,en-US;q=0.9,en;q=0.8", "en-GB,en;q=0.9,en-US;q=0.8"]


def generate_random_fingerprint():
    ua_config = random.choice(USER_AGENTS)
    screen = random.choice(SCREEN_CONFIGS)
    locale_config = random.choice(LOCALE_CONFIGS)
    accept_language = random.choice(ACCEPT_LANGUAGES)
    platform = ua_config["platform"]
    os_type = ua_config["os"]
    if os_type == "macOS":
        hardware_concurrency = random.choice([4, 8, 10, 12, 16, 20])
        device_memory = random.choice([8, 16, 32, 64])
        color_depth = 30
        webgl_vendor = "Apple Inc."
        webgl_renderer = random.choice(["Apple M1", "Apple M2", "Apple M3", "AMD Radeon Pro 5500M"])
    elif os_type == "Linux":
        hardware_concurrency = random.choice([2, 4, 6, 8, 12, 16, 24, 32])
        device_memory = random.choice([4, 8, 16, 32, 64])
        color_depth = 24
        webgl_vendor = random.choice(["Intel", "NVIDIA Corporation", "AMD"])
        webgl_renderer = random.choice(["Mesa Intel UHD Graphics", "NVIDIA GeForce GTX 1080", "AMD Radeon RX 580"])
    else:
        hardware_concurrency = random.choice([2, 4, 6, 8, 12, 16, 24])
        device_memory = random.choice([4, 8, 16, 32])
        color_depth = random.choice([24, 32])
        webgl_vendor = random.choice(["Google Inc. (NVIDIA)", "Google Inc. (Intel)", "Google Inc. (AMD)"])
        webgl_renderer = random.choice(["ANGLE (NVIDIA GeForce GTX 1660)", "ANGLE (Intel UHD Graphics 630)", "ANGLE (AMD Radeon RX 580)"])
    
    return {
        "user_agent": ua_config["ua"], "platform": platform, "os_type": os_type,
        "viewport": {"width": screen["width"], "height": screen["height"]},
        "device_scale_factor": screen["device_scale_factor"],
        "locale": locale_config["locale"], "timezone": locale_config["timezone"],
        "accept_language": accept_language, "hardware_concurrency": hardware_concurrency,
        "device_memory": device_memory, "color_depth": color_depth,
        "webgl_vendor": webgl_vendor, "webgl_renderer": webgl_renderer,
    }


async def short_delay(min_ms=20, max_ms=100):
    await asyncio.sleep(random.randint(min_ms, max_ms) / 1000)


def bezier_curve(t, p0, p1, p2, p3):
    return (1-t)**3 * p0 + 3 * (1-t)**2 * t * p1 + 3 * (1-t) * t**2 * p2 + t**3 * p3


def generate_human_curve_points(start_x, start_y, end_x, end_y, num_points=15):
    mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
    offset_x = (end_x - start_x) * random.uniform(-0.3, 0.3)
    offset_y = (end_y - start_y) * random.uniform(-0.3, 0.3)
    cp1_x = start_x + (mid_x - start_x) * 0.5 + offset_x
    cp1_y = start_y + (mid_y - start_y) * 0.5 + offset_y
    cp2_x = mid_x + (end_x - mid_x) * 0.5 - offset_x * 0.5
    cp2_y = mid_y + (end_y - mid_y) * 0.5 - offset_y * 0.5
    points = []
    for i in range(num_points + 1):
        t = i / num_points
        t_eased = t * t * (3 - 2 * t)
        x = bezier_curve(t_eased, start_x, cp1_x, cp2_x, end_x)
        y = bezier_curve(t_eased, start_y, cp1_y, cp2_y, end_y)
        if 0 < i < num_points:
            x += random.uniform(-1.5, 1.5)
            y += random.uniform(-1.5, 1.5)
        points.append((x, y))
    return points


async def human_type(element, text):
    fast_pairs = ['th', 'he', 'in', 'er', 'an', 're', 'on', 'at', 'en', 'nd']
    prev_char = ''
    for char in text:
        await element.type(char, delay=0)
        pair = prev_char + char.lower()
        if pair in fast_pairs:
            delay = random.randint(30, 60)
        elif char.isupper():
            delay = random.randint(80, 140)
        elif char.isdigit():
            delay = random.randint(100, 180)
        elif char == ' ':
            delay = random.randint(40, 120)
        else:
            delay = random.randint(50, 100)
            if random.random() < 0.08:
                delay += random.randint(80, 200)
        await asyncio.sleep(delay / 1000)
        prev_char = char.lower()
    await asyncio.sleep(random.randint(50, 150) / 1000)


async def move_and_click(page, element):
    box = await element.bounding_box()
    if box:
        click_x = box["x"] + box["width"] * random.uniform(0.25, 0.75)
        click_y = box["y"] + box["height"] * random.uniform(0.35, 0.65)
        start_x = max(50, min(random.randint(int(box["x"] - 200), int(box["x"] + 200)), 1800))
        start_y = max(50, min(random.randint(int(box["y"] - 150), int(box["y"] + 150)), 900))
        points = generate_human_curve_points(start_x, start_y, click_x, click_y, random.randint(10, 20))
        for i, (x, y) in enumerate(points):
            await page.mouse.move(x, y)
            progress = i / len(points)
            delay = random.uniform(8, 18) if progress < 0.2 or progress > 0.8 else random.uniform(3, 10)
            await asyncio.sleep(delay / 1000)
        await asyncio.sleep(random.randint(30, 100) / 1000)
        if random.random() < 0.3:
            await page.mouse.move(click_x + random.uniform(-3, 3), click_y + random.uniform(-2, 2))
            await asyncio.sleep(random.randint(20, 50) / 1000)
        await page.mouse.click(click_x, click_y)
    else:
        await element.click()


async def lookup_insurance_group(registration: str):
    proxy_host = os.environ.get("PROXY_HOST", "")
    proxy_port = os.environ.get("PROXY_PORT", "")
    proxy_user = os.environ.get("PROXY_USER", "")
    proxy_pass = os.environ.get("PROXY_PASS", "")
    
    proxy_config = None
    if proxy_host and proxy_port and proxy_host.strip() and proxy_port.strip():
        proxy_config = {"server": f"http://{proxy_host}:{proxy_port}"}
        if proxy_user and proxy_pass:
            proxy_config["username"] = proxy_user
            proxy_config["password"] = proxy_pass
    
    fingerprint = generate_random_fingerprint()
    debug_info = [f"Fingerprint: {fingerprint['user_agent'][:50]}... | {fingerprint['os_type']}"]
    if proxy_config:
        debug_info.append(f"Using proxy: {proxy_host}:{proxy_port}")
    else:
        debug_info.append("No proxy configured")
    
    try:
        async with async_playwright() as p:
            # Apply stealth BEFORE launching browser
            stealth = Stealth()
            stealth.hook_playwright_context(p)
            
            browser_args = {
                "headless": True,
                "args": ["--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox",
                         "--disable-setuid-sandbox", "--disable-infobars",
                         f"--window-size={fingerprint['viewport']['width']},{fingerprint['viewport']['height']}"]
            }
            if proxy_config:
                browser_args["proxy"] = proxy_config
            
            browser = await p.chromium.launch(**browser_args)
            
            context = await browser.new_context(
                viewport=fingerprint["viewport"], user_agent=fingerprint["user_agent"],
                locale=fingerprint["locale"], timezone_id=fingerprint["timezone"],
                device_scale_factor=fingerprint["device_scale_factor"],
                color_scheme=random.choice(["light", "light", "dark"]),
                geolocation={"latitude": 51.5074 + random.uniform(-0.1, 0.1), "longitude": -0.1278 + random.uniform(-0.1, 0.1)},
                permissions=["geolocation"],
                extra_http_headers={
                    "Accept-Language": fingerprint["accept_language"],
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br", "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": f'"{fingerprint["platform"]}"',
                    "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1",
                },
            )
            
            await context.add_init_script(f"""
                Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprint['hardware_concurrency']} }});
                Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprint['device_memory']} }});
                Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprint['platform']}' }});
                Object.defineProperty(screen, 'colorDepth', {{ get: () => {fingerprint['color_depth']} }});
                Object.defineProperty(screen, 'pixelDepth', {{ get: () => {fingerprint['color_depth']} }});
                const getParameterProxyHandler = {{
                    apply: function(target, thisArg, args) {{
                        if (args[0] === 37445) return '{fingerprint['webgl_vendor']}';
                        if (args[0] === 37446) return '{fingerprint['webgl_renderer']}';
                        return Reflect.apply(target, thisArg, args);
                    }}
                }};
                ['WebGLRenderingContext', 'WebGL2RenderingContext'].forEach(ctx => {{
                    if (window[ctx]) {{
                        const original = window[ctx].prototype.getParameter;
                        window[ctx].prototype.getParameter = new Proxy(original, getParameterProxyHandler);
                    }}
                }});
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {{
                    if (type === 'image/png' && this.width > 16 && this.height > 16) {{
                        const context = this.getContext('2d');
                        if (context) {{
                            const imageData = context.getImageData(0, 0, this.width, this.height);
                            for (let i = 0; i < imageData.data.length; i += 4) {{
                                imageData.data[i] = imageData.data[i] ^ (Math.random() > 0.99 ? 1 : 0);
                            }}
                            context.putImageData(imageData, 0, 0);
                        }}
                    }}
                    return originalToDataURL.apply(this, arguments);
                }};
            """)
            
            page = await context.new_page()
            # Listen for console messages for debugging
            page.on("console", lambda msg: None)  # Suppress console
            
            # Use networkidle for better page load detection, with fallback
            try:
                await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            except Exception as nav_error:
                # Fallback to domcontentloaded if networkidle times out
                debug_info.append(f"Networkidle timeout, retrying with domcontentloaded: {str(nav_error)[:50]}")
                await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            
            debug_info.append("Page loaded")
            # Wait longer for page to stabilize and JavaScript to execute
            await asyncio.sleep(4)
            
            # Check if we hit a Cloudflare challenge page early
            page_text_early = await page.inner_text('body')
            if any(x in page_text_early.lower() for x in ['checking your browser', 'just a moment', 'enable javascript', 'ray id', 'cloudflare']):
                debug_info.append("Detected Cloudflare challenge, waiting longer...")
                await asyncio.sleep(8)  # Wait for challenge to complete
            # Handle cookies
            for selector in ['button:has-text("Accept all")', 'button:has-text("Accept")', '#onetrust-accept-btn-handler']:
                try:
                    cookie_btn = page.locator(selector).first
                    if await cookie_btn.is_visible(timeout=1500):
                        await short_delay(100, 200)
                        await move_and_click(page, cookie_btn)
                        await short_delay(200, 400)
                        break
                except:
                    continue
            
            # Find input with extended timeout and more selectors
            input_element = None
            input_selectors = [
                'input[data-testid="vrm-input"]',
                'input[name="vrm"]',
                'input[name="registration"]',
                'input[id="vrm"]',
                'input[placeholder*="registration" i]',
                'input[placeholder*="reg" i]',
                'input[placeholder*="number plate" i]',
                'input[aria-label*="registration" i]',
                'input[type="text"][maxlength]',
                'input.vrm-input',
                '#registration-input',
                '[data-cy="vrm-input"] input',
            ]
            
            # Try multiple times with increasing waits
            for attempt in range(3):
                for selector in input_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible(timeout=1500):
                            input_element = element
                            debug_info.append(f"Found input with selector: {selector}")
                            break
                    except:
                        continue
                if input_element:
                    break
                # Wait and retry if not found
                debug_info.append(f"Input not found on attempt {attempt + 1}, waiting...")
                await asyncio.sleep(2)
            
            if not input_element:
                page_text = await page.inner_text('body')
                page_url = page.url
                debug_info.append(f"Final URL: {page_url}")
                debug_info.append(f"Page title: {await page.title()}")
                await browser.close()
                return {"success": False, "error": "Could not find registration input field", "registration": registration, "debug": debug_info, "pageTextSample": page_text[:3000], "finalUrl": page_url}
            
            await short_delay(50, 150)
            await input_element.click()
            await short_delay(30, 80)
            await input_element.fill("")
            await human_type(input_element, registration)
            debug_info.append(f"Typed: {registration}")
            await short_delay(100, 200)
            
            # Find button
            button_element = None
            for selector in ['button[data-testid="vrm-submit"]', 'button:has-text("Find insurance group")', 'button:has-text("Find")', 'button[type="submit"]']:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=800):
                        button_element = element
                        break
                except:
                    continue
            
            if not button_element:
                await browser.close()
                return {"success": False, "error": "Could not find submit button", "registration": registration, "debug": debug_info}
            
            await short_delay(50, 150)
            await move_and_click(page, button_element)
            debug_info.append("Clicked submit")
            # Wait for results
            max_wait, poll_interval, waited, results_loaded = 20, 0.3, 0, False
            while waited < max_wait:
                await asyncio.sleep(poll_interval)
                waited += poll_interval
                page_text = await page.inner_text('body')
                if "unusual requests" in page_text.lower():
                    await browser.close()
                    return {"success": False, "error": "Blocked by Cloudflare", "registration": registration, "debug": debug_info}
                if registration.upper() in page_text.upper() and "retrieving data" not in page_text.lower() and "your car insurance group" in page_text.lower():
                    results_loaded = True
                    debug_info.append(f"Results loaded in {waited:.1f}s")
                    break
                if "couldn't find" in page_text.lower() or "not found" in page_text.lower():
                    break
            
            if not results_loaded:
                page_text = await page.inner_text('body')
                await browser.close()
                return {"success": False, "error": "Timeout waiting for results", "registration": registration, "debug": debug_info, "pageTextSample": page_text[:1500]}
            
            page_text = await page.inner_text('body')
            patterns = [r'Your car insurance group[^\d]*Group\s+(\d+)\s*/\s*(\d+)', r'\(' + registration + r'\)[^\d]*Group\s+(\d+)\s*/\s*(\d+)', r'Group\s+(\d+)\s*/\s*(\d+)']
            group_num, max_group = None, None
            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    group_num, max_group = int(match.group(1)), int(match.group(2))
                    break
            
            await browser.close()
            
            if group_num is not None:
                return {"success": True, "registration": registration, "insuranceGroup": group_num, "maxGroup": max_group, "displayText": f"Group {group_num}/{max_group}"}
            return {"success": False, "error": "Could not find insurance group in response", "registration": registration, "debug": debug_info, "pageTextSample": page_text[:1500]}
    except Exception as e:
        return {"success": False, "error": str(e), "registration": registration, "debug": debug_info}


async def main(registration: str):
    # Retry up to 5 times with different proxy IPs
    max_retries = 5
    for attempt in range(max_retries):
        result = await lookup_insurance_group(registration)
        if result.get("success"):
            print(json.dumps(result))
            return
        # Check if it's a Cloudflare block or retryable error - retry with new IP
        page_sample = result.get("pageTextSample", "").lower()
        error_msg = result.get("error", "").lower()
        is_cloudflare_block = (
            "cloudflare" in page_sample or
            "cloudflare" in error_msg or
            "unusual requests" in page_sample or
            "unblock challenges" in page_sample or
            "ray id" in page_sample or
            "checking your browser" in page_sample or
            "just a moment" in page_sample
        )
        # Also retry if input field not found (could be blocked page)
        is_input_not_found = "could not find registration input" in error_msg
        
        if (is_cloudflare_block or is_input_not_found) and attempt < max_retries - 1:
            # Wait a bit before retrying with new proxy IP
            result["debug"] = result.get("debug", []) + [f"Retrying (attempt {attempt + 2}/{max_retries})..."]
            await asyncio.sleep(2)
            continue
        # For other errors or last attempt, don't retry
        break
    print(json.dumps(result))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Missing registration argument"}))
        sys.exit(1)
    asyncio.run(main(sys.argv[1].strip().upper()))