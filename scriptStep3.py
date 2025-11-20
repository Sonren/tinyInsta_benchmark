import subprocess
import csv
import re
import os

url = "https://tinyinstagramtp1dm.ew.r.appspot.com/api/timeline?user=user1&limit=20"

param = 100 #We change the parameter here to match the number of followees
concurrency = 50 #-c
total_requests = 100 #-n
runs = 3

csv_file = "out/fanout.csv" #path to the csv exit file

write_header = not os.path.exists(csv_file)

with open(csv_file, "a", newline="") as f:
    writer = csv.writer(f)

    if write_header:
        writer.writerow(["PARAM", "AVG_TIME", "RUN",  "FAILED"]) #header of the csv

    for r in range(1, runs + 1):

        result = subprocess.run(
            ["ab", "-n", str(total_requests), "-c", str(concurrency), url], # here -n is the number of simulated requests, -c is the number of concurrent users
            capture_output=True,
            text=True
        )
        output = result.stdout

        match_lat = re.search(r"Time per request:\s+([\d\.]+)\s+\[ms\]", output)
        avg_lat = float(match_lat.group(1)) if match_lat else None

        match_fail = re.search(r"Non-2xx responses:\s+(\d+)", output)
        failed = int(match_fail.group(1)) if match_fail else 0

        writer.writerow([param, avg_lat, r, failed])
        print(f"Done: AVG_LAT={avg_lat} ms, FAILED={failed}")
