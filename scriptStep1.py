import subprocess
import csv
import re
import os


params = [1, 10, 20, 50, 100, 1000]  #parameters we want to try 
runs = 3
url = "https://tinyinstagramtp1dm.ew.r.appspot.com/api/timeline?user=user1&limit=20"

csv_file = "out/conc.csv" #path to the csv exit file

write_header = not os.path.exists(csv_file)

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)

    if write_header:
        writer.writerow(["PARAM", "AVG_TIME", "RUN",  "FAILED"]) #header of the csv


    for concurrent in params:
        amount = concurrent 
        for r in range(1, runs + 1):
            print(f"Running test: {concurrent} concurrent, run {r}...")

            result = subprocess.run(
                ["ab", "-n", str(amount), "-c", str(concurrent), url], #here -n is the number of simulated requests, -c is the number of concurrent users
                capture_output=True,
                text=True
            )
            output = result.stdout

            match_lat = re.search(
                r"Time per request:\s+([\d\.]+)\s+\[ms\]\s+\(mean\)", 
                output
            )
            avg_lat = float(match_lat.group(1)) if match_lat else None

            match_fail = re.search(r"Non-2xx responses:\s+(\d+)", output)
            failed = int(match_fail.group(1)) if match_fail else 0

            writer.writerow([concurrent, avg_lat, r, failed])
            print(f"Done: AVG_LAT={avg_lat} ms, FAILED={failed}")
