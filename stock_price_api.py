import requests
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error, r2_score
import matplotlib.pyplot as plt

##### 
#    Used my API key to get the data, extracted the JSON file
#    Run this section of the code separately ('creating the JSON file from the API')
#    Comment the code after the file is created   
#    Save the CSV file later
#####

# url = 'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol=IBM&apikey=40DM9ER64D42F2RN'
# r = requests.get(url)
# if r.status_code == 200:
#     data = r.json()

#     with open('raw_data.json', 'w') as json_file:
#         json.dump(data, json_file, indent=4)

# else:
#     print('Failed to create the file!')

with open('E:/ML tutorials/ML Projects/Stock Price Prediction/stock_data.json', 'r') as json_file:
    data = json.load(json_file)

if 'Weekly Adjusted Time Series' in data:
    stock_data = data['Weekly Adjusted Time Series']

df = pd.DataFrame.from_dict(stock_data, orient='index', dtype=float) #converting the dates to index from the dictionary keys

df.columns = ['Open', 'High', 'Low', 'Close', 'Adjusted Close', 'Volume', 'Dividend Amount']
df.index = pd.to_datetime(df.index) # convertin the date into pandas datetime object
df = df.astype(float)
df.sort_index(inplace=True) # sorting from the old to new data

# df.to_csv('stocks_adjusted_weekly.csv')


df['HL_PCT'] = (df['High'] - df['Low']) / df['Open'] * 100      # dividing by open to see the change relative to the starting price
df['PCT_Chng'] = (df['Close'] - df['Open']) / df['Open'] * 100  # using the % change of open and close price
df = df[['PCT_Chng', 'HL_PCT', 'Volume', 'Adjusted Close']]     # columns used for the prediction

forecast_col = 'Adjusted Close'           
df['label'] = df[forecast_col].shift(-10) # moving adjusted close price to 10 weeks in the future
df.dropna(inplace=True)                   # dropping NaN values
X = np.array(df.drop('label', axis=1))
y = np.array(df['label'])

#splitting dataset 75% for training and 25% for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=1)

scaler = StandardScaler() # scaling data for better training
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = LinearRegression() # using simple LinearRegression
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
error = root_mean_squared_error(y_test, y_pred) # calculating Root Mean Sqaured Error, R2-score, and Standard Deviation to evaluate the model
r2 = r2_score(y_test, y_pred) 
std = df[forecast_col].std()
print('RMSE: ', error,'\nR2 Score: ', r2, '\nStandard Deviation: ', std)

plt.figure(figsize=(8,5))
plt.plot(df.index[-len(y_test[-50:]):], y_test[-50:], label='Actual Data') # only plotting the recent 50 weeks
plt.plot(df.index[-len(y_test[-50:]):], y_pred[-50:], label='Predicted Data', alpha=0.7)
plt.xlabel('Date')
plt.ylabel('Adjusted Close')
plt.legend(loc='upper right')
plt.title('Stock Market Price Prediction')
plt.show()