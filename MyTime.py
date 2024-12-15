# can not name "time.py", or cause bug 
from datetime import datetime, time

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

print("time =", current_datetime.time().hour)

# 定義起點時間：公元 1 年 1 月 1 日
epoch = datetime(1, 1, 1)

# 獲取當前時間
now = datetime.now()

# 計算從起點到當前時間的天數
time_difference = now - epoch
start_date = (epoch - epoch).days + 1
days_since_epoch = time_difference.days + 1 # 直接以天為單位

# 打印 64 位時間戳（天級）
print("64 位時間戳起點 (天級):", start_date) # 0001-01-01
print("64 位時間戳（天級）:", days_since_epoch)
'''
每400年有97個閏年 = 146,097天
如果2001-01-01 是星期1
=> 0001-01-01 也是星期1
'''
print("星期", days_since_epoch % 7) # 星期日 回傳 0


print(type(current_datetime), current_datetime) # YYYY-MM-DD hh:mm:ss.us
print(type(current_datetime.time()), current_datetime.time()) # hh:mm:ss.us
print(type(time(3, 30)), time(3, 30)) # 自訂的 hh:mm:ss

if current_datetime.time() > time(3, 30) and current_datetime.time() < time(4, 0):
    print(1)
elif current_datetime.time() > time(4, 0) and current_datetime.time() < time(4, 30):
    print(2)
else:
    print(3)