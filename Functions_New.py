
from enum import Enum
from unittest import result
import numpy as np
import pandas as pd
import datetime
class Security_:
    def __init__(self,symbol,date_timestamp,open,high,low,close,volume,opt_type,strike,expiry,delta):
        self.symbol = symbol
        self.date_timestamp = date_timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.opt_type = opt_type
        self.strike = strike
        self.expiry = expiry
        self.delta = delta

class Security:
    def __init__(self, symbol, strike, opttype,price,dt,delta):
        self.Symbol = symbol
        self.Strike = strike
        self.OptType = opttype
        self.Price = price
        self.dt = dt
        self.delta = delta

class BasketSecurity:
    def __init__(self, symbol, strike, bstype,opttype,quantity):
        super().__init__(symbol,strike,opttype)
        self.BSType = bstype
        self.Quantity = quantity
        self.OptType = opttype

class Trade:
    def __init__(self,_id,dt,price,strike,tradetype,delta,log):
        self.dt = dt
        self.id = _id
        self.Price = price
        self.Strike = strike
        self.Delta = delta
        self.TradeType = tradetype
        self.Log = log

class Result(Enum):
    FAIL = 0
    SUCESS = 1

def GetSecurity(Opt,strike,dt,type_):
    Temp = Opt[(Opt['date_timestamp']==dt) & (Opt['opt_type']==type_) & (Opt['strike']==strike)]
    if Temp.empty:
        return None
    else:
        temp = Temp.iloc[0]
        return Security_(temp['symbol'],temp['date_timestamp'],temp['open'],temp['high'],temp['low'],temp['close'],temp['volume'],temp['opt_type'],temp['strike'],temp['expiry'],temp['delta'])

def GetSecurity(Option,strike,dt):
    Temp = Option[(Option['strike'] == strike) & (Option['date_timestamp']==dt)]
    if Temp.empty:
        return None
    else:
        temp = Temp.iloc[0]
        return Security_(temp['symbol'],temp['date_timestamp'],temp['open'],temp['high'],temp['low'],temp['close'],temp['volume'],temp['opt_type'],temp['strike'],temp['expiry'],temp['delta'])


def GetallOptionsClosetoDelta(options,delta,delta_range,date_timestamp,opt_type,file):
    delta = abs(delta)
    option = None
    if opt_type == 'PE':
        temp = options[(options['delta'].notna()) & (options['date_timestamp'] == date_timestamp) & (abs(options['delta']+delta)<=delta_range)].sort_values(by='delta')
        if temp.empty:
            return None
        abs_diff = np.abs(temp['delta'] - delta)
        key = np.argmin(abs_diff)
        if key-1 >= 0 and temp.iloc[key]['delta'] > delta:
            key-=1
        option = temp.iloc[key]
        return option
    else:
        temp = options[(options['delta'].notna()) & (options['date_timestamp'] == date_timestamp) & (abs(options['delta']-delta)<=delta_range)].sort_values(by='delta')
        if temp.empty:
            return None
        abs_diff = np.abs(temp['delta'] - delta)
        key = np.argmin(abs_diff)
        if key+1 < len(temp)  and temp.iloc[key]['delta'] < delta:
            key+=1
        option = temp.iloc[key]
        return option
    return None


def comf(temp):
    return Security_(temp['symbol'],temp['date_timestamp'],temp['open'],temp['high'],temp['low'],temp['close'],temp['volume'],temp['opt_type'],temp['strike'],temp['expiry'],temp['delta'])

def Submit(it,Ratio,TL,DB):
    if it.opt_type == 'PE': DB.pp += 1; DB.ps = it.strike
    else: DB.cp += 1; DB.cs = it.strike
    TL.append({'dt':it.date_timestamp,'price':it.close,'total':Ratio*it.close,'strike':it.strike,'quantity':Ratio,'opt_type':it.opt_type,'trade_type':'BUYING','delta':it.delta})

def Reverse(it,Ratio,TL,DB):
    if it.opt_type == 'PE': DB.pp -= 1; DB.ps = it.strike
    else: DB.cp -= 1; DB.cs = it.strike
    TL.append({'dt':it.date_timestamp,'price':it.close,'total':Ratio*it.close,'strike':it.strike,'quantity':Ratio,'opt_type':it.opt_type,'trade_type':'SELLING','delta':it.delta})

def Submit_(it,Ratio,TL,DB,P,key):
    if it.opt_type == 'PE': DB.pp += 1; DB.ps = it.strike
    else: DB.cp += 1; DB.cs = it.strike
    TL.append({'dt':it.date_timestamp,'price':it.close,'total':Ratio*it.close,'strike':it.strike,'quantity':Ratio,'opt_type':it.opt_type,'trade_type':'BUYING','delta':it.delta})
    P[key]['type']=it.opt_type
    if P[key]['ent'] == None:
        P[key]['ent'] = TL[-1].copy()
        P[key]['entry']=True
    else:
        P[key]['ext'] = TL[-1].copy()
        P[key]['exit']=True


