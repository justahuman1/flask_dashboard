import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.linear_model import LinearRegression as lr
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from bs4 import BeautifulSoup
import pygsheets
import locale as lc
from datetime import datetime,timedelta
from scraper import DataScraper
# from qStart import SheetsCall
from flask_cors import CORS, cross_origin
import json
import requests
app = Flask(__name__)
CORS(app)
#/  CLI INIT
#/*     export FLASK_APP=app.py
#/*     flask run
#/  Optional local run:   flask run --host=0.0.0.0


@app.route('/', methods=["GET"])
def dashboard():
    return render_template('graph.html')

@app.route('/postScrape', methods=["POST"])
def scrape_postRoute():
    g_query = 'https://www.google.com/search?q=Bitcoin'
    data = request.data
    req_date = str(json.loads(data.decode('utf-8'))['date'])
    req_date = req_date.replace(" ", "%20")
    url = g_query+req_date
    s = requests.Session()
    unparsed_req = s.get(url)
    fitted_res = BeautifulSoup(unparsed_req.text, features="lxml")
    href_dict = {'links':[]}
    for a in fitted_res.find_all('a', href=True):
        if 'coin' in a['href'] and 'UTF-8&' not in a['href']:
            href_dict['links'].append(str(a['href']))    
    return jsonify(href_dict)

@app.route('/peekValues', methods=["POST"])
def peekValueRoute():
    all_locales = lc.locale_alias
    lc.setlocale(lc.LC_ALL,all_locales["en_us"])
    data = json.loads(request.data.decode('utf-8'))
    req_currency = str(data['value'])
    if req_currency not in ["BTC", "ETH", "XRP", "VET", "LTC","NANO"]:
        return jsonify({'400':'Failed'})
    tday = datetime.today() - timedelta(days=2)
    td_frmt = tday.strftime('%d-%m-%Y')
    prior_frmt = (tday - timedelta(days=5)).strftime('%d-%m-%Y')
    scraper = DataScraper(req_currency, prior_frmt, td_frmt)
    df = scraper.get_dataframe()
    for i in list(df.columns):
        if(i != 'Date'):
            if req_currency in ['XRP','VET','NANO']:
                df[i] = df[i].apply(lambda x: "$"+lc.format("%.3f",x,True)) 
            else:   
                df[i] = df[i].apply(lambda x: "$"+lc.format("%.0f",x,True))
    return jsonify({'userVals':df.values.tolist()})


class serverCalls():
    '''use Google sheets to minimize server RAM usage (vs pandas)
        --> Google Apps script for quick data manipulation
    '''
    def __init__(self):
        return

    def call(self):
        cred = './gauth_SCM315.json'
        sheet = 'https://docs.google.com/spreadsheets/d/1C4vuMFaJ-xL0QJGjgqkiGylRUACrxGtD9AerDwItIQo/'
        gc = pygsheets.authorize(service_file=cred)
        sh = gc.open_by_url(sheet)
        return sh

    def btc_scrape(self):
        scraper = DataScraper('BTC')
        df = scraper.get_dataframe()
        print('===Sample Data===')
        print(df.tail(5))
        print('===Sample Data End===')
        return df
        
class statistics():
    '''All the maths'''
    def __init__(self):
        return

    def getNewSheetData(self):
        sheet_id = '1C4vuMFaJ-xL0QJGjgqkiGylRUACrxGtD9AerDwItIQo'
        a = SheetsCall(sheet_id,'A:G').getValues()
        sheets_df = pd.DataFrame(a)
        return sheets_df

    def setXandY(self,df):
        x = df.iloc[1:,4:5].values
        y = df.iloc[1:,-2].values
        return x,y

    def linRegression(self,df,x,y):
        l_reg = lr()
        l_reg.fit(x,y)
        return l_reg

    def polyRegression(self,df,x,y):
        pf = PolynomialFeatures(degree=4)
        x_poly = pf.fit_transform(x,y)
        p_reg = lr()
        p_reg.fit(x_poly, y)
        return pf, p_reg

    def polyReg_df(self,poly_reg,pf,x,y,train_test):
        a = {'x_price':[], 'y_pred_vol':[],'y_actual_vol':[],'training_or_test':[]}
        for i in range(0,len(x)-1):
            prediction = poly_reg.predict(pf.fit_transform([x[i]]))
            a['x_price'].append(x[i][0])
            a['y_pred_vol'].append(prediction)
            a['training_or_test'].append(train_test)
            a['y_actual_vol'].append(y[i])
        a = pd.DataFrame(a)
        a['y_pred_vol'] = a['y_pred_vol'].astype(float)
        return a
    
    def neural_nets(self):
        """perform backpropagation"""
        return None

# if __name__ == "__main__":
#     s = statistics()    
#     df = s.getNewSheetData()
#     x,y = s.setXandY(df)
#     x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.2)
#     print(f'x_train row counts is {y_train.shape[0]}')
#     print(f'x_test row counts is {y_test.shape[0]}')
#     pf, poly_reg = s.polyRegression(df,x_train,y_train)
#     g_client = serverCalls().call()
#     try:
#         new_pred_tab = g_client.add_worksheet("Poly Regression",rows=500,cols=5)
#     except:
#         new_pred_tab = g_client.worksheet_by_title('Poly Regression')
        
#     train_model = s.polyReg_df(poly_reg,pf,x_train,y_train,'train')
#     test_model = s.polyReg_df(poly_reg,pf,x_test,y_train,'test')
#     all_models = train_model.append(test_model)
#     new_pred_tab.set_dataframe(all_models,(1,1))

