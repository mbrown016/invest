import requests
import time
import csv
from yahoo_finance import Share


class Data():

    
    def __init__(self):
        self.user = '4c17b4af06c36748f2517f1651a442ae'
        self.pw = 'd4391357b369d6288e31652c22e2cc69'
        self.date = time.strftime('%Y-%m-%d')
        div_companies = {}

        with open('div_companies.csv', 'r') as f:
            reader = csv.DictReader(f)
            for line in reader:
                ticker = line['Ticker']
                name = line['Name']
                div_companies[ticker] = name

        self.div_ticker = list(div_companies.keys())

        
    def shareholder_yield(self, hurdle):
        hurdle = float(hurdle)
        div_comp = Data().div_ticker
        comp_list = []
        for ticker in div_comp:
            try:
                divyield = float(Share(ticker).get_dividend_yield())
                if divyield >= hurdle:
                    comp_list.append(ticker)
            except:
                pass
        
        for comp in comp_list[:20]:
            try:
                url = 'https://www.intrinio.com/api/financials/standardized'
                payload = {'ticker': comp, 'statement': 'cash_flow_statement', 'type': 'TTM', 'date': Data().date}
                response = requests.get(url, params = payload, auth = (Data().user, Data().pw))
                data = response.json().get('data')
                clean_data = {}
                results = {}
                for val in data:
                    tag = val.get('tag')
                    value = val.get('value')
                    clean_data[tag] = value

                if clean_data.get('paymentofdividends') != None:
                    dividends = clean_data.get('paymentofdividends')
                else:
                    dividends = 0
                    
                if clean_data.get('repaymentofdebt') != None:
                    debt_repayment = clean_data.get('repaymentofdebt')
                else:
                    debt_repayment = 0

                if clean_data.get('issuanceofdebt') != None:
                    debt_issuance = clean_data.get('issuanceofdebt')
                else:
                    debt_issuance = 0

                if clean_data.get('issuanceofcommonequity') != None:
                    common_issued = clean_data.get('issuanceofcommonequity')
                else:
                    common_issued = 0

                if clean_data.get('repurchaseofcommonequity') != None:
                    common_repurchased = clean_data.get('repurchaseofcommonequity')
                else:
                    common_repurchased = 0

                if clean_data.get('issuanceofpreferredequity') != None:
                    preferred_issued = clean_data.get('issuanceofpreferredequity')
                else:
                    preferred_issued = 0

                if clean_data.get('repurchaseofpreferredequity') != None:
                    preferred_repurchased = clean_data.get('repurchaseofpreferredequity')
                else:
                    preferred_repurchased = 0
                    
                net_debt = (- debt_repayment + debt_issuance) 
                net_equity = (common_repurchased - common_issued) + (preferred_repurchased - preferred_issued)                            
                mkt_cap = Share(comp).get_market_cap()
                if mkt_cap[-1] == 'B':
                    mkt_cap = float(mkt_cap[:-1]) * 1000000000
                elif mkt_cap[-1] == 'M':
                    mkt_cap = float(mkt_cap[:-1]) * 1000000
                else:
                    mkt_cap = mkt_cap[-1]
                    
                shareholder_yield = (- (dividends + net_debt + net_equity) / mkt_cap) * 100
                div_yield = (- dividends / mkt_cap) * 100

               # if div_yield >= hurdle and shareholder_yield >= hurdle:
                print(comp, round(shareholder_yield, 2), round(div_yield, 2))

            except:
                print(ticker)
                  
        print(results)
        
if __name__ == '__main__':    
    Data().shareholder_yield(2.75)
        
        