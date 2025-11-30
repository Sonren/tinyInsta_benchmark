import asyncio
import aiohttp
import csv
import time
import os
from statistics import mean

params = [1, 10, 20, 50, 100, 1000]
runs = 3
base_url = "https://tinyinstagramtp1dm.ew.r.appspot.com/api/timeline"
csv_file = "outAsync/conc.csv"

os.makedirs("outAsync", exist_ok=True)


async def fetch_timeline(session, user_id, semaphore):
    """Fetch the timeline for a specific user."""
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


async def run_benchmark(concurrency, amount):
    """Run the benchmark with a given concurrency level."""
    semaphore = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_timeline(session, user_id=i + 1, semaphore=semaphore)
            for i in range(amount)
        ]
        results = await asyncio.gather(*tasks)

    durations = [r[0] for r in results]
    failures = sum(1 for r in results if not r[1])
    avg_time = mean(durations)

    return avg_time, failures


async def main():
    print("Benchmark Start - TinyInsta Timeline API")

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PARAM", "AVG_TIME", "RUN", "FAILED"])

        total_tests = len(params) * runs
        current_test = 0

        for concurrency in params:
            amount = concurrency
            for run_id in range(1, runs + 1):
                current_test += 1
                avg_time, failed = await run_benchmark(concurrency, amount)

                writer.writerow([concurrency, round(avg_time, 2), run_id, failed])
                print(f"Saved: {concurrency} users, avg={avg_time:.2f}ms, run={run_id}, failed={failed}")

                if current_test < total_tests:
                    await asyncio.sleep(2)

    print("Benchmark Completed")


if __name__ == "__main__":
    asyncio.run(main())
