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
    base_url = "http://185.51.121.22:8000/process_string"
    devices = ['mobile', 'desktop', 'mobile', 'desktop', 'mobile']
    tokens = [
        "116873402439359",
        "116873425585885",
        "116873505697407",
        "116874599893493",
        "116874609805971",
    ]
    emails = [
        "gebamo5450@camplvad.com",
        "nobex39232@aaorsi.com",
        "asdfkjasdfaslkf@gmail.com",
        "yexegi8441@bodeem.com",
        "kisih34724@byorby.com",
    ]
    keyword = "bmw"
    location = "usa"
    country = "usa"

    tasks = []
    for i in range(len(devices)):
        url = f"{base_url}/{keyword}/{location}/{country}/{devices[i]}?token={tokens[i]}&email={emails[i]}"
        tasks.append(asyncio.ensure_future(make_request(url)))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())