def Reverse_(it,Ratio,TL,DB,P,key):
    if it.opt_type == 'PE':
        DB.pp -= 1
        DB.ps = it.strike
    else:
        DB.cp -= 1
        DB.cs = it.strike
    TL.append({'dt':it.date_timestamp,'price':it.close,'total':Ratio*it.close,'strike':it.strike,'quantity':Ratio,'opt_type':it.opt_type,'trade_type':'SELLING','delta':it.delta})
    P[key]['type']=it.opt_type
    if P[key]['ent'] == None:
        P[key]['ent'] = TL[-1].copy()
        P[key]['entry']=True
    else:
        P[key]['ext'] = TL[-1].copy()
        P[key]['exit']=True

class DB:
    def __init__(self,cp,pp,cs,ps):
        self.cp = cp ; self.pp = pp ; self.cs = cs; self.ps = ps



def trades(futures, gen_call, gen_put, io=0,gap = 15,delta_range=0.1,DeltaUB = 0.5,profit_cap = 20,Stop_loss = 10):
    Securities = []
    entry = False
    initial_capital = 100000
    db, TL = DB(0, 0, 0, 0), []
    keys = pd.date_range("09:15", "14:00", freq="15min").time
    positions = {k: {'call': None, 'put': None, 'null': True, 'entry': False, 'exit': False, 'type': None, 'ent': None, 'ext': None, 'ttype': None} for k in keys}
    call, put = [], []
    Plots = {k: [] for k in keys}

    with open(f"_Logs.txt", "w") as file:
        for i in range(1, len(futures) - 1):
            row = futures.iloc[i]
            dt = row['date_timestamp']
            print(f"TimeStamp: {dt} \n\n",file=file)
            row_i = futures.iloc[i - 1]

            # First loop through positions
            for k, v in positions.items():

                if k <= dt.time() and v['null']:
                    print(f"Attempting Subscribe for {k}",file=file)
                    Call = GetallOptionsClosetoDelta(gen_call, DeltaUB, delta_range / 2, dt, 'CE', file)
                    if Call is None:    print(f"No Call Available in range [{DeltaUB - delta_range}, {DeltaUB + delta_range}]", file=file)
                    else:
                        Put = GetallOptionsClosetoDelta(gen_put, DeltaUB, delta_range / 2, dt, 'PE', file)
                        if Put is None:    print(f"No Put Available in range [{DeltaUB - delta_range}, {DeltaUB + delta_range}]", file=file)
                        else:
                            print(f"Subscribed Call and Put for Entry of {k}",file=file)
                            v['call'], v['put'] = comf(Call), comf(Put)
                            v['null'] = False


            # Second loop for checking trades within a 15-minute window

            for k, v in positions.items():

                k_datetime = pd.Timestamp.combine(dt.date(), k)  # Convert `k` to a full datetime object
                if dt <= k_datetime + pd.to_timedelta(15, unit='m') and v['null'] == False and not v['entry']:

                    print(f"Checking For subscribed Securities for taking entry {k}",file=file)
                    Call = GetSecurity(gen_call, v['call'].strike, dt)
                    Put = GetSecurity(gen_put, v['put'].strike, dt)

                    if Call is not None:
                        if (Call.close - v['call'].close) * 100 > gap * v['call'].close:
                            print(f"Call Is Available and Has a Rise, Buying",file=file)
                            Submit_(Call, 1, TL, db, positions, k)
                        elif (v['call'].close - Call.close) * 100 > gap * v['call'].close:
                            print(f"Call Is Available and Has a Drop, Selling",file=file)
                            Reverse_(Call, 1, TL, db, positions, k)

                    elif Put is not None:
                        if (Put.close - v['put'].close) * 100 > gap * v['put'].close:
                            print(f"Put Is Available and Has a Rise, Buying",file=file)
                            Submit_(Put, 1, TL, db, positions, k)
                        elif (v['put'].close - Put.close) * 100 > gap * v['put'].close:
                            print(f"Put Is Available and Has a Drop, Selling",file=file)
                            Reverse_(Put, 1, TL, db, positions, k)

            for k, v in positions.items():
                if v['entry'] and v['exit']==False :
                    Sec = GetSecurity(gen_call,v['call'].strike, dt) if v['type'] == 'CE' else GetSecurity(gen_put, v['put'].strike, dt)
                    if Sec is not None:
                        Plots[k].append((dt, Sec.close))
                    else:
                        if (len(Plots[k]) > 0):
                            Plots[k].append((dt, Plots[k][-1][1]))
                        else:
                            Plots[k].append((dt, None))
                else:
                        Plots[k].append((dt, None))
                       
            # Third loop for handling existing positions
            for k, v in positions.items():
                if not v['null'] and v['entry'] and not v['exit']:
                    print(f"Checking for Exit conditions on {k}",file=file)
                    sec = GetSecurity(gen_call, v['call'].strike, dt) if v['type'] == 'CE' else GetSecurity(gen_put, v['put'].strike, dt)
                    if sec is not None:
                        # Plots[k].append((v['ent']['trade_type'],sec.close))

                        if (sec.close - v['ent']['price'])*100 >= profit_cap*(v['ent']['price']):
                            print(f"Closing position of {k}, Profit Cap Reached",file=file)
                            if v['ent']['trade_type'] == 'SELLING':
                                print(f"Buying for Closing position",file=file)
                                Submit_(sec, 1, TL, db, positions, k)
                            else:
                                print(f"Selling for Closing position",file=file)
                                Reverse_(sec, 1, TL, db, positions, k)
                        elif (v['ent']['price'] - sec.close)*100 >= Stop_loss*(v['ent']['price']):
                            print(f"Closing position of {k} , Stop_Loss Reached",file=file)
                            if v['ent']['trade_type'] == 'SELLING':
                                print(f"Buying for Closing position",file=file)
                                Submit_(sec, 1, TL, db, positions, k)
                            else:
                                print(f"Selling for Closing position",file=file)
                                Reverse_(sec, 1, TL, db, positions, k)
                    else:
                        pass
                        # Plots[k].append((v['ent']['trade_type'],None))




        for k, v in positions.items():
                if not v['null'] and v['entry'] and not v['exit']:
                    print(f"Checking for Final Exit condition on {k}",file=file)
                    sec = gen_call[gen_call['strike'] == v['call'].strike].iloc[-1] if v['type']=='CE' else gen_put[gen_put['strike']==v['put'].strike].iloc[-1]
                    sec = comf(sec)
                    print(f"Closing position of {k}, Final SQOff",file=file)
                    if v['ent']['trade_type'] == 'SELLING':
                        print(f"Buying for Closing position",file=file)
                        Submit_(sec, 1, TL, db, positions, k)
                    else:
                        print(f"Selling for Closing position",file=file)
                        Reverse_(sec, 1, TL, db, positions, k)

    return positions,Plots



