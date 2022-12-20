import yfinance as yf 
from datetime import date
from datetime import datetime

def getdata(name,prevdate):
    today = str(date.today())
    data = yf.download(name+'.NS',prevdate,today)
    if list(data['Close'])==[]:
        return 0, "No Data Available"
    close = float(data['Close'][0])
    diff = (datetime.strptime(today, "%Y-%m-%d") -  datetime.strptime(prevdate, "%Y-%m-%d")).days/365.2425
    print(data)
    return close,diff


# getdata('HDFCBANK.NS','2009-06-18')