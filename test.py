import requests
from yahoo_finance import Share

comp = input("Ticker: ")
user = '4c17b4af06c36748f2517f1651a442ae'
pw = 'd4391357b369d6288e31652c22e2cc69'

url = 'https://www.intrinio.com/api/financials/standardized'
payload = {'ticker': comp, 'statement': 'cash_flow_statement', 'type': 'TTM', 'date': '2016-07-13'}
response = requests.get(url, params = payload, auth = (user, pw))
data = response.json().get('data')
clean_data = {}
                
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

if __name__ == '__main__':

    print(comp, debt_repayment, debt_issuance, net_debt, '', common_repurchased, common_issued, preferred_repurchased, preferred_issued, net_equity, '',mkt_cap, '', shareholder_yield, div_yield, sep='\n')
