### For more info on possible return values for each financial statement 
### go to: http://community.intrinio.com/docs/financial-tags/


import requests
import time

class Financials():

    def __init__(self):
        self.user = '4c17b4af06c36748f2517f1651a442ae'
        self.pw = 'd4391357b369d6288e31652c22e2cc69'
        self.url_standard = 'https://www.intrinio.com/api/financials/standardized'
        self.url_reported = 'https://www.intrinio.com/api/financials/reported'
    
        
    def income_statement(self, ticker, year = None):
        ticker = ticker.upper()

        if year == None:
            payload = {'ticker': ticker, 'statement': 'income_statement', 'type': 'TTM', 'date': time.strftime('%Y-%m-%d')}
        else:
            payload = {'ticker': ticker, 'statement': 'income_statement', 'fiscal_year': str(year), 'fiscal_period': 'FY'}
                
        response = requests.get(self.url_standard, params = payload, auth = (self.user, self.pw))
        data = response.json().get('data')
        income = {}

        try:
            for val in data:
                tag = val.get('tag')
                value = val.get('value')
                income[tag] = value
            return(income)

        except:
            print(ticker, response.status_code, sep = '\t')          

    
    def balance_sheet(self, ticker, year = None):
        ticker = ticker.upper()

        if year == None:
            payload = {'ticker': ticker, 'statement': 'balance_sheet', 'type': 'TTM', 'date': time.strftime('%Y-%m-%d')}
        else:
            payload = {'ticker': ticker, 'statement': 'balance_sheet', 'fiscal_year': str(year), 'fiscal_period': 'FY'}
            
        response = requests.get(self.url_standard, params = payload, auth = (self.user, self.pw))
        data = response.json().get('data')
        balance = {}

        try:
            for val in data:
                tag = val.get('tag')
                value = val.get('value')
                balance[tag] = value
            return(balance)

        except:
            print(ticker, response.status_code, sep = '\t')           
        

    def cashflow_statement(self, ticker, year = None):
        ticker = ticker.upper()
        
        if year == None:
            payload = {'ticker': ticker, 'statement': 'cash_flow_statement', 'type': 'TTM', 'date': time.strftime('%Y-%m-%d')}
        else:
            payload = {'ticker': ticker, 'statement': 'cash_flow_statement', 'fiscal_year': str(year), 'fiscal_period': 'FY'}
        
        response = requests.get(self.url_standard, params = payload, auth = (self.user, self.pw))
        data = response.json().get('data')
        cashflow = {}

        try:
            for val in data:
                tag = val.get('tag')
                value = val.get('value')
                cashflow[tag] = value
            return(cashflow)

        except:
            print(ticker, response.status_code, sep = '\t')

    
    def fundamentals(self, ticker, year = None):
        ticker = ticker.upper()
        
        if year == None:
            payload = {'ticker': ticker, 'statement': 'calculations', 'type': 'TTM', 'date': time.strftime('%Y-%m-%d')}
        else:
            payload = {'ticker': ticker, 'statement': 'calculations', 'fiscal_year': str(year), 'fiscal_period': 'FY'}

        response = requests.get(self.url_standard, params = payload, auth = (self.user, self.pw))
        data = response.json().get('data')
        fundamentals = {}

        try:
            for val in data:
                tag = val.get('tag')
                value = val.get('value')
                fundamentals[tag] = value
            return(fundamentals)

        except:
            print(ticker, response.status_code, sep = '\t')
            

if __name__ == '__main__':
    ticker = input('Ticker: ')
    financial = input('Financial: ')
    year = input('Year: ')

    if financial.lower() == 'income' or financial.lower() == 'is':
        value = Financials().income_statement(ticker)
       
    if financial.lower() == 'balance' or financial.lower() == 'bs':
        value = Financials().balance_sheet(ticker)

    if financial.lower() == 'cashflow' or financial.lower() == 'cash' or financial.lower() == 'cf':
        value = Financials().cashflow_statement(ticker)

    print(value)
        
