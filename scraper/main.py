"""
VerdictFinder Scraper — Supreme Court of India
================================================
Usage:
    python main.py            # scrape 1 test case, own IP
    python main.py --tor      # scrape 1 test case, route through Tor (Tor must be running)
    python main.py --count 5  # scrape first 5 cases

First run: solve the CAPTCHA manually when the browser pauses.
"""

import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, BrowserContext, Page

from config import (
    HOME_URL, SEARCH_URL, BASE_URL,
    OUTPUT_DIR, LOG_DIR,
    VIEWPORTS, USER_AGENTS, TOR_PROXY, PROFILE_DIR,
)
from human import (
    random_delay,
    human_hover_and_click,
    simulate_reading,
    human_scroll,
)

import random


# ── Logging ───────────────────────────────────────────────────────────────────

def _setup_logging() -> logging.Logger:
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    stamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(LOG_DIR) / f"scrape_{stamp}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
    return logging.getLogger("scraper")


log = _setup_logging()


# ── Stealth JS injected into every page ──────────────────────────────────────

_STEALTH_SCRIPT = """
    // Hide automation signals
    Object.defineProperty(navigator, 'webdriver',  { get: () => undefined });
    Object.defineProperty(navigator, 'plugins',    { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages',  { get: () => ['en-IN', 'en-US', 'en'] });
    Object.defineProperty(navigator, 'platform',   { get: () => 'Win32' });

    // Fake Chrome runtime so bot-detector scripts see a "real" Chrome
    window.chrome = { runtime: {}, loadTimes: function(){}, csi: function(){} };

    // Permissions API — return real notification state rather than throwing
    const _origPermQuery = window.navigator.permissions.query.bind(navigator.permissions);
    window.navigator.permissions.query = (params) =>
        params.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : _origPermQuery(params);
"""


# ── Browser factory ───────────────────────────────────────────────────────────

async def create_browser(playwright, use_tor: bool = False):
    """
    Launch Chromium with a PERSISTENT profile stored in scraper/browser_profile/.

    On first run the folder is created fresh.
    Every subsequent run reuses it — cookies, cache, localStorage, and
    browsing history accumulate, making the browser look like a returning
    human visitor rather than a bot opening a brand-new browser.
    """
    profile_path = Path(__file__).parent / PROFILE_DIR
    profile_path.mkdir(parents=True, exist_ok=True)

    # Pick a stable fingerprint. Because the profile persists, we keep the
    # same viewport/UA across runs (a real person doesn't change screen size
    # every session). We store the choice in a small JSON file.
    fp_file = profile_path / "fingerprint.json"
    if fp_file.exists():
        fp = json.loads(fp_file.read_text())
        viewport   = fp["viewport"]
        user_agent = fp["user_agent"]
        log.info("Loaded existing browser fingerprint from profile.")
    else:
        viewport   = random.choice(VIEWPORTS)
        user_agent = random.choice(USER_AGENTS)
        fp_file.write_text(json.dumps({"viewport": viewport, "user_agent": user_agent}))
        log.info("Created new browser fingerprint and saved to profile.")

    log.info(f"Profile  : {profile_path}")
    log.info(f"Viewport : {viewport['width']}x{viewport['height']}")
    log.info(f"UserAgent: {user_agent[:72]}...")

    launch_kwargs = dict(
        headless=False,          # visible window — required for manual CAPTCHA
        viewport=viewport,
        user_agent=user_agent,
        accept_downloads=True,
        locale="en-IN",
        timezone_id="Asia/Kolkata",
        extra_http_headers={
            "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "DNT": "1",
        },
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
        ],
    )

    if use_tor:
        launch_kwargs["proxy"] = {"server": TOR_PROXY}
        log.info(f"Routing traffic through Tor ({TOR_PROXY})")

    # launch_persistent_context returns a BrowserContext directly (not a Browser)
    context = await playwright.chromium.launch_persistent_context(
        str(profile_path),
        **launch_kwargs,
    )

    # Inject stealth overrides before any page script runs
    await context.add_init_script(_STEALTH_SCRIPT)

    return context


# ── CAPTCHA pause ─────────────────────────────────────────────────────────────

async def wait_for_captcha(page: Page) -> None:
    log.info("━" * 62)
    log.info("  CAPTCHA DETECTED")
    log.info("  Solve it in the browser window, then press ENTER here.")
    log.info("━" * 62)
    # run_in_executor lets us await a blocking input() call
    await asyncio.get_event_loop().run_in_executor(
        None, input, "\n  >>> Press ENTER after solving the CAPTCHA: "
    )
    log.info("Resuming after CAPTCHA...")
    await random_delay(1.5, 3.0)


