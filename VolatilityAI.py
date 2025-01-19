import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

# 假設你的數據已經存儲在一個 CSV 文件 volatility_data.csv 中
data = pd.read_csv('volatility_data.csv', parse_dates=['Date'], index_col='Date')

# 選擇要用於預測的特徵
features = ['Volatility']

# 將數據正規化
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data[features])

# 創建訓練數據集
train_data = []
train_labels = []
for i in range(60, len(scaled_data)):
    train_data.append(scaled_data[i-60:i, 0])
    train_labels.append(scaled_data[i, 0])
train_data, train_labels = np.array(train_data), np.array(train_labels)

# 重塑數據以符合 LSTM 的輸入要求
train_data = np.reshape(train_data, (train_data.shape[0], train_data.shape[1], 1))

# 創建 LSTM 模型
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(train_data.shape[1], 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

# 編譯模型
model.compile(optimizer='adam', loss='mean_squared_error')

# 訓練模型
model.fit(train_data, train_labels, batch_size=1, epochs=1)

# 使用模型進行預測（以最近60天的數據為例）
last_60_days = data[-60:].values
last_60_days_scaled = scaler.transform(last_60_days)
X_test = []
X_test.append(last_60_days_scaled)
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

predicted_volatility = model.predict(X_test)
predicted_volatility = scaler.inverse_transform(predicted_volatility)

# 繪製預測結果
plt.figure(figsize=(16, 8))
plt.title('Predicted Volatility')
plt.plot(data.index, data['Volatility'], label='Actual Volatility')
plt.plot(data.index[-1] + pd.Timedelta(days=1), predicted_volatility[0], 'ro', label='Predicted Volatility')
plt.xlabel('Date')
plt.ylabel('Volatility')
plt.legend()
plt.show()
