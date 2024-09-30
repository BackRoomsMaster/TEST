import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from collections import defaultdict
import time
import sys
import os

API_KEY = "7Mfs5AGoTDiSouhN"
BASE_URL = "https://api.torn.com"

def loading_animation(duration):
    animation = "|/-\\"
    idx = 0
    start = time.time()
    while time.time() - start < duration:
        print(f"\rCaricamento {animation[idx % len(animation)]}", end="")
        idx += 1
        time.sleep(0.1)
    print("\rCaricamento completato!     ")

def get_api_data(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}?key={API_KEY}"
    if params:
        url += "&" + "&".join([f"{k}={v}" for k, v in params.items()])
    response = requests.get(url)
    return response.json()

def analyze_stock_market():
    print("\n--- Analisi Approfondita del Mercato Azionario ---")
    loading_animation(2)
    stocks_data = get_api_data("market", {"type": "stocks"})
    
    df = pd.DataFrame(stocks_data['stocks'].values())
    
    df['daily_return'] = (df['current_price'] - df['previous_price']) / df['previous_price'] * 100
    df['weekly_return'] = (df['current_price'] - df['price_1w']) / df['price_1w'] * 100
    df['monthly_return'] = (df['current_price'] - df['price_4w']) / df['price_4w'] * 100
    
    # Calcolo del coefficiente di variazione (CV)
    df['cv'] = df['current_price'].std() / df['current_price'].mean() * 100
    
    top_performers = df.sort_values('monthly_return', ascending=False).head(10)
    worst_performers = df.sort_values('monthly_return', ascending=True).head(10)
    
    print("\nTop 10 azioni performanti (rendimento mensile):")
    print(top_performers[['name', 'current_price', 'daily_return', 'weekly_return', 'monthly_return']])
    print("\nPeggiori 10 azioni performanti (rendimento mensile):")
    print(worst_performers[['name', 'current_price', 'daily_return', 'weekly_return', 'monthly_return']])
    
    total_volume = df['total_shares'].sum()
    total_market_cap = (df['current_price'] * df['total_shares']).sum()
    print(f"\nVolume totale di scambi: {total_volume:,}")
    print(f"Capitalizzazione totale di mercato: ${total_market_cap:,.2f}")
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x='current_price', y='monthly_return', size='total_shares', hue='cv', palette='viridis')
    plt.title('Prezzo vs Rendimento Mensile (dimensione = volume totale, colore = CV)')
    plt.xlabel('Prezzo Corrente')
    plt.ylabel('Rendimento Mensile (%)')
    plt.savefig('stock_analysis.png')
    plt.close()
    
    df['volatility'] = df[['daily_return', 'weekly_return', 'monthly_return']].std(axis=1)
    volatile_stocks = df.sort_values('volatility', ascending=False).head(10)
    print("\nAzioni più volatili:")
    print(volatile_stocks[['name', 'current_price', 'volatility', 'cv']])

    return df

def analyze_item_market():
    print("\n--- Analisi Approfondita del Mercato degli Oggetti ---")
    loading_animation(2)
    items_data = get_api_data("market", {"type": "bazaar"})
    
    df = pd.DataFrame(items_data['bazaar'].items(), columns=['item_id', 'data'])
    df = pd.concat([df.drop(['data'], axis=1), df['data'].apply(pd.Series)], axis=1)
    
    df['avg_price'] = df['cost'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    df['median_price'] = df['cost'].apply(lambda x: pd.Series(x).median() if len(x) > 0 else 0)
    df['price_range'] = df['cost'].apply(lambda x: max(x) - min(x) if len(x) > 1 else 0)
    
    most_expensive = df.sort_values('avg_price', ascending=False).head(15)
    print("Top 15 oggetti più costosi:")
    print(most_expensive[['name', 'avg_price', 'median_price', 'price_range']])
    
    most_common = df.sort_values('quantity', ascending=False).head(15)
    print("\nTop 15 oggetti più comuni:")
    print(most_common[['name', 'quantity', 'avg_price']])
    
    df['price_diff_percent'] = df['cost'].apply(lambda x: (max(x) - min(x)) / min(x) * 100 if len(x) > 1 else 0)
    
    high_variance = df.sort_values('price_diff_percent', ascending=False).head(15)
    print("\nOggetti con la maggiore variazione di prezzo:")
    print(high_variance[['name', 'price_diff_percent', 'avg_price', 'quantity']])
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x='avg_price', y='quantity', size='price_range', hue='price_diff_percent', palette='viridis')
    plt.title('Prezzo Medio vs Quantità (dimensione = range di prezzo, colore = % diff prezzo)')
    plt.xlabel('Prezzo Medio')
    plt.ylabel('Quantità')
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig('item_market_analysis.png')
    plt.close()
    
    return df

