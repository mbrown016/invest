import datetime
import re
import csv
import sys
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

        self.ticker = ticker
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
        etf = {}
        etf_results = {}
        etf_mom = []
        mom_list = []
        etf_posative = []
        mom_results = []
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
            
if __name__ == '__main__':
    arg = str(sys.argv[1])
    if arg == '-etf':
        Invest().etf()
    elif arg == '-401k':
        Invest().four01k()
    elif arg == '-tr':
        ticker = str(input('Ticker: '))
        print('Enter dates as YYYY-MM-DD')
        start_date = str(input('Start Date: '))
        finish_date = str(input('End Date: '))
        Invest().total_return(ticker, start_date, finish_date)
    else:
        print('Invalid argument.','', sep ='\n')
        print('Valid arguments:')
        print('[-etf]    Returns positive momentum ETFs')
        print('[-401k]   Returns positive momentum Funds')  
        print('[-tr]     Returns total return for specified period')
    
