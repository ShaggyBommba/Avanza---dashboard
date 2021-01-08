import pandas as pd
from Data import AvanzaData as avanza

class DataManager:
    def __init__(self):
        # Datasets
        self.stocks_info = pd.read_csv("Projects/Effective frontier/Data/stocks.csv", header=0, index_col=0)
        self.stocks_prices = pd.read_csv("Projects/Effective frontier/Data/stocks_prices.csv", header=[0,1], skipinitialspace=True, index_col=0).astype("float")

    def retrieveInformation(self, stock=None, columns=None):
        ''' Retrieves the information of a specific stock '''
        if columns is None:
            if stock is None:
                return self.stocks_info.loc[:, :]
            else:
                return self.stocks_info.loc[stock, :]
        else:
            if stock is None:
                return self.stocks_info.loc[:, columns]
            else:
                return self.stocks_info.loc[stock, columns]

    def retrievePrices(self, stock=None, columns=None, drop=False):
        ''' Retrieves the price of a specific stock '''
        if columns is None:
            if(drop):
                return self.stocks_prices.loc[:,(stock,)].dropna().astype("int").droplevel("Stock", axis=1)
            else:
                return self.stocks_prices.loc[:,(stock,)].dropna().astype("int")

        else:
            if(drop):
                return self.stocks_prices.loc[:,(stock,tuple(columns))].dropna().astype("int").droplevel("Values", axis=1)
            else:
                return self.stocks_prices.loc[:,(stock,tuple(columns))].dropna().astype("int")

    def getOptionsAvailable(self):
        ''' Returns a dictionary containing each feature and their corresponding intervals: 
                For numerical values: the intervalls are the Q1, Q2, Q3 quantiles 
                For categorical values: the unique values a used as intervalls  '''
        val = dict()
        features = self.stocks_info.drop(columns=['ISIN','Kortnamn']).nunique(axis=0)
        for x,idx in zip(features,features.index):
            if(x>20):
                data = self.stocks_info[self.stocks_info[idx] != '-'][idx].replace(',','.', regex=True).astype('float')
                values = data.quantile([0.25,0.5,0.75])
                val[idx] = values.values
            else:
                val[idx] = self.stocks_info[self.stocks_info[idx] != '-'][idx].unique()
        return val

    def priceAvailable(self):
        ''' Return a mask whether or not price data for the stocks are available '''
        mask = []
        stock_prices = self.stocks_prices.columns.get_level_values(level=0).values
        for stock in self.stocks_info.index:
            mask.append(stock in stock_prices)
        return mask

    def uppdate(self, save):
        ''' Uppdata data'''
        avanza.retrieveStock(save=save)
        avanza.donwloadPrices(save=save)

