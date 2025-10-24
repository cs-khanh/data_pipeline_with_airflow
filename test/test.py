from datetime import datetime, timedelta

date_str = "2025-10-01"
dt = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)

message = f"Next date: {dt.strftime('%Y-%m-%d')}"
print(message)