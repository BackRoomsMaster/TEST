import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from collections import defaultdict
import time
import sys
import os

API_KEY = "7Mfs5AGoTDiSouhN"  # Sostituisci con la tua chiave API
BASE_URL = "https://api.torn.com"

def get_api_data(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}?key={API_KEY}"
    if params:
        url += "&" + "&".join([f"{k}={v}" for k, v in params.items()])
    response = requests.get(url)
    return response.json()

def analyze_stock_market():
    stocks_data = get_api_data("market", {"type": "stocks"})
    
    df = pd.DataFrame(stocks_data['stocks'].values())
    
    df['daily_return'] = (df['current_price'] - df['previous_price']) / df['previous_price'] * 100
    df['weekly_return'] = (df['current_price'] - df['price_1w']) / df['price_1w'] * 100
    df['monthly_return'] = (df['current_price'] - df['price_4w']) / df['price_4w'] * 100
    
    df['cv'] = df['current_price'].std() / df['current_price'].mean() * 100
    
    df.to_csv('stock_data.csv', index=False)
    return df

def analyze_item_market():
    items_data = get_api_data("market", {"type": "bazaar"})
    
    df = pd.DataFrame(items_data['bazaar'].items(), columns=['item_id', 'data'])
    df = pd.concat([df.drop(['data'], axis=1), df['data'].apply(pd.Series)], axis=1)
    
    df['avg_price'] = df['cost'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    df['median_price'] = df['cost'].apply(lambda x: pd.Series(x).median() if len(x) > 0 else 0)
    df['price_range'] = df['cost'].apply(lambda x: max(x) - min(x) if len(x) > 1 else 0)
    
    df['price_diff_percent'] = df['cost'].apply(lambda x: (max(x) - min(x)) / min(x) * 100 if len(x) > 1 else 0)
    
    df.to_csv('item_data.csv', index=False)
    return df

def analyze_auctions():
    auctions_data = get_api_data("market", {"type": "itemmarket"})
    
    df = pd.DataFrame(auctions_data['itemmarket'].items(), columns=['auction_id', 'data'])
    df = pd.concat([df.drop(['data'], axis=1), df['data'].apply(pd.Series)], axis=1)
    
    df['time_left'] = pd.to_timedelta(df['time_left'], unit='s')
    df['end_time'] = datetime.now() + df['time_left']
    
    df['bid_increment'] = df['cost'] - df['base_cost']
    df['bid_increment_percent'] = (df['bid_increment'] / df['base_cost']) * 100
    
    df['bid_count'] = df['bidders'].apply(len)
    
    df.to_csv('auction_data.csv', index=False)
    return df

def analyze_points_price():
    points_data = get_api_data("market", {"type": "pointsmarket"})
    
    df = pd.DataFrame(points_data['pointsmarket'].items(), columns=['listing_id', 'data'])
    df = pd.concat([df.drop(['data'], axis=1), df['data'].apply(pd.Series)], axis=1)
    
    df['price_per_point'] = df['cost'] / df['quantity']
    df['total_value'] = df['quantity'] * df['price_per_point']
    
    df.to_csv('points_data.csv', index=False)
    return df

def main():
    analyze_stock_market()
    analyze_item_market()
    analyze_auctions()
    analyze_points_price()

if __name__ == "__main__":
    main()
