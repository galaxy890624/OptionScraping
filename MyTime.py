# can not name "time.py", or cause bug 
from datetime import datetime

# Get the current date and time
current_datetime = datetime.now()

# Extract components separately
year = current_datetime.year
month = current_datetime.month
day = current_datetime.day
hour = current_datetime.hour
minute = current_datetime.minute
second = current_datetime.second

# Print each component
print("Year:", year)
print("Month:", month)
print("Day:", day)
print("Hour:", hour)
print("Minute:", minute)
print("Second:", second)