import datetime
import re
import csv
import sys
from financials import Financials
from yahoo_finance import Share
from transactions import DB

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
        etf = {}
        with open('etf.csv', 'r') as etf_file:
            reader = csv.DictReader(etf_file)
            for line in reader:
                ticker = line['Ticker']
                name = line['Fund_Name']
                etf[ticker] = name
        
        sp500 = Invest().momentum('VOO')[1]
        bond = Invest().momentum('VGSH')[1]
        intl = Invest().momentum('VEU')[1]
        benchmark = {sp500: 'VOO', bond: 'VGSH', intl: 'VEU'}
        max_bench = max(list(benchmark.keys()))
        max_fund = benchmark[max_bench]
                
        for fund in etf:
            mom = Invest().momentum(fund)
            etf_mom.append(mom)
            etf_results[mom[1]] = fund
            if mom[1] > 0 and mom[2] > 0 and mom[1] > max_bench:
                mom_list.append(mom[1])

        mom_list.sort(reverse = True)

        print('', 'IRA:', sep = '\n')
        print('Fund', 'MOM', '%', 'Type', sep = '\t')

        if len(mom_list) == 0:
            fund_type = etf[max_fund]
            print(max_fund, round(max_bench, 2), 100, fund_type, sep = '\t')
        elif len(mom_list) >= 4:
            percent = 25
            for val in mom_list[:4]:
                symbol = etf_results[val]
                fund_type = etf[symbol]
                print(symbol, round(val, 2), percent, fund_type, sep = '\t')
        else:
            percent = int(100.0 / (len(mom_list) + 1))
            for val in mom_list:
                symbol = etf_results[val]
                fund_type = etf[symbol]
                print(symbol, round(val, 2), percent, fund_type, sep = '\t')
                types = etf[max_fund]
                print(max_fund, round(max_bench, 2), percent, types, sep = '\t')        
                


    def etf_rank(self, number, amt):
        etf_results = {}
        etf_mom = []
        mom_list = []
        etf = {}
        etf_type = {}
        results = []

        benchmark = Invest().momentum('RSP')[1]
        
        with open('ETF_list.csv', 'r') as etf_file:
            reader = csv.DictReader(etf_file)
            for line in reader:
                ticker = line['Ticker']
                name = line['Name']
                category = line['Category']
                etf[ticker] = name
                etf_type[ticker] = category
        
        for fund in etf:
            try:
                mom = Invest().momentum(fund)
                etf_mom.append(mom)
                etf_results[mom[1]] = fund
                if mom[1] >= benchmark and mom[1] > 0 and mom[2] > 0:
                    mom_list.append(mom[1])
            except:
                print(fund)

                    
        mom_list.sort(reverse = True)

        number = float(number)
        amt = float(amt)
        std_threshold = 30  ### % max allocation to one standard fund category
        alt_threshold = 10  ### % max allocation to one alternative fund category
        allocation = 100 / number  ### % allocated to each investment
        count = 0
        std_count = 0
        alt_count = 0
        max_alt = .4 * number  ### max portfolio allocation to alternative assets
        allocate = amt / number

        alt_energy = 0
        bonds = 0
        commodities = 0
        consumer = 0
        currencies = 0
        dev_markets = 0
        emerg_markets = 0
        energy = 0
        financials = 0
        healthcare = 0
        industrials = 0
        mining = 0
        preferred = 0
        real_estate = 0
        tech = 0
        utilities = 0
        
        for value in mom_list:
            symbol = etf_results[value]
            fund_name = etf[symbol]
            fund_type = etf_type[symbol]
            momentum = value

            count = std_count + alt_count

            if count >= number:
                break
            else:
            
                if fund_type == 'Alternative Energy':
                    if (alt_energy * (allocation + 1)) >= alt_threshold or (alt_count + 1) >= max_alt:
                        pass
                    else:
                        alt_energy += 1
                        alt_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Bonds':
                    if (bonds * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        bonds += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Commodities':
                    if (commodities * (allocation + 1)) >= alt_threshold or (alt_count + 1) >= max_alt:
                        pass
                    else:
                        commodities += 1
                        alt_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Consumer':
                    if (consumer * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        consumer += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Currencies':
                    if (currencies * (allocation + 1)) >= alt_threshold or (alt_count + 1) >= max_alt:
                        pass
                    else:
                        currencies += 1
                        alt_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Developed Markets':
                    if (dev_markets * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        dev_markets += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Emerging Markets':
                    if (emerg_markets * (allocation + 1)) >= alt_threshold or (alt_count + 1) >= max_alt:
                        pass
                    else:
                        emerg_markets += 1
                        alt_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Energy':
                    if (energy * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        energy += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Financials':
                    if (financials * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        financials += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Healthcare':
                    if (healthcare * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        healthcare += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Industrials':
                    if (industrials * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        industrials += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Metals & Mining':
                    if (mining * (allocation + 1)) >= alt_threshold or (alt_count + 1) >= max_alt:
                        pass
                    else:
                        mining += 1
                        alt_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Preferred Equity':
                    if (preferred * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        preferred += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Real Estate':
                    if (real_estate * (allocation + 1)) >= alt_threshold or (alt_count + 1) >= max_alt:
                        pass
                    else:
                        real_estate += 1
                        alt_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Technology':
                    if (tech * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        tech += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

                if fund_type == 'Utilities':
                    if (utilities * (allocation + 1)) >= std_threshold:
                        pass
                    else:
                        utilities += 1
                        std_count += 1
                        results.append([symbol, round(momentum,2), fund_name, fund_type, allocate])

        if count < number:
            if benchmark > 0:
                diff = number - count
                results.append(['RSP', round(benchmark), 'S&P 500 Eq Weight', 'Index', (diff * allocate)])
            else:
                results.append(['CASH', '', '', '', (diff * allocate)])
                        
        for v in results:
            print(v[0], v[1], v[2], v[3], round(v[4], 2), sep = '\t')

    def four01k(self):
        fidelity = ('RGAGX', 'VWNAX', 'FSEVX', 'RTRIX', 'VEXRX', 'RERGX', 'FINPX', 'PHYIX')		

        fund_mom = {}
        mom_list = []
        matt_mom = {}
        matt_mom_list = []

        sp500 = Invest().momentum('FXSIX')[1]
        intl = Invest().momentum('FSIVX')[1]
        bonds = Invest().momentum('MWTSX')[1]
        benchmark = {sp500: 'FXSIX', intl: 'FSIVX', bonds: 'MWTSX'}
        max_bench = max(list(benchmark.keys()))
        max_fund = benchmark[max_bench]

        for fund in fidelity:
            mom = Invest().momentum(fund)[1]
            if mom > 0 and mom > max_bench:
                mom_list.append(mom)
                fund_mom[mom] = fund

        print('', 'Maxi 401k:', sep = '\n')
        print('Fund', 'MOM', '%', sep = '\t')
        mom_list.sort(reverse = True)
        
        if len(mom_list) == 0:
           print(max_fund, round(max_bench, 2), 100, sep = '\t')
        elif len(mom_list) >= 4:
            percent = 25
            for val in mom_list[:4]:
                symbol = fund_mom[val]
                print(symbol, round(val, 2), percent, sep = '\t')
        else:
            percent = int(100.0 / (len(mom_list) + 1))
            for val in mom_list:
                symbol = fund_mom[val]
                print(symbol, round(val, 2), percent, sep = '\t')
                print(max_fund, round(max_bench, 2), percent, sep = '\t')


        principal = ('PFMRX', 'PLFNX', 'PINNX', 'PEASX')
        ### PFMRX = Short term bond
        ### PLFNX = S&P 500
        ### PINNX = International stocks
        ### PEASX = Emerging market stocks

        for fund in principal:
            momentum = Invest().momentum(fund)[1]
            if momentum > 0:
                matt_mom[fund] = momentum
                matt_mom_list.append(momentum)

        matt_mom_list.sort(reverse = True)

        percentage = 100
            
        bond = matt_mom['PFMRX']
        sp500 = matt_mom['PLFNX']
        intl = matt_mom['PINNX'] 
        emerg = matt_mom['PEASX']

        print('', 'Matt 401k:', sep = '\n')
        print('Fund', 'Type', 'MOM', '%', sep = '\t')

        if emerg == max(matt_mom_list):
            percentage = 80
            print('PEASX', 'Emerg', round(emerg, 2), '20', sep = '\t')

        if bond == max(matt_mom_list):
            print('PFMRX', 'Bonds', round(bond, 2), percentage, sep = '\t')
        elif sp500 == max(matt_mom_list):
            print('PLFNX', 'SP500', round(sp500, 2), percentage, sep = '\t')
        elif intl == max(matt_mom_list):
            print('PINNX', 'Intl', round(intl, 2), percentage, sep = '\t')
        else:
            print('CASH', '', '', 100, sep = '\t')


    def shareholder_yield(self, ticker, yr = None):
        ticker = ticker.upper()
        if year == None:
            cashflow = Financials().cashflow_statement(ticker)
        else:
            cashflow = Financials().cashflow_statement(ticker, year = yr)
            
        if cashflow == None:
            shareholder_yield = 0
            div_yield = 0
            return(shareholder_yield, div_yield)
        else:
            cf_keys = cashflow.keys()
        
        if 'paymentofdividends' in cf_keys:
            dividends = - cashflow.get('paymentofdividends')
        else:
            dividends = 0

        if 'repaymentofdebt' in cf_keys:
            debt_repayment = - cashflow.get('repaymentofdebt')
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
            common_repurchased = - cashflow.get('repurchaseofcommonequity')
        else:
            common_repurchased = 0
            
        if 'issuanceofpreferredequity' in cf_keys:
            preferred_issued = - cashflow.get('issuanceofpreferredequity')
        else:
            preferred_issued = 0

        if 'repurchaseofpreferredequity' in cf_keys:
            preferred_repurchased = cashflow.get('repurchaseofpreferredequity')
        else:
            preferred_repurchased = 0

        net_debt = (debt_repayment - debt_issuance)
        net_equity = (common_repurchased - common_issued) + (preferred_repurchased - preferred_issued)
        mkt_cap = Share(ticker).get_market_cap()

        if mkt_cap != None:
            if mkt_cap[-1] == 'B':
                mkt_cap = float(mkt_cap[:-1]) * 1000000000
            elif mkt_cap[-1] == 'M':
                mkt_cap = float(mkt_cap[:-1]) * 1000000
            else:
                mkt_cap = mkt_cap[-1]
                    
        shareholder_yield = ((dividends + net_debt + net_equity) / mkt_cap) * 100
        div_yield = (dividends / mkt_cap) * 100
        shareholder_contribution = dividends + net_debt + net_equity
                
        return(shareholder_yield, div_yield, shareholder_contribution)


    def dividend_rank(self, hurdle):
        hurdle = float(hurdle)
        div_companies = {}
        company_list = []
        sh_yield_list = []
        div_yield_list = []
        pb_list = []
        ps_list = []
        pe_list = []
        evebitda_list = []
        evfcf_list = []
        results = {}
        rank = {}
        
        with open('div_companies.csv', 'r') as f:
            reader = csv.DictReader(f)
            for line in reader:
                ticker = line['Ticker']
                name = line['Name']
                div_companies[ticker] = name
                company_list.append(ticker)
                
        spy_div = float(Share('SPY').get_dividend_yield())
        spy_mom = float(Invest().momentum('SPY')[1])

        for company in company_list:
            try:
                div_yield = float(Share(company).get_dividend_yield())
                if div_yield >= hurdle and div_yield >= spy_div:
                    
                    momentum = float(Invest().momentum(company)[1])
                    if momentum > spy_mom:
                        result = Invest().shareholder_yield(company)
                        ratios = Invest().fundamentals(company)
                        
                        shareholder_yield = float(result[0])
                        sh_yield_list.append(shareholder_yield)

                        div_yield_list.append(div_yield)

                        pricetobook = float(ratios[0])
                        if pricetobook != 0:
                            pb_list.append(1 / pricetobook)

                        pricetosales = float(ratios[1])
                        if pricetosales != 0:
                            ps_list.append(1 / pricetosales)

                        pricetoearnings = float(ratios[2])
                        if pricetoearnings != 0:
                            pe_list.append(1 / pricetoearnings)

                        evtoebitda = float(ratios[3])
                        if evtoebitda != 0:
                            evebitda_list.append(1/ evtoebitda)
                    
                        evtofcf = float(ratios[4])                    
                        if evtofcf != 0:
                            evfcf_list.append(1 / evtofcf)

                        divpayoutratio = float(ratios[5])
                        altzscore = float(ratios[6])

                        if shareholder_yield >= hurdle and divpayoutratio < 0.9 and pricetoearnings > 0:
                            results[company] = ([pricetobook, pricetosales, pricetoearnings, evtoebitda, evtofcf, shareholder_yield, div_yield, divpayoutratio, altzscore, momentum])
                        elif shareholder_yield >= hurdle and divpayoutratio > 0.9 and altzscore > 2.99 and pricetoearnings > 0:
                            results[company] = ([pricetobook, pricetosales, pricetoearnings, evtoebitda, evtofcf, shareholder_yield, div_yield, divpayoutratio, altzscore, momentum])
                    
                        ###  z-score < 1.81 is distressed  ###
                        ###  z-score > 2.99 is stable      ###

            except Exception as ex:
                template = "An exception of type {0} occured. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(company)
                print(message)
                
        company_out = list(results.keys())
        max_sh_yield = max(sh_yield_list)
        max_pb = max(pb_list)
        max_ps = max(ps_list)
        max_pe = max(pe_list)
        max_evebitda = max(evebitda_list)
        max_evfcf = max(evfcf_list)

        for comp in company_out:
            pb = results.get(comp)[0]
            ps = results.get(comp)[1]
            pe = results.get(comp)[2]
            evebitda = results.get(comp)[3]
            evfcf = results.get(comp)[4]
            sh_y = results.get(comp)[5]

            sh_yield_norm = sh_y / max_sh_yield
            
            if pb != 0:
                pb_norm = (1 / pb) / max_pb
            else: 
                pb_norm = 0

            if ps != 0:
                ps_norm = (1 / ps) / max_ps
            else:
                ps_norm = 0

            if pe != 0:
                pe_norm = (1 / pe) / max_pe
            else:
                pe_norm = 0

            if evebitda != 0:
                evebitda_norm = (1 / evebitda) / max_evebitda
            else:
                evebitda_norm = 0

            if evfcf != 0:
                evfcf_norm = (1 / evfcf) / max_evfcf
            else:
                evfcf_norm = 0

            rank_val = sh_yield_norm + ps_norm + pe_norm + evebitda_norm + evfcf_norm
            
            rank[rank_val] = comp

        ranked_list = list(rank.keys())
        ranked_list.sort(reverse = True)

        print('Ticker', 'SH Yld', 'DIV Yld', 'Pay %', 'Alt-Z', 'Rank', 'MOM', sep = '\t')  
        for v in ranked_list:
            symbol = rank.get(v)
            shareholder = round(results.get(symbol)[5], 2)
            div_yield = round(results.get(symbol)[6], 2)
            payout = round((results.get(symbol)[7] * 100), 2)
            zscore = round(results.get(symbol)[8], 2)
            mom = round(results.get(symbol)[9], 2)
            rank_value = round(v, 2)
            print(symbol, shareholder, div_yield, payout, zscore, rank_value, mom, sep = '\t')


    def div_portfolio(self, hurdle):
        port_companies = []
        company_list = []
        average_cost = {}
        investment_date = {}

        company_list = DB().securities()

        for comp in company_list:
            average_cost[comp] = DB().avg_cost(comp)
        
        print('', 'Dividend Portfolio', sep = '\n')
        print('Ticker', 'SHYOC', 'DVYOC', 'SHPO', 'DVPO', 'COST', 'PRICE', 'STOP', 'REC', sep = '\t')

        for company in company_list:
            transactions = DB().transactions(company)
            start_date = None
            for v in range(len(transactions)):
                trans_date = datetime.datetime.strptime(transactions[v]['date'], '%Y-%m-%d')
                if start_date == None:
                    start_date = trans_date
                else:
                    if trans_date < start_date:
                        start_date = trans_date
            start_date = str(start_date)[:10]
            price_history = Share(company).get_historical(Invest().weekday(start_date), Invest().weekday(today))
            adj_close = [float(price_history[x].get('Adj_Close')) for x in range(len(price_history))]
            max_price = max(adj_close)
            stop_loss = round(max_price * .8, 2)
            current_price = round(adj_close[0], 2)

            income = Financials().income_statement(company)

            if income == None:
                shares_outstanding = 0
                net_income = 0
            else:
                keys = income.keys()
        
            if 'weightedavedilutedsharesos' in keys:
                shares_outstanding = income.get('weightedavedilutedsharesos')
            else:
                shares_outstanding = 0

            if 'netincome' in keys:
                net_income = income.get('netincome')
            else:
                net_income = 0


            cashflow = Financials().cashflow_statement(company)
            
            if cashflow == None:
                shareholder_payout = 0
                div_payout = 0
            else:
                cf_keys = cashflow.keys()
        
            if 'paymentofdividends' in cf_keys:
                dividends = - cashflow.get('paymentofdividends')
            else:
                dividends = 0

            if 'repaymentofdebt' in cf_keys:
                debt_repayment = - cashflow.get('repaymentofdebt')
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
                common_repurchased = - cashflow.get('repurchaseofcommonequity')
            else:
                common_repurchased = 0

            if 'issuanceofpreferredequity' in cf_keys:
                preferred_issued = - cashflow.get('issuanceofpreferredequity')
            else:
                preferred_issued = 0

            if 'repurchaseofpreferredequity' in cf_keys:
                preferred_repurchased = cashflow.get('repurchaseofpreferredequity')
            else:
                preferred_repurchased = 0

            net_debt = (debt_repayment - debt_issuance)
            net_equity = (common_repurchased - common_issued) + (preferred_repurchased - preferred_issued)
            shareholder = (dividends + net_debt + net_equity)
            shareholder_payout = (shareholder / net_income) * 100
            div_payout = (dividends / net_income) * 100
            cost = average_cost.get(company)
            sh_yield_on_cost = ((shareholder / shares_outstanding) / cost) * 100
            div_yield_on_cost = ((dividends / shares_outstanding) / cost) * 100
            hurdle = float(hurdle)
            if sh_yield_on_cost >= hurdle and div_yield_on_cost >= hurdle and current_price > stop_loss:
                if shareholder_payout < 100 and div_payout < 100 and current_price > stop_loss:
                    rec = 'HOLD'
                else:
                    rec = 'REVIEW'
            else:
                rec = 'SELL'
            

            print(company, round(sh_yield_on_cost, 2), round(div_yield_on_cost, 2), round(shareholder_payout, 2), round(div_payout, 2), cost, current_price, stop_loss, rec, sep = '\t')


    def fundamentals(self, ticker, yr = None):
        if yr == None:
            ratios = Financials().fundamentals(ticker)
        else:
            ratios = Financials().fundamentals(ticker, year = yr)

        if ratios == None:
            shareholder_yield = 0
            div_yield = 0
            return(shareholder_yield, div_yield)
        else:
            keys = ratios.keys()

        ### List of keys can be found @ http://community.intrinio.com/docs/industrial-tags/ ###
        
        if 'divpayoutratio' in keys:
            try:
                div_payout = float(ratios.get('divpayoutratio'))
            except:
                div_payout = 0
        else:
            div_payout = 0

        if 'altmanzscore' in keys:
            try:
                z_score = float(ratios.get('altmanzscore'))
            except:
                z_score = 0
        else:
            z_score = 0

        ### z_score < 1.81 = distress   ###
        ### z_score > 2.99 = safe       ###
        ### otherwise = grey zone       ###

        if 'pricetobook' in keys:
            try:
                price_book = float(ratios.get('pricetobook'))
            except:
                price_book = 0
        else:
            price_book = 0

        if 'evtorevenue' in keys:
            try:
               price_sales = float(ratios.get('evtorevenue'))
            except:
               price_sales = 0
        else:
            price_sales = 0

        if 'pricetoearnings' in keys:
            try:
                price_earnings = float(ratios.get('pricetoearnings'))
            except:
                price_earnings = 0
        else:
            price_earnings = 0

        if 'evtoebitda' in keys:
            try:
                ev_ebitda = float(ratios.get('evtoebitda'))
            except:
                ev_ebitda = 0
        else:
            ev_ebitda = 0

        if 'evtofcff' in keys:
            try:
                ev_fcf = float(ratios.get('evtofcff'))
            except:
                ev_fcf = 0
        else:
            ev_fcf = 0

        return(price_book, price_sales, price_earnings, ev_ebitda, ev_fcf, div_payout, z_score)

                
    def error(self):
        print('Invalid argument.','', sep ='\n')
        print('Valid arguments:')
        print('[-rebalance]  Returns tax deferred recommendations')
        print('[-divrank]    Returns ranked list based on shareholder yield')
        print('[-etfrank]    Returns ranked list of ETFs based on momentum')
        print('')
        print('[-buy]        Add a buy transaction to DB')
        print('[-sell]       Add a sell transaciton to DB')
        print('[-dividend]   Add a dividend transaction to DB')
        print('')
        print('[-mom]        Returns momentum for a security')
        print('[-tr]         Returns total return for specified period')
        print('[-yield]      Returns shareholder & dividend yield for a security')
          
        


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
    elif arg == '-divrank':
        hurdle = float(input('DIV Hurdle Rate: '))
        Invest().dividend_rank(hurdle)
    elif arg == '-divport':
        hurdle = input('Hurdle Rate: ')
        Invest().div_portfolio(hurdle)
    elif arg == '-etfrank':
        number = input('# of Funds: ')
        amt = input('Amt to Invest: ')
        Invest().etf_rank(number, amt)
    elif arg == '-rebalance':
        hurdle = float(input('DIV Hurdle Rate: '))
        Invest().four01k()
        Invest().etf()
        Invest().div_portfolio(hurdle)
    elif arg == '-buy':
        DB().add('buy')
    elif arg == '-sell':
        DB().add('sell')
    elif arg == '-dividend':
        DB().add('dividend')
    else:
        Invest().error()
    
