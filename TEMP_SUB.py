import plotly.graph_objects as go
import copy_ as cp
dt = 'date_timestamp'
import psycopg2;import pandas as pd;import process as dp;import functions_straddle as fn;from pandas.errors import SettingWithCopyWarning;import GeeksCalculator as gk;import importlib;import warnings;importlib.reload(dp);importlib.reload(cp);importlib.reload(fn);importlib.reload(gk);warnings.simplefilter(action='ignore', category=FutureWarning);warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)
conn = psycopg2.connect(dbname="qdap_test",user="amt",password="your_password",host="192.168.2.23",port="5432")
cursor = conn.cursor()

importlib.reload(dp); importlib.reload(fn)
all_trades, all_execs , trade_id = {} , {} ,0

print("please provide the date range in which you want to trade in  ")
print("Start day (Min = 2020-01-01)")
st = input()
print("End day (Max = 2024-06-30)")
en = input()

ranges = pd.date_range(start=st, end=en)
# entry time
eh,em = 9,30
tradeid = 0

all_running_pnl, all_call_movement, all_put_movement, all_call_iv, all_put_iv = [],[],[],[],[]
print("please provide the list of symbols on which you wnat to trade ")
list_symbol = list(input().split(sep=','))

for symbol in list_symbol:
    all_trades[symbol],all_execs[symbol] = [] , []
    for d_t in ranges:
        try:
            futures = dp.FetchFuturesByDate(cursor,symbol,d_t)
            if not futures.empty:
                options = dp.FetchOptionsByDateCsv(symbol,d_t.date())
                print(symbol,str(d_t.date()))
                gen_call, gen_put = options[options['opt_type'] == 'CE'], options[options['opt_type'] == 'PE']
                call, put = dp.fetch_call_put_(options)
                call.ffill(inplace=True) ; put.ffill(inplace=True)
                tradeid,execs, trades, running_pnl, net_pnl, capital, rollover, positions, difference, call_movement, put_movement,delta_put, delta_call, call_iv, put_iv, iv, atr, civ = fn.generate_trades_syn(eh,em,tradeid,futures, call, put, gen_call, gen_put, io=0,DeltaLB=0.2,delta_range=0.1,DeltaUB=0.55, buying='close', selling='close', initial_capital=100000)
                all_running_pnl.extend(running_pnl);    all_call_movement.extend(call_movement);  all_put_movement.append(put_movement);   all_call_iv.extend(call_iv);  all_put_iv.extend(put_iv);    all_trades[symbol].extend(trades);  all_execs[symbol].extend(execs)
                if len(trades) == 0:
                    print(f"No trades took place on {d_t.date()}")
        except Exception as e:
            print(f"Error on date {d_t} for symbol {symbol}: {str(e)}")


sharpie,stats = fn.sharpie_straddle_Combine(all_trades)
print("sharpie = ",sharpie, sep='')
KPIs = fn.calculate_pnl_metrics(stats)
print('monthly_avg_profit/monthly_avg_loss : ',KPIs['monthly_avg_profit/monthly_avg_loss'],'\n','total pnl :',KPIs['total_pnl'],'\n','Max pnl : ',KPIs['max_pnl'],'\n','Min pnl : ',KPIs['min_pnl'],'\n','Win Ratio : ',KPIs['win_ratio'],sep='')
