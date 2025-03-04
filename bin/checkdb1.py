from datetime import datetime

timestamp = "2025-02-17T22:53:45.843878"

# Convert it correctly
time_achieved = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")

print(time_achieved)  # ✅ Should now work!