def analyze_auctions():
    print("\n--- Analisi Approfondita delle Aste ---")
    loading_animation(2)
    auctions_data = get_api_data("market", {"type": "itemmarket"})
    
    df = pd.DataFrame(auctions_data['itemmarket'].items(), columns=['auction_id', 'data'])
    df = pd.concat([df.drop(['data'], axis=1), df['data'].apply(pd.Series)], axis=1)
    
    df['time_left'] = pd.to_timedelta(df['time_left'], unit='s')
    df['end_time'] = datetime.now() + df['time_left']
    
    df['bid_increment'] = df['cost'] - df['base_cost']
    df['bid_increment_percent'] = (df['bid_increment'] / df['base_cost']) * 100
    
    ending_soon = df[df['time_left'] < pd.Timedelta(hours=1)].sort_values('current_cost', ascending=False).head(15)
    print("Top 15 aste che terminano entro un'ora:")
    print(ending_soon[['name', 'current_cost', 'time_left', 'bid_increment_percent']])
    
    high_bids = df.sort_values('current_cost', ascending=False).head(15)
    print("\nTop 15 aste con le offerte più alte:")
    print(high_bids[['name', 'current_cost', 'time_left', 'bid_increment_percent']])
    
    df['bid_count'] = df['bidders'].apply(len)
    popular_auctions = df.sort_values('bid_count', ascending=False).head(15)
    print("\nAste più popolari (per numero di offerenti):")
    print(popular_auctions[['name', 'current_cost', 'bid_count', 'bid_increment_percent']])
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x='current_cost', y='bid_count', size='bid_increment_percent', hue='time_left', palette='viridis')
    plt.title('Costo Corrente vs Numero di Offerte (dimensione = % incremento offerta, colore = tempo rimanente)')
    plt.xlabel('Costo Corrente')
    plt.ylabel('Numero di Offerte')
    plt.xscale('log')
    plt.savefig('auction_analysis.png')
    plt.close()
    
    return df

def analyze_points_price():
    print("\n--- Analisi Approfondita del Prezzo dei Punti ---")
    loading_animation(2)
    points_data = get_api_data("market", {"type": "pointsmarket"})
    
    df = pd.DataFrame(points_data['pointsmarket'].items(), columns=['listing_id', 'data'])
    df = pd.concat([df.drop(['data'], axis=1), df['data'].apply(pd.Series)], axis=1)
    
    df['price_per_point'] = df['cost'] / df['quantity']
    
    stats = df['price_per_point'].describe()
    print("Statistiche del prezzo per punto:")
    print(stats)
    
    best_deals = df.sort_values('price_per_point').head(10)
    print("\nMigliori 10 offerte per punti:")
    print(best_deals[['quantity', 'cost', 'price_per_point']])
    
    worst_deals = df.sort_values('price_per_point', ascending=False).head(10)
    print("\nPeggiori 10 offerte per punti:")
    print(worst_deals[['quantity', 'cost', 'price_per_point']])
    
    df['total_value'] = df['quantity'] * df['price_per_point']
    high_value_deals = df.sort_values('total_value', ascending=False).head(10)
    print("\nOfferte di maggior valore totale:")
    print(high_value_deals[['quantity', 'cost', 'price_per_point', 'total_value']])
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x='quantity', y='price_per_point', size='total_value', hue='cost', palette='viridis')
    plt.title('Quantità vs Prezzo per Punto (dimensione = valore totale, colore = costo)')
    plt.xlabel('Quantità di punti')
    plt.ylabel('Prezzo per punto ($)')
    plt.xscale('log')
    plt.savefig('points_price_analysis.png')
    plt.close()
    
    return df

