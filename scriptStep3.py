import asyncio
import aiohttp
import csv
import time
import os
from statistics import mean

param = 100
concurrency = 50
total_requests = 1000
runs = 3
base_url = "https://tinyinstagramtp1dm.ew.r.appspot.com/api/timeline"
csv_file = "outAsync/fanout.csv"

os.makedirs("outAsync", exist_ok=True)


async def fetch_timeline(session, user_id, semaphore):
    """Fetch timeline for a specific user."""
    async with semaphore:
        url = f"{base_url}?user=user{user_id}&limit=20"
        start = time.time()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                await response.text()
                duration = (time.time() - start) * 1000
                success = 200 <= response.status < 300
                return duration, success
        except Exception:
            duration = (time.time() - start) * 1000
            return duration, False


async def run_benchmark(concurrency, total_requests):
    """Run benchmark with specified concurrency."""
    semaphore = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_timeline(session, user_id=i + 1, semaphore=semaphore)
            for i in range(total_requests)
        ]
        results = await asyncio.gather(*tasks)

    durations = [r[0] for r in results]
    failures = sum(1 for r in results if not r[1])
    avg_time = mean(durations)

    return avg_time, failures


async def main():
    print("Benchmark Start - Fanout Scaling Test")

    write_header = not os.path.exists(csv_file)

    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)

        if write_header:
            writer.writerow(["PARAM", "AVG_TIME", "RUN", "FAILED"])

        for r in range(1, runs + 1):
            avg_time, failed = await run_benchmark(concurrency, total_requests)
            writer.writerow([param, round(avg_time, 2), r, failed])

            print(f"Saved: param={param}, avg={avg_time:.2f}ms, run={r}, failed={failed}")

            if r < runs:
                await asyncio.sleep(2)

    print("Benchmark Completed")


if __name__ == "__main__":
    asyncio.run(main())