def stats_(trades):
    pnl = []
    for k,v in trades.items():
        net_pnl = 0
        for a,s in v.items():
            if s['ent'] is not None:
                if s['ent']['trade_type'] == 'SELLING':
                    net_pnl += s['ent']['price']
                    net_pnl -= s['ext']['price']
                else:
                    net_pnl -= s['ent']['price']
                    net_pnl += s['ext']['price']
        pnl.append((k,net_pnl))

    return pnl

def TradeSummry(positions, filename="trade_logs.txt"):
    with open(filename, 'w') as file:
        net_pnl  = 0
        for a,s in positions.items():
            if s['ent'] is not None:
                if s['ent']['trade_type'] == 'SELLING':
                    net_pnl += s['ent']['price']
                    net_pnl -= s['ext']['price']
                else:
                    net_pnl -= s['ent']['price']
                    net_pnl += s['ext']['price']

        for key, position in positions.items():
            file.write(f"\nTrade Key: {key}\n")
            file.write("=======================================\n")

            # Write 'call' information if it exists and is not None
            if position.get('call') is not None:
                call = position['call']
                file.write(f"Call: {call.symbol} | {call.date_timestamp} | Strike: {call.strike} | Expiry: {call.expiry} | Delta: {call.delta}\n")

            # Write 'put' information if it exists and is not None
            if position.get('put') is not None:
                put = position['put']
                file.write(f"Put: {put.symbol} | {put.date_timestamp} | Strike: {put.strike} | Expiry: {put.expiry} | Delta: {put.delta}\n")

            # Write 'ent' entry details if it exists and is a dictionary
            if position.get('ent') is not None:
                ent = position['ent']
                file.write(f"Entry: Date: {ent['dt']} | Price: {ent['price']} | Total: {ent['total']} | Strike: {ent['strike']} | Quantity: {ent['quantity']} | "
                           f"Opt Type: {ent['opt_type']} | Trade Type: {ent['trade_type']} | Delta: {ent['delta']}\n")

            # Write 'ext' exit details if it exists and is a dictionary
            if position.get('ext') is not None:
                ext = position['ext']
                file.write(f"Exit: Date: {ext['dt']} | Price: {ext['price']} | Total: {ext['total']} | Strike: {ext['strike']} | Quantity: {ext['quantity']} | "
                           f"Opt Type: {ext['opt_type']} | Trade Type: {ext['trade_type']} | Delta: {ext['delta']}\n")

            # Write the type of trade and key flags
            file.write(f"Type: {position['ttype']} | Entry: {position['entry']} | Exit: {position['exit']} | Null: {position['null']}\n")

            file.write("=======================================\n\n")

        file.write(f"Net Pnl = {net_pnl}\n")
        file.write("\n=======================================\n\n")


