import sys
import asyncio
import subprocess
from crawl4ai import AsyncWebCrawler
from googlesearch import search

# WINDOWS EVENT LOOP FIX
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def _scrape(queries, num_results=3):
    """
    Internal async scraper: fetch URLs and scrape them with AsyncWebCrawler.
    """
    # Deduplicate URLs
    seen_urls = set()
    urls = []
    for query in queries:
        print(f"🔍 Searching for: {query}")
        try:
            for url in search(query, num_results=num_results):
                if url not in seen_urls:
                    seen_urls.add(url)
                    urls.append(url)
        except Exception as e:
            print(f"❌ Error during search '{query}': {e}")

    results = []

    # Attempt scraping, install browsers if needed
    for attempt in range(2):  # try at most twice: before and after install
        try:
            async with AsyncWebCrawler() as crawler:
                for url in urls:
                    print(f"🌐 Scraping: {url}")
                    try:
                        res = await crawler.arun(url=url)
                        # Prefer markdown, fallback to text
                        content = res.markdown.strip() if getattr(res, 'markdown', None) else getattr(res, 'text', '').strip()
                        if content:
                            print(f"✅ Got content ({len(content)} chars)")
                            results.append({'url': url, 'content': content})
                        else:
                            print("⚠️ No usable content, skipping.")
                    except Exception as e_scrape:
                        print(f"❌ Scraping failed for {url}: {e_scrape}")
            break  # success, exit retry loop
        except Exception as e:
            err = str(e)
            if 'BrowserType.launch' in err and attempt == 0:
                print("⚠️ Playwright browser missing. Installing Chromium...")
                try:
                    subprocess.run(["playwright", "install", "chromium"], check=True)
                    print("✅ Playwright browser installed. Retrying scraping...")
                except Exception as install_err:
                    print(f"❌ Failed to install Playwright browser: {install_err}")
                    break
            else:
                print(f"❌ WebCrawler error: {e}")
                break

    return results


def scrape_web_sync(queries, num_results=3):
    """
    Synchronous wrapper around the async scraper.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_scrape(queries, num_results=num_results))
