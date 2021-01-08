import numpy as np

def normaliz(df):
    mean = df.mean(axis=0)
    df = df.apply(lambda x: x-mean, axis=1)
    return df, mean

def getCov(df):
    return df.T.dot(df)/df.shape[0]

def buildFrontier(df, runs=6000):
    if(runs>120000): raise ValueError("number of runs surpasses maximum allowed: {}".format(runs))
    df, mean = normaliz(df)
    cov = getCov(df)

    # Variables to be calculated
    portfolio_var_l = []
    portfolio_return_l = []
    portfolio_sharpe_l = []
    portfolio_wheights_l = []

    for _ in range(runs):
        portfolio_weights = np.random.random(len(df.columns))
        portfolio_weights = portfolio_weights/np.sum(portfolio_weights)

        portfolio_var =  np.sqrt(portfolio_weights.T.dot(cov).dot(portfolio_weights))
        portfolio_return = portfolio_weights.dot(mean.T)
        portfolio_sharpe = portfolio_return/portfolio_var

        portfolio_var_l.append(portfolio_var)
        portfolio_return_l.append(portfolio_return)
        portfolio_sharpe_l.append(portfolio_sharpe)
        portfolio_wheights_l.append(", ".join([stock+": {:.2f} %".format(weight*100) for stock,weight in zip(df.columns,portfolio_weights)]))

    return portfolio_return_l,portfolio_var_l,portfolio_sharpe_l,portfolio_wheights_l










