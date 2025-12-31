import sys
import json
import asyncio
import os
import re
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()

TARGET_URL = "https://www.moneysupermarket.com/car-insurance/car-insurance-group-checker-tool/"

# Firefox-compatible user agents only
USER_AGENTS = [
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "platform": "Win32", "os": "Windows"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0; rv:121.0) Gecko/20100101 Firefox/121.0", "platform": "MacIntel", "os": "macOS"},
    {"ua": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0", "platform": "Linux x86_64", "os": "Linux"},
    {"ua": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0", "platform": "Linux x86_64", "os": "Linux"},
    {"ua": "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0", "platform": "Linux x86_64", "os": "Linux"},
]

SCREEN_CONFIGS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1680, "height": 1050},
    {"width": 2560, "height": 1440},
    {"width": 1280, "height": 720},
    {"width": 1600, "height": 900},
    {"width": 1280, "height": 800},
]

LOCALE_CONFIGS = [
    {"locale": "en-GB", "timezone": "Europe/London"},
]

ACCEPT_LANGUAGES = ["en-GB,en;q=0.9", "en-GB,en-US;q=0.9,en;q=0.8"]


def generate_random_fingerprint():
    ua_config = random.choice(USER_AGENTS)
    screen = random.choice(SCREEN_CONFIGS)
    locale_config = random.choice(LOCALE_CONFIGS)
    accept_language = random.choice(ACCEPT_LANGUAGES)
    
    return {
        "user_agent": ua_config["ua"],
        "platform": ua_config["platform"],
        "os_type": ua_config["os"],
        "viewport": {"width": screen["width"], "height": screen["height"]},
        "locale": locale_config["locale"],
        "timezone": locale_config["timezone"],
        "accept_language": accept_language,}


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


def is_cloudflare_challenge(page_title: str, page_text: str) -> bool:
    """Check if the page is a Cloudflare challenge page."""
    title_lower = page_title.lower() if page_title else ""
    text_lower = page_text.lower() if page_text else ""
    
    cloudflare_indicators = [
        "just a moment",
        "checking your browser",
        "please wait",
        "ddos protection",
        "cloudflare",
        "ray id",
        "enable javascript",
        "unusual activity",
        "security check",
        "attention required",
    ]
    
    return any(indicator in title_lower or indicator in text_lower[:500] for indicator in cloudflare_indicators)


async def verify_proxy_ip(page, debug_info: list) -> str:
    """Verify the proxy is working by checking the IP address."""
    try:
        await page.goto("https://api.ipify.org?format=json", timeout=15000)
        content = await page.content()
        # Extract IP from JSON response
        ip_match = re.search(r'"ip"\s*:\s*"([^"]+)"', content)
        if ip_match:
            ip = ip_match.group(1)
            debug_info.append(f"Proxy IP verified: {ip}")
            return ip
        # Try plain text format
        text = await page.inner_text('body')
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', text.strip()):
            debug_info.append(f"Proxy IP verified: {text.strip()}")
            return text.strip()
        debug_info.append("Could not parse IP from response")
        return ""
    except Exception as e:
        debug_info.append(f"IP verification failed: {str(e)[:50]}")
        return ""


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
    debug_info = [f"Fingerprint: {fingerprint['user_agent'][:60]}... | {fingerprint['os_type']}"]
    if proxy_config:
        debug_info.append(f"Using proxy: {proxy_host}:{proxy_port}")
    else:
        debug_info.append("No proxy configured")
    
    try:
        async with async_playwright() as p:
            # Use Firefox - better for bypassing bot detection on VPS
            browser_args = {
                "headless": True,
                "firefox_user_prefs": {
                    # Disable telemetry
                    "toolkit.telemetry.enabled": False,
                    "datareporting.healthreport.uploadEnabled": False,
                    # Disable webdriver detection
                    "dom.webdriver.enabled": False,
                    # Performance settings
                    "network.http.pipelining": True,
                    "network.http.proxy.pipelining": True,
                },}
            if proxy_config:
                browser_args["proxy"] = proxy_config
            
            browser = await p.firefox.launch(**browser_args)
            
            context = await browser.new_context(
                viewport=fingerprint["viewport"],
                user_agent=fingerprint["user_agent"],
                locale=fingerprint["locale"],
                timezone_id=fingerprint["timezone"],
                color_scheme="light",
                geolocation={"latitude": 51.5074 + random.uniform(-0.1, 0.1), "longitude": -0.1278 + random.uniform(-0.1, 0.1)},
                permissions=["geolocation"],
                extra_http_headers={
                    "Accept-Language": fingerprint["accept_language"],
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                },
            )
            
            page = await context.new_page()
            
            # Verify proxy is working by checking IP
            if proxy_config:
                await verify_proxy_ip(page, debug_info)
            
            # Navigate to target URL
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            debug_info.append("Page loaded")
            
            # Wait for page to stabilize (2 seconds as requested)
            await asyncio.sleep(2)
            
            # EARLY Cloudflare detection - fail fast if blocked
            page_title = await page.title()
            page_text_early = await page.inner_text('body')
            
            if is_cloudflare_challenge(page_title, page_text_early):
                debug_info.append(f"Cloudflare challenge detected (title: {page_title})")
                await browser.close()
                return {
                    "success": False,
                    "error": "Blocked by Cloudflare",
                    "cloudflare_blocked": True,
                    "registration": registration,
                    "debug": debug_info,
                    "pageTitle": page_title,
                }
            
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
            
            # Try to find input (single attempt, no retries - fail fast)
            for selector in input_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        input_element = element
                        debug_info.append(f"Found input with selector: {selector}")
                        break
                except:
                    continue
            
            if not input_element:
                page_text = await page.inner_text('body')
                page_url = page.url
                page_title = await page.title()
                debug_info.append(f"Final URL: {page_url}")
                debug_info.append(f"Page title: {page_title}")
                await browser.close()
                
                # Check if this is actually a Cloudflare block we missed
                if is_cloudflare_challenge(page_title, page_text):
                    return {
                        "success": False,
                        "error": "Blocked by Cloudflare",
                        "cloudflare_blocked": True,
                        "registration": registration,
                        "debug": debug_info,
                        "pageTitle": page_title,
                    }
                
                return {
                    "success": False,
                    "error": "Could not find registration input field",
                    "registration": registration,
                    "debug": debug_info,
                    "pageTextSample": page_text[:3000],
                    "finalUrl": page_url,
                }
            
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
                
                # Check for Cloudflare block during results wait
                page_title = await page.title()
                if is_cloudflare_challenge(page_title, page_text):
                    await browser.close()
                    return {
                        "success": False,
                        "error": "Blocked by Cloudflare",
                        "cloudflare_blocked": True,
                        "registration": registration,
                        "debug": debug_info,
                    }
                
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
        
        # Check if it's a Cloudflare block - retry with new IP
        is_cloudflare_block = result.get("cloudflare_blocked", False)
        
        if is_cloudflare_block and attempt < max_retries - 1:
            # Add retry info to debug
            result["debug"] = result.get("debug", []) + [f"Cloudflare blocked, retrying (attempt {attempt + 2}/{max_retries})..."]
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