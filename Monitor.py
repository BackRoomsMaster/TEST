import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import subprocess

class MonitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Torn Economy Monitor")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.stock_tab = QWidget()
        self.item_tab = QWidget()
        self.auction_tab = QWidget()
        self.points_tab = QWidget()

        self.tabs.addTab(self.stock_tab, "Stock Market")
        self.tabs.addTab(self.item_tab, "Item Market")
        self.tabs.addTab(self.auction_tab, "Auctions")
        self.tabs.addTab(self.points_tab, "Points")

        self.stock_canvas = FigureCanvas(Figure(figsize=(5, 4), dpi=100))
        self.item_canvas = FigureCanvas(Figure(figsize=(5, 4), dpi=100))
        self.auction_canvas = FigureCanvas(Figure(figsize=(5, 4), dpi=100))
        self.points_canvas = FigureCanvas(Figure(figsize=(5, 4), dpi=100))

        self.stock_tab.layout = QVBoxLayout(self.stock_tab)
        self.stock_tab.layout.addWidget(self.stock_canvas)
        self.item_tab.layout = QVBoxLayout(self.item_tab)
        self.item_tab.layout.addWidget(self.item_canvas)
        self.auction_tab.layout = QVBoxLayout(self.auction_tab)
        self.auction_tab.layout.addWidget(self.auction_canvas)
        self.points_tab.layout = QVBoxLayout(self.points_tab)
        self.points_tab.layout.addWidget(self.points_canvas)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1800000)  # 30 minuti in millisecondi

        self.update_data()

    def update_data(self):
        print("Aggiornamento dati...")
        
        # Esegui UbuntuTech.py in background
        subprocess.run(["python", "UbuntuTech.py"], capture_output=True)

        # Carica i dati dai file CSV generati da UbuntuTech.py
        stock_df = pd.read_csv('stock_data.csv')
        item_df = pd.read_csv('item_data.csv')
        auction_df = pd.read_csv('auction_data.csv')
        points_df = pd.read_csv('points_data.csv')

        self.plot_stock_data(stock_df)
        self.plot_item_data(item_df)
        self.plot_auction_data(auction_df)
        self.plot_points_data(points_df)

    def plot_stock_data(self, df):
        ax = self.stock_canvas.figure.subplots()
        ax.clear()
        ax.scatter(df['current_price'], df['monthly_return'], alpha=0.5)
        ax.set_xlabel('Current Price')
        ax.set_ylabel('Monthly Return (%)')
        ax.set_title('Stock Market Overview')
        self.stock_canvas.draw()

    def plot_item_data(self, df):
        ax = self.item_canvas.figure.subplots()
        ax.clear()
        ax.scatter(df['avg_price'], df['quantity'], alpha=0.5)
        ax.set_xlabel('Average Price')
        ax.set_ylabel('Quantity')
        ax.set_title('Item Market Overview')
        ax.set_xscale('log')
        ax.set_yscale('log')
        self.item_canvas.draw()

    def plot_auction_data(self, df):
        ax = self.auction_canvas.figure.subplots()
        ax.clear()
        ax.scatter(df['current_cost'], df['bid_count'], alpha=0.5)
        ax.set_xlabel('Current Cost')
        ax.set_ylabel('Bid Count')
        ax.set_title('Auction Overview')
        ax.set_xscale('log')
        self.auction_canvas.draw()

    def plot_points_data(self, df):
        ax = self.points_canvas.figure.subplots()
        ax.clear()
        ax.scatter(df['quantity'], df['price_per_point'], alpha=0.5)
        ax.set_xlabel('Quantity')
        ax.set_ylabel('Price per Point')
        ax.set_title('Points Market Overview')
        ax.set_xscale('log')
        self.points_canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MonitorWindow()
    main_window.show()
    sys.exit(app.exec_())