def get_company_data():
    companies_data = get_api_data("torn", {"selections": "companies"})
    return companies_data['companies']

def analyze_losing_companies(stock_df):
    print("\n--- Analisi Approfondita delle Compagnie in Perdita ---")
    loading_animation(2)
    companies_data = get_company_data()
    
    company_types = defaultdict(list)
    for company_id, company_info in companies_data.items():
        company_type = company_info['name']
        company_types[company_type].append(company_id)
    
    losing_companies = defaultdict(list)
    profitable_companies = defaultdict(list)
    
    for company_type, company_ids in company_types.items():
        for company_id in company_ids[:10]:  # Consideriamo solo le prime 10 compagnie di ogni tipo
            company_stock = stock_df[stock_df['stock_id'] == int(company_id)]
            if not company_stock.empty:
                daily_return = company_stock['daily_return'].values[0]
                weekly_return = company_stock['weekly_return'].values[0]
                monthly_return = company_stock['monthly_return'].values[0]
                if monthly_return < 0:
                    losing_companies[company_type].append((company_id, daily_return, weekly_return, monthly_return))
                else:
                    profitable_companies[company_type].append((company_id, daily_return, weekly_return, monthly_return))
    
    print("\nCompagnie in perdita (rendimento mensile negativo):")
    for company_type, losses in losing_companies.items():
        if losses:
            print(f"\nCompagnie di tipo '{company_type}' in perdita:")
            for company_id, daily, weekly, monthly in sorted(losses, key=lambda x: x[3]):
                print(f"  - Compagnia ID {company_id}: Giornaliero: {daily:.2f}%, Settimanale: {weekly:.2f}%, Mensile: {monthly:.2f}%")
        else:
            print(f"\nNessuna delle prime 10 compagnie di tipo '{company_type}' è in perdita questo mese.")
    
    print("\nCompagnie più redditizie (top 3 per tipo):")
    for company_type, profits in profitable_companies.items():
        if profits:
            print(f"\nCompagnie di tipo '{company_type}' più redditizie:")
            for company_id, daily, weekly, monthly in sorted(profits, key=lambda x: x[3], reverse=True)[:3]:
                print(f"  - Compagnia ID {company_id}: Giornaliero: {daily:.2f}%, Settimanale: {weekly:.2f}%, Mensile: {monthly:.2f}%")
        else:
            print(f"\nNessuna delle prime 10 compagnie di tipo '{company_type}' è in profitto questo mese.")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("UbuntuTech - Analisi Avanzata dell'Economia di Torn")
    print("==================================================")
    
    stock_df = analyze_stock_market()
    input("\nPremi Invio per continuare...")
    os.system('cls' if os.name == 'nt' else 'clear')
    
    item_df = analyze_item_market()
    input("\nPremi Invio per continuare...")
    os.system('cls' if os.name == 'nt' else 'clear')
    
    auction_df = analyze_auctions()
    input("\nPremi Invio per continuare...")
    os.system('cls' if os.name == 'nt' else 'clear')
    
    points_df = analyze_points_price()
    input("\nPremi Invio per continuare...")
    os.system('cls' if os.name == 'nt' else 'clear')
    
    analyze_losing_companies(stock_df)
    
    print("\nAnalisi completata. I grafici sono stati salvati come file PNG.")
  
if __name__ == "__main__":
    main()
