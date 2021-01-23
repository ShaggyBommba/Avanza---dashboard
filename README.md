# Avanza---dashboard
This project aims to show how data gathering and visualization could be used in tandem with great success. To show this a dashboard for stock analysis has been created. This dashboard offers the user the possibility to search and analyze stocks to manage their savings. To improve the usefulness of the dashboard an additional function has been added. This functionality calculates the best distribution of your portfolio in regards to the estimated returns while considering the risks. Practically, this is done by identifying the most effective frontier for a given set of stocks. 


The main library used to implement the dashboard is the dash library. To gather the data visualized in the dashboard the selenium library has been utilized to scrape the necessary data needed. The source code is divided into three subparts. The model class represents the code associated with the GUI of the program. The data folder includes the data of each stock, but also the code used to retrieve the data from Avanza. The AvanzaData.py file contains the source code responsible for scraping the data from the web. The DataManeger.py functions as the class that links the data with the GUI. 

# To start the model: 
- 1: Change the pathname for the varaible driver in the class AvanzaData. Change this path to the location where you have your ChromeDriver located. 

- 2: Before you can start the model you need to download the necessary data. To do this you will have run the following model.

from Data import AvanzaData as avanza
avanza.retrieveStock(save=True)
avanza.donwloadPrices(save=True)

- 3: Now you can start the application by initializing the script App.py
