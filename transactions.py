from tinydb import TinyDB, Query

transaction_db = TinyDB('transaction_db.json')

class DB():

    def __init__(self):
        pass

    def add(self, trans_type):
        date = input('Date of Transaction (YYYY-MM-DD): ')
        ticker = input('Ticker: ').upper()
        shares = int(input('# of Shares: '))
        price = float(input('$ per Share: '))
        trans_type = str(trans_type).lower()
        record = {'date': date, 'security': ticker, 'shares': shares, 'price': price, 'trans_type': trans_type}
        
        if trans_type == 'buy':
            transaction_db.insert(record)
            print('Buy record added')
            
        elif trans_type == 'sell':
           owned_shares = DB().num_shares(ticker)
           if owned_shares >= shares:
               transaction_db.insert(record)
               print('Sell record added')
           else:
               print('Sell amt > owned shares')

        elif trans_type == 'dividend':
            owned_shares = DB().num_shares(ticker)
            if owned_shares > 0:
                transaction_db.insert(record)
                print('Dividend record added')

        else:
            print('Invalid record.  No database update occured.')

    def num_shares(self, ticker):
        ticker = ticker.upper()
        buys = transaction_db.search((Query().security == ticker) & (Query().trans_type == 'buy'))
        sold = transaction_db.search((Query().security == ticker) & (Query().trans_type == 'sell'))
        buy_count = len(buys)
        sell_count = len(sold)

        if buy_count == 0:
            print('No record of security in DB')
                
        elif buy_count > 0:
            owned_shares = 0
            for x in range(buy_count):
                buy_amt = int(buys[x].get('shares'))
                owned_shares += buy_amt

            for y in range(sell_count):
                sell_amt = int(sold[y].get('shares'))
                owned_shares += -sell_amt

        return(owned_shares)

    def avg_cost(self, ticker):
        ticker = ticker.upper()
        buys = transaction_db.search((Query().security == ticker) & (Query().trans_type == 'buy'))
        sold = transaction_db.search((Query().security == ticker) & (Query().trans_type == 'sell'))
        div = transaction_db.search((Query().security == ticker) & (Query().trans_type == 'dividend'))
        buy_count = len(buys)
        sell_count = len(sold)
        div_count = len(div)

        if buy_count == 0:
            print('No record of security in DB')

        elif buy_count > 0:
            owned_shares = 0
            total_spend = 0
            for x in range(buy_count):
                buy_number = int(buys[x].get('shares'))
                buy_cost = float(buys[x].get('price')) * buy_number

                owned_shares += buy_number
                total_spend += buy_cost

            for y in range(sell_count):
                sell_number = int(sold[y].get('shares'))
                sell_cost = float(sold[y].get('price')) * sell_number

                owned_shares += -sell_number
                total_spend += -sell_cost

            for z in range(div_count):
                div_number = int(div[z].get('shares'))
                div_income = float(div[z].get('price')) * div_number

                total_spend += -div_income

            average_cost = round((total_spend / owned_shares), 2)

        return(average_cost)

    def transactions(self, ticker = None):
        if ticker == None:
            transactions = transaction_db.all()
        else:
            ticker = ticker.upper()
            transactions = transaction_db.search(Query().security == ticker)

        return(transactions)

    def securities(self):
        ticker_list = []
        transactions = DB().transactions()
        for v in range(len(transactions)):
            ticker = transactions[v]['security']
            if ticker not in ticker_list:
                ticker_list.append(ticker)

        return(ticker_list)
                
