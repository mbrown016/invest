### For more info on possible return values for each financial statement 
### go to: http://community.intrinio.com/docs/financial-tags/

from tinydb import TinyDB, Query
from datetime import datetime
import requests
import time

financial_db = TinyDB('financial_db.json')

class Financials():

    def __init__(self):
        self.user = '4c17b4af06c36748f2517f1651a442ae'
        self.pw = 'd4391357b369d6288e31652c22e2cc69'
        self.url_standard = 'https://www.intrinio.com/api/financials/standardized'
        self.url_reported = 'https://www.intrinio.com/api/financials/reported'
        self.date_format = '%Y-%m-%d'
        self.date = time.strftime(self.date_format)
        self.cache_ttl = 30

    def get_cache(self, ticker, financial_type, year = None):
        ticker = ticker.upper()

        if year == None:
            year = str(self.date)[:4]
        else:
            year = str(year)
            
        cache = financial_db.get((Query().security == ticker) & (Query().financial_type == financial_type) & (Query().year == year))
        
        if cache != None:
            cache_date = cache.get('insert_date')
            current_date = datetime.strptime(self.date, self.date_format)
            cache_date_clean = datetime.strptime(cache_date, self.date_format)
            diff = current_date - cache_date_clean
            cache_age = diff.days
            eid = cache.eid
        else:
            cache_age = None
            eid = None

        return(cache, cache_age, eid)


    def get_income_statement(self, ticker, year = None):
        ticker = ticker.upper()
        date_format = '%Y-%m-%d'

        if year == None:
            year = str(self.date)[:4]
            payload = {'ticker': ticker, 'statement': 'income_statement', 'type': 'TTM', 'date': self.date}
        else:
            year = str(year)
            payload = {'ticker': ticker, 'statement': 'income_statement', 'fiscal_year': year, 'fiscal_period': 'FY'}
                
        response = requests.get(self.url_standard, params = payload, auth = (self.user, self.pw))
        data = response.json().get('data')
        income = {}

        try:
            for val in data:
                tag = val.get('tag')
                value = val.get('value')
                income[tag] = value
            
            record = {'security': ticker, 'year': year, 'financial_type': 'income', 'results': income, 'insert_date': time.strftime('%Y-%m-%d')}
            financial_db.insert(record) 
            return(income)

        except:
            print(ticker, response.status_code, sep = '\t')

        
    def income_statement(self, ticker, year = None):
        ticker = ticker.upper()
        date_format = '%Y-%m-%d'
        date = time.strftime(date_format)

        if year == None:
            cache_results = Financials().get_cache(ticker, 'income')
            if cache_results[0] != None:
                cache = cache_results[0]
                cache_age = cache_results[1]
                record_id = cache_results[2]
       
                if cache_age < self.cache_ttl:
                    income = cache.get('results')

                else:
                    financial_db.remove(eids = [record_id])
                    income = Financials().get_income_statement(ticker)

            else:
                income = Financials().get_income_statement(ticker)

        else:
            year = str(year)
            cache_results = Financials().get_cache(ticker, 'income', year)
            if cache_results[0] != None:
                cache = cache_results[0]
                cache_age = cache_results[1]
                record_id = cache_results[2]
       
                if cache_age < self.cache_ttl:
                    income = cache.get('results')

                else:
                    financial_db.remove(eids = [record_id])
                    income = Financials().get_income_statement(ticker, year)

            else:
                income = Financials().get_income_statement(ticker, year)

        return(income)          

    
    def get_balance_sheet(self, ticker, year = None):
        ticker = ticker.upper()

        if year == None:
            year = str(self.date)[:4]
            payload = {'ticker': ticker, 'statement': 'balance_sheet', 'type': 'TTM', 'date': time.strftime('%Y-%m-%d')}
        else:
            year = str(year)
            payload = {'ticker': ticker, 'statement': 'balance_sheet', 'fiscal_year': str(year), 'fiscal_period': 'FY'}
            
        response = requests.get(self.url_standard, params = payload, auth = (self.user, self.pw))
        data = response.json().get('data')
        balance = {}

        try:
            for val in data:
                tag = val.get('tag')
                value = val.get('value')
                balance[tag] = value

                record = {'security': ticker, 'year': year, 'financial_type': 'balance', 'results': balance, 'insert_date': time.strftime('%Y-%m-%d')}
            financial_db.insert(record)
            return(balance)

        except:
            print(ticker, response.status_code, sep = '\t')

    def balance_sheet(self, ticker, year = None):
        ticker = ticker.upper()
        date_format = '%Y-%m-%d'
        date = time.strftime(date_format)

        if year == None:
            cache_results = Financials().get_cache(ticker, 'balance')
            if cache_results[0] != None:
                cache = cache_results[0]
                cache_age = cache_results[1]
                record_id = cache_results[2]
       
                if cache_age < self.cache_ttl:
                    balance = cache.get('results')

                else:
                    financial_db.remove(eids = [record_id])
                    balance = Financials().get_balance_sheet(ticker)

            else:
                balance = Financials().get_balance_sheet(ticker)

        else:
            year = str(year)
            cache_results = Financials().get_cache(ticker, 'balance', year)
            if cache_results[0] != None:
                cache = cache_results[0]
                cache_age = cache_results[1]
                record_id = cache_results[2]
       
                if cache_age < self.cache_ttl:
                    balance = cache.get('results')

                else:
                    financial_db.remove(eids = [record_id])
                    balance = Financials().get_balance_sheet(ticker, year)

            else:
                balance = Financials().get_balance_sheet(ticker, year)

        return(balance) 
        

    def get_cashflow_statement(self, ticker, year = None):
        ticker = ticker.upper()
        
        if year == None:
            year = str(self.date)[:4]
            payload = {'ticker': ticker, 'statement': 'cash_flow_statement', 'type': 'TTM', 'date': time.strftime('%Y-%m-%d')}
        else:
            year = str(year)
            payload = {'ticker': ticker, 'statement': 'cash_flow_statement', 'fiscal_year': str(year), 'fiscal_period': 'FY'}
        
        response = requests.get(self.url_standard, params = payload, auth = (self.user, self.pw))
        data = response.json().get('data')
        cashflow = {}

        try:
            for val in data:
                tag = val.get('tag')
                value = val.get('value')
                cashflow[tag] = value

            record = {'security': ticker, 'year': year, 'financial_type': 'cashflow', 'results': cashflow, 'insert_date': time.strftime('%Y-%m-%d')}
            financial_db.insert(record)
            return(cashflow)

        except:
            print(ticker, response.status_code, sep = '\t')

    def cashflow_statement(self, ticker, year = None):
        ticker = ticker.upper()
        date_format = '%Y-%m-%d'
        date = time.strftime(date_format)

        if year == None:
            cache_results = Financials().get_cache(ticker, 'cashflow')
            if cache_results[0] != None:
                cache = cache_results[0]
                cache_age = cache_results[1]
                record_id = cache_results[2]
       
                if cache_age < self.cache_ttl:
                    cashflow = cache.get('results')

                else:
                    financial_db.remove(eids = [record_id])
                    cashflow = Financials().get_cashflow_statement(ticker)

            else:
                cashflow = Financials().get_cashflow_statement(ticker)

        else:
            year = str(year)
            cache_results = Financials().get_cache(ticker, 'cashflow', year)
            if cache_results[0] != None:
                cache = cache_results[0]
                cache_age = cache_results[1]
                record_id = cache_results[2]
       
                if cache_age < self.cache_ttl:
                    cashflow = cache.get('results')

                else:
                    financial_db.remove(eids = [record_id])
                    cashflow = Financials().get_cashflow_statement(ticker, year)

            else:
                cashflow = Financials().get_cashflow_statement(ticker, year)

        return(cashflow) 

    
    def get_fundamentals(self, ticker, year = None):
        ticker = ticker.upper()
        
        if year == None:
            year = str(self.date)[:4]
            payload = {'ticker': ticker, 'statement': 'calculations', 'type': 'TTM', 'date': time.strftime('%Y-%m-%d')}
        else:
            year = str(year)
            payload = {'ticker': ticker, 'statement': 'calculations', 'fiscal_year': str(year), 'fiscal_period': 'FY'}

        response = requests.get(self.url_standard, params = payload, auth = (self.user, self.pw))
        data = response.json().get('data')
        fundamentals = {}

        try:
            for val in data:
                tag = val.get('tag')
                value = val.get('value')
                fundamentals[tag] = value

            record = {'security': ticker, 'year': year, 'financial_type': 'fundamentals', 'results': fundamentals, 'insert_date': time.strftime('%Y-%m-%d')}
            financial_db.insert(record)
            return(fundamentals)

        except:
            print(ticker, response.status_code, sep = '\t')

    def fundamentals(self, ticker, year = None):
        ticker = ticker.upper()
        date_format = '%Y-%m-%d'
        date = time.strftime(date_format)

        if year == None:
            cache_results = Financials().get_cache(ticker, 'fundamentals')
            if cache_results[0] != None:
                cache = cache_results[0]
                cache_age = cache_results[1]
                record_id = cache_results[2]
       
                if cache_age < self.cache_ttl:
                    fundamentals = cache.get('results')

                else:
                    financial_db.remove(eids = [record_id])
                    fundamentals = Financials().get_fundamentals(ticker)

            else:
                fundamentals = Financials().get_fundamentals(ticker)

        else:
            year = str(year)
            cache_results = Financials().get_cache(ticker, 'fundamentals', year)
            if cache_results[0] != None:
                cache = cache_results[0]
                cache_age = cache_results[1]
                record_id = cache_results[2]
       
                if cache_age < self.cache_ttl:
                    fundamentals = cache.get('results')

                else:
                    financial_db.remove(eids = [record_id])
                    fundamentals = Financials().get_fundamentals(ticker, year)

            else:
                fundamentals = Financials().get_fundamentals(ticker, year)

        return(fundamentals)
            

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
        
