import random
import csv
 
# average km per day for each usage pattern
# patterns 1, 2, 3 and 5, 7, 8 are scaled using real averages
# from the 197-response survey (only used categories with enough
# replies). patterns 4 and 6 kept as estimates (not enough survey
# data for those specific cases).
pattern_daily_km = {
    1: 31,
    2: 49,
    3: 107,
    4: 150,
    5: 29,
    6: 70,
    7: 39,
    8: 16
}
 
intervals = [5000, 7500, 10000]
 
rows = []
 
for i in range(500):
    pattern = random.randint(1, 8)
    interval = random.choice(intervals)
    base_km = pattern_daily_km[pattern]
 
    # add some random noise so not everyone is exactly the same
    noise = random.uniform(-8, 8)
    real_km = base_km + noise
    if real_km < 1:
        real_km = 1
 
    rows.append([pattern, interval, round(real_km, 1)])
 
with open("training_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["usage_pattern", "preferred_interval", "km_per_day"])
    writer.writerows(rows)
 
print("done, made", len(rows), "rows")




