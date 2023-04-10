import asyncio
import time

import aiohttp

async def make_request(url):
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        async with session.get(url) as response:
            response_time = time.time() - start_time
            print(f"Response time for {url}: {response_time:.2f} seconds")

async def main():
    urls = [
        "http://185.51.121.22:8000/process_string/bmw/us",
        "http://185.51.121.22:8000/process_string/lada/us",
        "http://185.51.121.22:8000/process_string/michelin/us",
        "http://185.51.121.22:8000/process_string/fallout/us",
        "http://185.51.121.22:8000/process_string/italy/us",
    ]
    tasks = []
    for url in urls:
        tasks.append(asyncio.ensure_future(make_request(url)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())