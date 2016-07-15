import datetime
import re
import csv
import sys
from financials import Financials
from yahoo_finance import Share

today = datetime.date.today()
year = datetime.timedelta(days = 365)
year_ago = (today - year)

class Invest():
    
    def __init__(self):
        pass
                

    def weekday(self, day):
        '''Standardize dates to last weekday.'''
        day = str(day)
        if re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', day):
            year = int(day.split("-")[0])
            month = int(day.split("-")[1])
            day = int(day.split("-")[2])

            start_date = datetime.datetime(year, month, day)
            weekday_start = start_date.isoweekday()

            if weekday_start > 5:
                adj_start_date = start_date - datetime.timedelta(days=(weekday_start - 5))  
            else:
                adj_start_date = start_date
	
            adj_start_date = str(adj_start_date).split(" ")[0]
            start_year = adj_start_date.split("-")[0]
            start_month = adj_start_date.split("-")[1]
            start_day = adj_start_date.split("-")[2]
            output = "%s-%s-%s" % (start_year, start_month, start_day)

            return output
        else:
            return 'Invalid date.  Please use YYYY-MM-DD format.'
	

    def momentum(self, ticker):
        '''Calculate price momentum past 10 months, 1 month lag.'''

        history_365 = Share(ticker).get_historical(Invest().weekday(year_ago), Invest().weekday(today))
        adj_close = [float(history_365[x].get('Adj_Close')) for x in range(len(history_365))]
        current = adj_close[0]
        ma1 = adj_close[21]
        ma11 = adj_close[231]

        ### 10 month MA w/ 1 month lag ###
        mom = (((ma1 / ma11) - 1) * 100)

        ### price relative to 11 month SMA ###
        p_sma = (((current / ma11) - 1) * 100)

        return(ticker, mom, p_sma)
    

    def total_return(self, ticker, start_date, finish_date):
        start = Invest().weekday(start_date)
        finish = Invest().weekday(finish_date)
        history = Share(ticker).get_historical(start, finish)

        end = float(history[0].get('Adj_Close'))
        beg = float(history[-1].get('Adj_Close'))
        ytd = float(((end / beg) - 1) * 100)
        print('Total Return:   ', round(ytd, 2), '%', sep = '')
        

    def etf(self):
        etf_results = {}
        etf_mom = []
        mom_list = []
        etf_posative = []
        mom_results = []
        etf = {}
        with open('etf.csv', 'r') as etf_file:
            reader = csv.DictReader(etf_file)
            for line in reader:
                ticker = line['Ticker']
                name = line['Fund_Name']
                etf[ticker] = name
        
        for fund in etf:
            mom = Invest().momentum(fund)
            etf_mom.append(mom)
            etf_results[mom[1]] = fund
            if mom[1] > 0 and mom[2] > 0:
                mom_list.append(mom[1])

        mom_list.sort(reverse = True)
                
        for value in mom_list:
            symbol = etf_results[value]
            fund_type = etf[symbol]
            momentum = value
            print(symbol, round(momentum,2), fund_type, sep = '\t')
                

    def four01k(self):
        fidelity = ('RGAGX', 'FXSIX', 'VWNAX', 'FSEVX', 'RTRIX', 'VEXRX', 'RERGX', 'FSIVX', 'FINPX', 'MWTSX', 'PHYIX')		

        fund_mom = {}
        mom_list= []

        for fund in fidelity:
            mom = Invest().momentum(fund)[1]
            if mom > 0:
                fund_mom[mom] = fund
                mom_list.append(mom)

        mom_list.sort(reverse = True)
        for value in mom_list:
            symbol = fund_mom[value]
            print(symbol, round(value, 2), sep = '\t')


    def shareholder_yield(self, ticker):
        ticker = ticker.upper()
        cashflow = Financials().cashflow_statement(ticker)
        if cashflow == None:
            shareholder_yield = 0
            div_yield = 0
        else:
            cf_keys = cashflow.keys()
        
            if 'paymentofdividends' in cf_keys:
                dividends = cashflow.get('paymentofdividends')
            else:
                dividends = 0

            if 'repaymentofdebt' in cf_keys:
                debt_repayment = cashflow.get('repaymentofdebt')
            else:
                debt_repayment = 0

            if 'issuanceofdebt' in cf_keys:
                debt_issuance = cashflow.get('issuanceofdebt')
            else:
                debt_issuance = 0

            if 'issuanceofcommonequity' in cf_keys:
                common_issued = cashflow.get('issuanceofcommonequity')
            else:
                common_issued = 0

            if 'repurchaseofcommonequity' in cf_keys:
                common_repurchased = cashflow.get('repurchaseofcommonequity')
            else:
                common_repurchased = 0

            if 'issuanceofpreferredequity' in cf_keys:
                preferred_issued = cashflow.get('issuanceofpreferredequity')
            else:
                preferred_issued = 0

            if 'repurchaseofpreferredequity' in cf_keys:
                preferred_repurchased = cashflow.get('repurchaseofpreferredequity')
            else:
                preferred_repurchased = 0

            net_debt = (- debt_repayment + debt_issuance)
            net_equity = (common_repurchased - common_issued) + (preferred_repurchased - preferred_issued)
            mkt_cap = Share(ticker).get_market_cap()

            if mkt_cap != None:
                if mkt_cap[-1] == 'B':
                    mkt_cap = float(mkt_cap[:-1]) * 1000000000
                elif mkt_cap[-1] == 'M':
                    mkt_cap = float(mkt_cap[:-1]) * 1000000
                else:
                    mkt_cap = mkt_cap[-1]
                    
                shareholder_yield = (- (dividends + net_debt + net_equity) / mkt_cap) * 100
                div_yield = (- dividends / mkt_cap) * 100
                
            else:
                shareholder_yield = 0
                div_yield = 0
                
        return(shareholder_yield, div_yield)


    def shareholder_yield_rank(self, hurdle):
        hurdle = float(hurdle)
        div_companies = {}
        company_list = []
        sh_yield_list = []
        div_yield_list = []
        mom_list = []
        results = {}
        rank = {}
        
        with open('div_companies.csv', 'r') as f:
            reader = csv.DictReader(f)
            for line in reader:
                ticker = line['Ticker']
                name = line['Name']
                div_companies[ticker] = name
                company_list.append(ticker)
                
        for company in company_list:
            try:
                div_yield = float(Share(company).get_dividend_yield())
                if div_yield >= hurdle:
                    mom = Invest().momentum(company)
                    if float(mom[1]) > 0:
                        result = Invest().shareholder_yield(company)
                        if abs(result[1] - div_yield) < 1:
                            if result[0] >= hurdle and result[1] >= hurdle:
                                sh_yield_list.append(result[0])
                                div_yield_list.append(result[1])
                                mom_list.append(mom[1])
                                results[company] = ([result[0], result[1], mom[1]])

            except Exception as ex:
                template = "An exception of type {0} occured. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(company)
                print(message)
                
        company_out = list(results.keys())
        max_sh_yield = max(sh_yield_list)
        max_div_yield = max(div_yield_list)
        max_mom = max(mom_list)

        for comp in company_out:
            sh_y = results.get(comp)[0]
            div_y = results.get(comp)[1]
            momen = results.get(comp)[2]

            sh_yield_norm = sh_y / max_sh_yield
            div_yield_norm = div_y / max_div_yield
            mom_norm = momen / max_mom
            rank_val = sh_yield_norm + div_yield_norm + mom_norm
            
            rank[rank_val] = comp

        ranked_list = list(rank.keys())
        ranked_list.sort()

        print('Ticker', 'SH Yld', 'DIV Yld', 'MOM', 'Rank', sep = '\t')        

        for val in ranked_list[::-1]:
            symbol = rank.get(val)
            share_yield = round(results.get(symbol)[0], 2)
            div_yield = round(results.get(symbol)[1], 2)
            momentum = round(results.get(symbol)[2], 2)
            rank_value = round(val, 2)
            print(symbol, share_yield, div_yield, momentum, rank_value, sep = '\t')

    def error(self):
        print('Invalid argument.','', sep ='\n')
        print('Valid arguments:')
        print('[-etf]    Returns positive momentum ETFs')
        print('[-401k]   Returns positive momentum Funds')
        print('[-mom]    Returns momentum for a security')
        print('[-tr]     Returns total return for specified period')
        print('[-yield]  Returns shareholder & dividend yield for a security')
        print('[-rank]   Returns ranked list based on shareholder yield')


if __name__ == '__main__':
    arg = str(sys.argv[1])

    if arg == None:
        Invest().error()
    elif arg == '-etf':
        Invest().etf()
    elif arg == '-401k':
        Invest().four01k()
    elif arg == '-tr':
        ticker = str(input('Ticker: '))
        print('Enter dates as YYYY-MM-DD')
        start_date = str(input('Start Date: '))
        finish_date = str(input('End Date: '))
        Invest().total_return(ticker, start_date, finish_date)
    elif arg == '-mom':
        ticker = str(input('Ticker: '))
        output = Invest().momentum(ticker)
        print(output[0], round(output[1], 2), sep ='\t')
    elif arg == '-yield':
        ticker = str(input('Ticker: '))
        output = Invest().shareholder_yield(ticker)
        print(ticker.upper(), round(output[0], 2), round(output[1], 2), sep = '\t')
    elif arg == '-rank':
        hurdle = input('Hurdle Rate: ')
        Invest().shareholder_yield_rank(hurdle)
    else:
        Invest().error()
    