# ── Debug helper ──────────────────────────────────────────────────────────────

async def save_debug_html(page: Page, label: str = "debug") -> Path:
    html  = await page.content()
    stamp = datetime.now().strftime("%H%M%S")
    path  = Path(LOG_DIR) / f"{label}_{stamp}.html"
    path.write_text(html, encoding="utf-8")
    log.info(f"Debug HTML → {path}")
    return path


# ── Result-page parsing ───────────────────────────────────────────────────────

async def find_pdf_buttons(page: Page) -> list:
    """
    Try a priority list of selectors to locate VIEW-PDF links/buttons.
    Returns the matched element list (possibly empty).
    """
    selectors = [
        "a[href*='.pdf']",
        "a[href*='PDF']",
        "a[href*='viewpdf']",
        "a[href*='view_pdf']",
        "a[href*='getpdf']",
        "a:has-text('VIEW PDF')",
        "a:has-text('View PDF')",
        "a:has-text('PDF')",
        "button:has-text('PDF')",
        "input[type='button'][value*='PDF']",
        "a[target='_blank']",
    ]

    for sel in selectors:
        try:
            elements = await page.query_selector_all(sel)
            if elements:
                log.info(f"Found {len(elements)} PDF link(s) via: {sel!r}")
                return elements
        except Exception:
            continue

    # Fallback: inspect all <a> tags for PDF-looking href / text
    log.warning("Standard selectors found nothing — scanning all <a> tags...")
    all_links = await page.query_selector_all("a[href]")
    found = []
    for link in all_links:
        href = (await link.get_attribute("href") or "").lower()
        text = (await link.inner_text()).lower()
        if "pdf" in href or "pdf" in text or "view" in text:
            found.append(link)

    log.info(f"Fallback scan: {len(found)} candidate link(s)")
    return found


async def extract_table_rows(page: Page) -> list[dict]:
    """Pull text from every <td> in the results table."""
    rows = []
    try:
        await page.wait_for_selector("table", timeout=12000)
        tr_list = await page.query_selector_all("table tbody tr")
        for i, tr in enumerate(tr_list):
            cells    = await tr.query_selector_all("td")
            row_data = {"row_index": i}
            for j, td in enumerate(cells):
                row_data[f"col_{j}"] = (await td.inner_text()).strip()
            rows.append(row_data)
        log.info(f"Table: {len(rows)} row(s) extracted")
    except Exception as exc:
        log.warning(f"Table extraction skipped: {exc}")
    return rows


# ── PDF capture ───────────────────────────────────────────────────────────────

async def capture_pdf(
    page: Page,
    context: BrowserContext,
    element,
) -> tuple[bytes | None, str]:
    """
    Click `element` and capture the PDF via whichever mechanism the site uses:
      1. New tab  — most common for government portals
      2. Download — if the server sends Content-Disposition: attachment
    Returns (pdf_bytes, suggested_filename).
    """

    # ── Attempt 1: new tab ────────────────────────────────────────────────────
    try:
        async with context.expect_page(timeout=8_000) as new_page_info:
            await element.click()

        new_page = await new_page_info.value
        await new_page.wait_for_load_state("networkidle", timeout=30_000)

        pdf_url = new_page.url
        log.info(f"PDF opened in new tab: {pdf_url}")

        response = await new_page.goto(pdf_url)
        content  = await response.body() if response else None

        filename = pdf_url.rstrip("/").split("/")[-1]
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        await new_page.close()
        return content, filename

    except Exception as exc_tab:
        log.info(f"New-tab approach: {exc_tab} — trying download handler...")

    # ── Attempt 2: browser download ───────────────────────────────────────────
    try:
        async with page.expect_download(timeout=12_000) as dl_info:
            await element.click()

        download = await dl_info.value
        tmp_path = await download.path()
        filename = download.suggested_filename or "case.pdf"

        with open(tmp_path, "rb") as f:
            content = f.read()

        log.info(f"PDF captured via download: {filename} ({len(content):,} bytes)")
        return content, filename

    except Exception as exc_dl:
        log.error(f"Download approach also failed: {exc_dl}")
        return None, "case.pdf"


# ── Save to disk ──────────────────────────────────────────────────────────────

