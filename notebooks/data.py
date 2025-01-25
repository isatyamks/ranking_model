import pandas as pd
import numpy as np

data = pd.read_csv("..\\data\\soapnutshistory.csv")
data.fillna(method='ffill', inplace=True)



from sklearn.preprocessing import MinMaxScaler


scaler = MinMaxScaler()
data[['Product Price', 'Organic Conversion Percentage', 
      'Ad Conversion Percentage', 'Total Profit', 
      'Total Sales']] = scaler.fit_transform(data[['Product Price', 
                                                    'Organic Conversion Percentage', 
                                                    'Ad Conversion Percentage', 
                                                    'Total Profit', 
                                                    'Total Sales']])

data['Report Date'] = pd.to_datetime(data['Report Date'])
data['Day'] = data['Report Date'].dt.day
data['Month'] = data['Report Date'].dt.month

data['Day_sin'] = np.sin(2 * np.pi * data['Day'] / 30)
data['Day_cos'] = np.cos(2 * np.pi * data['Day'] / 30)
data['Month_sin'] = np.sin(2 * np.pi * data['Month'] / 12)
data['Month_cos'] = np.cos(2 * np.pi * data['Month'] / 12)
