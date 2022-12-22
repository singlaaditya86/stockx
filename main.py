# from bokeh.plotting import figure, output_file, show
# from bokeh.layouts import row
from flask import Flask,render_template,request
import requests
from datetime import datetime
import pandas as pd
from datetime import date
import olddata as old

app = Flask(__name__)

global trendStock
file = pd.read_excel("MCAP31032022.xlsx")
compnamedata = []
api_key = 'e5eefe72ca6d0ae3fe6eed73705d47121f0e3dad99908345f7439f8ffabdffc4'

def get_stock_price(api):
    url = f"https://api.stockmarketapi.in/api/v1/allstocks?token={api}"
    response = requests.get(url).json()
    return response

def createcompnamelist():
    res = get_stock_price(api_key)
    for i in range(0,len(res['data'])):
        compnamedata.append(res['data'][i]['CompanyName'])


def gettrending(data):
    d = {}
    for i in data:
        compname = i['CompanyName']
        prevclose = i['TodayClose']
        ltp = i['ltp']
        if prevclose!=0 and prevclose!=None and ltp!=None:
            percentage = float(i["dayChangePerc"])
        else:
            percentage = 0
        d[compname] = round(percentage, 2)
    trendStock = dict(sorted(d.items(), key = lambda x: x[1], reverse = True)[:5])
    return trendStock


def givedata(name):
    res = get_stock_price(api_key)
    index = -1
    for i in range(0,len(res['data'])):
        if res['data'][i]['CompanyName'] == name:
            index = i
            break
    return res['data'][index]

def rate(name,money,years):
    data = givedata(name)
    yearhigh = data['YrHigh']
    curr = data['ltp']
    no_of_stock = money/curr
    profit = (yearhigh-curr)*no_of_stock*years
    final1 = pow(((profit+money)/money),(1/years))
    # final2 = ((yearhigh-curr)/curr)*100
    final2 = abs(final1-1)
    r = round(final2, 2)
    return r

def givesubmitdata(keyword):
    keydata = []
    for i in compnamedata:
        if keyword in i or keyword.capitalize() in i or keyword.upper() in i or keyword.lower() in i:
            keydata.append(i)
    return keydata

createcompnamelist()
res = get_stock_price(api_key)
trendStock = gettrending(res['data'])

