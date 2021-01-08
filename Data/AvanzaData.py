import pandas as pd
from currency_converter import CurrencyConverter
import yfinance as yf
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import urllib3
import time


main_url = "https://www.avanza.se"

def makeSoup(url):
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data ,'lxml')
    return soup

def retrieveStock(save=True):
    ''' The main function that navigates through the webpage containing the stock-listning'''
    markets_info = pd.DataFrame()
    stocklist_p = "/".join([main_url, "aktier/lista.html"])
    driver = webdriver.Chrome("C:/Program Files/chromedriver.exe")
    driver.get(stocklist_p)
    
    # Accept the cookie popup.
    driver.find_element_by_xpath("//button[@class='cookie-consent-btn']").click()

    # Button associated with loading more data.
    botton = driver.find_elements_by_xpath("//div[@class = 'component landFilter']/div[@class='multiSelect u-clearFix u-relative']")[1]

    # The dropdown option for selecting market of interest.
    markets = driver.find_elements_by_xpath("//div[@class = 'component landFilter']//ul[@class='u-cleanList']//li")[1::]
    
    # Removing preselected market
    botton.click()
    markets[1].click()

    # The main for-loop that parses each stock 
    for market in markets:
        # Select the market of intrest
        market.click()
        botton.click()

        # Load all the stocks
        while(True):
            try:
                driver.find_element_by_xpath("//button[@class='button invertedFocusBtn extraLargeBtn fetchMoreButton']").click()           
            except NoSuchElementException:
                break
        
        # Parse the page containing the stocks 
        page = driver.page_source
        market_info = downloadPages(page)
        print(market_info.head())
        markets_info = markets_info.append(market_info, sort=False)

        # Deselect the market.
        botton.click()
        market.click()       
    driver.quit()

    if(save):
        markets_info.to_csv("Projects/Effective frontier/Data/stocks.csv", na_rep = "-")

def downloadPages(page_source):
    ''' Download the pages containing the stock from each list '''
    soup = BeautifulSoup(page_source,'lxml')
    pages = pd.DataFrame()

    # iterates and parses each stock on the page
    for idx,a in enumerate(soup.find_all("a", class_="ellipsis")):
        print(idx)
        stock_page = "".join([main_url, a["href"]])
        page = parsePage(stock_page)
        pages = pages.append(page, sort=False)
    return pages
        
def parsePage(url):
    ''' Converts the stock page to a Series containing critical information'''
    # Converter objcet
    c = CurrencyConverter()

    # Dictionaries
    invalid_words={"&nbsp;" : '',
                    "\n" : '',
                    "\xa0" : '',
                    "\r" : '',
                    "\t": '',
                    "," : "."}
    currencies = {" EUR" : c.convert(1, 'EUR', 'SEK'),
                  " MSEK" : 1000000,  
                  " GBP" : c.convert(1, 'GBP', 'SEK'), 
                  " USD" : c.convert(1, 'USD', 'SEK'),
                  " MUSD" : c.convert(1000000, 'USD', 'SEK'), 
                  " CAD" : c.convert(1, 'CAD', 'SEK'), 
                  " DKK" : c.convert(1, 'DKK', 'SEK'), 
                  " MEUR" : c.convert(1000000, 'EUR', 'SEK'), 
                  " NOK": c.convert(1, 'NOK', 'SEK')}
    
    # Retrieving data
    soup = makeSoup(url)
    values = []
    attributes = []
    for val,att in zip(soup.find("div", class_="row").find_all("dd"), soup.find("div", class_="row").find_all("dt")):
        value = val.get_text().strip()
        attribute = att.get_text().strip()

        for w,r in invalid_words.items():
            value = value.replace(w,r)
            attribute = attribute.replace(w,r)
 
        for cur,rate in currencies.items():   
            if(attribute.find(cur) != -1):
                attribute = attribute.replace(cur," SEK")
                try:                  
                    value = "{:.2f}".format(float(value.replace(",",'.'))*rate)
                except ValueError:
                    pass
       
        values.append(value)
        attributes.append(attribute)
    return pd.Series(data=values, index=attributes, name=values[0])

def donwloadPrices(period="max", save=True, path="stocks_prices.csv"):
        stocks = pd.read_csv("Projects/Effective frontier/Data/stocks.csv", header=0, index_col=0)
        stocks = [''.join([abv.replace(' ','-'),".ST"]) for abv in stocks.index]
        prices = pd.DataFrame()

        for idx,stock in enumerate(stocks):
            print("Stock number: {} - {} ".format(idx,stock))
            price = yf.download(stock, period="3y", progress=False)[['Open', 'High', 'Low', 'Close']]
            price = price[~price.index.duplicated(keep='last')]
            prices = pd.concat([prices, price], axis=1)

        # Add collumns
        prices.columns = pd.MultiIndex.from_tuples([col for stock in stocks for col in  
                                            zip([stock.replace('.ST','')]*4, ['Open', 'High', 'Low', 'Close'])],
                                            names=["Stock", "Values"])  

        #Removes non available prices
        prices = prices.loc[:,[~prices.loc[:,row].isna().all() for row in prices]]

        # Save data
        if(save):
            path = "".join(["Projects/Effective frontier/Data/", path])
            prices.to_csv(path)
        return prices



