import asyncio
from crawl4ai import AsyncWebCrawler
from googlesearch import search

async def scrape_web(queries, num_results=3):
    urls = []
    for query in queries:
        try:
            urls.extend(list(search(query, num_results=num_results)))
        except Exception as e:
            print(f"Error searching for {query}: {e}")
    async with AsyncWebCrawler() as crawler:
        results = []
        for url in urls:
            try:
                result = await crawler.arun(url=url)
                if result.markdown and len(result.markdown) > 500:  # Filter as in the working code
                    results.append({'url': url, 'content': result.markdown})
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        return results

def scrape_web_sync(queries):
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If no event loop exists, create and set a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    # Run the async function using the event loop
    return loop.run_until_complete(scrape_web(queries))