@app.route('/')
def index():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    return render_template('index.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) , namedata=compnamedata,compname="Select Company")

@app.route('/data', methods = ['POST','GET'])
def data():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    if request.method == 'POST':
        comp = request.form["namedropdown"]
        data = givedata(comp)
        if comp == "Select Company":
            return render_template('errorselectcompany.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) , namedata=compnamedata,compname="Select Company")
    return render_template('data.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) , namedata=compnamedata,compname=comp,data=data)

@app.route('/submit',methods = ['POST','GET'])
def submit():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    if request.method=='POST':
        keyword = request.form["input"]
        if keyword=="":
            return render_template('index.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) , namedata=compnamedata,compname="Select Company")
        else:
            l=givesubmitdata(keyword)
    return render_template('submit.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()),lst=l)

@app.route('/submitdata',methods = ['POST','GET'])
def submitdata():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    if request.method=='POST':
        comp = request.form.get("sub_btn")
        data = givedata(comp)
    return render_template('data.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) , namedata=compnamedata,compname=comp,data=data)



@app.route('/cagr')
def cagr():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    return render_template('cagr.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) , namedata=compnamedata,compname="Select Company")

@app.route('/datacagr',methods = ['POST','GET'])
def datacagr():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    if request.method=='POST':
        comp = request.form["namedropdown"]
        if comp == "Select Company":
            return render_template('cagrnameerror.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) ,namedata=compnamedata,compname=comp)
        prevdate = request.form["inputYears"]
        data = givedata(comp)
        today = str(date.today())
        compcode = data['NSECode']
        oldata,noofyear  = old.getdata(compcode,prevdate)
        if noofyear == "No Data Available":
            return render_template('cagrerror.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) ,namedata=compnamedata,compname=comp,data=data, error = noofyear)
        curr = data['ltp']
        CAGR = (curr / oldata)**(1/noofyear) - 1
        final_cagr = round(CAGR, 2)
    return render_template('datacagr.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) ,namedata=compnamedata,compname=comp,data=data,prev=prevdate,today=today,cagrfinal = final_cagr)


@app.route('/sip')
def sip():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    return render_template('sip.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) ,namedata=compnamedata,compname="Select Company")

@app.route('/datasip',methods = ['POST','GET'])
def datasip():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    if request.method=='POST':
        res = get_stock_price(api_key)
        trendStock = gettrending(res['data'])
        prog_no = request.form["program_number"]
        frequency = request.form["frequency"]
        period = int(request.form["period"])
        amount = float(request.form["amount"])
        n = 0
        if frequency == 'Monthly':
            n = 12
        elif frequency == 'Half Yearly':
            n = 2
        elif frequency == 'Yearly':
            n=1
        amount = amount*n*period

        if prog_no == "prog_type":
            net_profit = None
            prog_type = request.form["program_type"]
            if prog_type == 'Top 5 Trending':
                l1 = []
                
                amount1 = amount/5
                for i in trendStock:
                    if len(l1)==5:
                        break
                    l1.append(i)
                rate1 = rate(l1[0],amount1,period)
                p1 = pow((1+rate1),period)*amount1
                rate2 = rate(l1[1],amount1,period)
                p2 = pow((1+rate2),period)*amount1
                rate3 = rate(l1[2],amount1,period)
                p3 = pow((1+rate3),period)*amount1
                rate4 = rate(l1[3],amount1,period)
                p4 = pow((1+rate4),period)*amount1
                rate5 = rate(l1[4],amount1,period)
                p5 = pow((1+rate5),period)*amount1
                totalamoount= p1+p2+p3+p4+p5
                net_profit = ((p1+p2+p3+p4+p5)/amount)*100

            elif prog_type == 'Top 4 Trending':
                l2 = []
                
                amount2 = amount/4
                for i in trendStock:
                    if len(l2)==4:
                        break
                    l2.append(i)
                rate1 = rate(l2[0],amount2,period)
                p1 = pow((1+rate1),period)*amount2
                rate2 = rate(l2[1],amount2,period)
                p2 = pow((1+rate2),period)*amount2
                rate3 = rate(l2[2],amount2,period)
                p3 = pow((1+rate3),period)*amount2
                rate4 = rate(l2[3],amount2,period)
                p4 = pow((1+rate4),period)*amount2
                totalamoount= p1+p2+p3+p4
                net_profit = ((p1+p2+p3+p4)/(amount))*100

            elif prog_type == 'Top 3 Trending':
                l3 = []
                amount3 = amount/3
                for i in trendStock:
                    if len(l3)==3:
                        break
                    l3.append(i)
                rate1 = rate(l3[0],amount3,period)
                p1 = pow((1+rate1),period)*amount3
                rate2 = rate(l3[1],amount3,period)
                p2 = pow((1+rate2),period)*amount3
                rate3 = rate(l3[2],amount3,period)
                p3 = pow((1+rate3),period)*amount3
                totalamoount= p1+p2+p3
                net_profit = ((p1+p2+p3)/amount)*100
                

            elif prog_type == 'Top 2 Trending':
                l4 = []
                amount4 = amount/2
                for i in trendStock:
                    if len(l4)==2:
                        break
                    l4.append(i)
                rate1 = rate(l4[0],amount4,period)
                p1 = pow((1+rate1),period)*amount4
                rate2 = rate(l4[1],amount4,period)
                p2 = pow((1+rate2),period)*amount4
                totalamoount= p1+p2
                net_profit = ((p1+p2)/amount)*100

            elif prog_type == 'Top 1 Trending':
                l5 = []
                amount5 = amount
                for i in trendStock:
                    if len(l5)==1:
                        break
                    l5.append(i)
                rate1 = rate(l5[0],amount5,period)
                p1 = pow((1+rate1),period)*amount5
                totalamoount= p1
                net_profit = ((p1)/amount)*100

        elif prog_no == "namedd":
            comp = request.form["namedropdown"]
            if comp == "Select Company":
                return render_template('SIPnameerror.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) ,namedata=compnamedata,compname=comp)
            ratex = rate(comp,amount,period)
            totalamoount = pow((1+ratex),period)*amount
            net_profit = ((totalamoount)/amount)*100
        finalamount = round(totalamoount, 2)
        net_profit = round(net_profit, 2)
    return render_template('datasip.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) , namedata=compnamedata,compname="Select Company",netprofit = net_profit-100, amount1 = finalamount-amount)


@app.route('/trend', methods = ['POST','GET'])
def trend():
    # sortedcompnamedata = compnamedata
    # sortedcompnamedata.sort()
    if request.method == 'POST':
        comp = request.form.get("Trend")
        data = givedata(comp)
    return render_template('data.html',trendingkeys=list(trendStock.keys()),trendingvals=list(trendStock.values()) , namedata=compnamedata,compname=comp,data=data)



if __name__ == '__main__':
    createcompnamelist()
    res = get_stock_price(api_key)
    trendStock = gettrending(res['data'])
    app.run(debug=True)