def save_pdf(content: bytes, filename: str, index: int) -> Path:
    safe   = re.sub(r"[^\w\-.]", "_", filename)
    stamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    name   = f"{index:04d}_{stamp}_{safe}"
    path   = Path(OUTPUT_DIR) / name
    path.write_bytes(content)
    log.info(f"Saved: {path}  ({len(content):,} bytes)")
    return path


def save_metadata(row_data: dict, pdf_path: Path) -> None:
    meta_path = Path(LOG_DIR) / (pdf_path.stem + ".json")
    row_data["pdf_file"] = str(pdf_path)
    row_data["scraped_at"] = datetime.now().isoformat()
    meta_path.write_text(json.dumps(row_data, indent=2, ensure_ascii=False))
    log.info(f"Metadata: {meta_path}")


# ── Main entry point ──────────────────────────────────────────────────────────

async def run(count: int = 1, use_tor: bool = False) -> None:
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        context = await create_browser(p, use_tor=use_tor)
        page = await context.new_page()

        try:
            # ── 1. Homepage (CAPTCHA gate) ────────────────────────────────
            log.info(f"Opening homepage: {HOME_URL}")
            await page.goto(HOME_URL, wait_until="domcontentloaded", timeout=30_000)
            await random_delay(2.0, 4.0)

            await wait_for_captcha(page)

            # ── 2. Search results page ────────────────────────────────────
            log.info(f"Loading search results: {SEARCH_URL}")
            await page.goto(SEARCH_URL, wait_until="networkidle", timeout=30_000)
            await random_delay(2.5, 5.5)

            # Human: spend a moment reading the page
            await simulate_reading(page, duration=random.uniform(3.0, 6.0))

            # ── 3. Locate PDF buttons ─────────────────────────────────────
            pdf_buttons = await find_pdf_buttons(page)

            if not pdf_buttons:
                log.error("No PDF links found — saving debug HTML for inspection.")
                await save_debug_html(page, "no_pdf_links")
                return

            # Pull table metadata for context
            table_rows = await extract_table_rows(page)

            # ── 4. Scrape N cases ─────────────────────────────────────────
            target_count = min(count, len(pdf_buttons))
            log.info(f"Scraping {target_count} case(s) from {len(pdf_buttons)} found...")

            for i in range(target_count):
                log.info(f"\n{'─'*50}")
                log.info(f"Case {i+1} / {target_count}")

                # Random pre-click reading pause
                await random_delay(1.5, 4.0)
                await human_scroll(page)
                await random_delay(0.5, 1.5)

                btn = pdf_buttons[i]

                # Human-like hover → click
                await human_hover_and_click(page, btn)

                # Capture the PDF
                pdf_bytes, filename = await capture_pdf(page, context, btn)

                if pdf_bytes and len(pdf_bytes) > 512:
                    pdf_path = save_pdf(pdf_bytes, filename, i + 1)
                    row_meta = table_rows[i] if i < len(table_rows) else {}
                    save_metadata(row_meta, pdf_path)
                else:
                    log.error(f"Case {i+1}: empty or missing PDF content.")
                    await save_debug_html(page, f"case_{i+1:04d}_failed")

                # Inter-case delay — longer for more cases to stay under radar
                if i < target_count - 1:
                    gap = random.uniform(4.0, 10.0)
                    log.info(f"Waiting {gap:.1f}s before next case...")
                    await asyncio.sleep(gap)

            log.info("\n" + "━" * 62)
            log.info(f"  Done — {target_count} case(s) scraped.")
            log.info(f"  PDFs → {Path(OUTPUT_DIR).resolve()}")
            log.info("━" * 62)

        except Exception as exc:
            log.error(f"Fatal error: {exc}", exc_info=True)
            try:
                await save_debug_html(page, "fatal_error")
            except Exception:
                pass

        finally:
            await random_delay(2.0, 4.0)
            await context.close()   # closes the persistent context (and its browser)
            log.info("Browser closed. Profile saved to browser_profile/")


# ── CLI arg parsing ───────────────────────────────────────────────────────────

def _parse_args() -> tuple[int, bool]:
    args    = sys.argv[1:]
    use_tor = "--tor" in args
    count   = 1

    if "--count" in args:
        idx = args.index("--count")
        try:
            count = int(args[idx + 1])
        except (IndexError, ValueError):
            log.warning("--count requires a number. Defaulting to 1.")

    return count, use_tor


if __name__ == "__main__":
    n, tor = _parse_args()
    log.info(f"Starting scraper | cases={n} | tor={tor}")
    asyncio.run(run(count=n, use_tor=tor))
