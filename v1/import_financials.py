#!/usr/bin/env python

import argparse
import bs4
import datetime
import time
import logging
import re
import requests
from bs4 import BeautifulSoup
import threading
import common
import data
import Quandl

####
# Setup tor to use for all imports
import socks
import socket 
import requests

#socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
#socket.socket = socks.socksocket
#####

QUAND_KEY = "1BCHxHp1ExoE4hXRmafE"
BATCH = 100
LOGGER = logging.getLogger('import_financial_data')
MONEY = { '': 10**3, 'M': 10**6, 'B': 10**9 }
MONEY_RE = re.compile(r'^\$?(\-?\d+\.?\d*)([MB])?$')


def get_time():
    now = datetime.date.today()
    return now

def chunks(list, n):
    for i in xrange(0, len(list), n):
        yield list[i:i+n]


def check_valid(value):
    if value == 'N/A':
        value = None
        return value
    
    if value is None:
        value = None
        return value
    
    value = str(value)
    value = value.replace(',', '')
    
    return value

def decode_float(value):
    if isinstance(value, float):
        return value
    
    value = check_valid(value)
    
    if value is None:
        return value
    
    try:
        value = float(value)
        return value
    
    except:
        print "could not convert value %s" % value
    
    return value


def decode_percent(value):
    value = check_valid(value)

    if value is None:
        return value

    percent = '%'
    if value.endswith(percent):
        value = value.strip(percent)

    return float(value)


def decode_money(value):
    value = check_valid(value)

    if not value:
        return None

    results = MONEY_RE.search(value)

    if not results:
        raise TypeError('invalid money: %s' % value)

    value = float(results.group(1))
    abbr = results.group(2) or ''

    return float(value * MONEY[abbr]) / 1000

def decode_quandl(string):
    value_list = []
    string = str(string)
    value = re.search(r'\d{4}.*', string)
    value = value.group()
    value_list = value.split(' ')
    value = (value_list[-1])
    return value

def get_yahoo_roa(companies):
    
    url = 'https://finance.yahoo.com/q/ks'
    
    for company in companies:
        LOGGER.info('Getting ks: %s' % company.symbol)
        
        map_data = {
            'Return on Assets (ttm):': {
                'key': 'return_on_assets',
                'decode': decode_percent,
            },
            'Return on Equity (ttm):': {
                'key': 'return_on_equity',
                'decode': decode_percent,
            },
        }
        
        response = requests.get(url, params={'s': company.symbol})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for doc in soup.body.find_all('tr'):
            try:
                md = map_data[doc.td.text]
                if doc.td.text in map_data:
                    md['value'] = doc.contents[1].text.strip()
            except:
                continue
        
        extra = {}
        
        for md in map_data.values():
            if 'value' not in md:
                continue
            value = md['decode'](md['value'])
            if value is not None:
                extra[md['key']] = value
        
        if extra:
            timestamp = get_time()
            LOGGER.info('Setting ks: %s: %s' % (company.symbol, extra))
            data.set_financial_data(company=company, symbol=company.symbol, date=timestamp, **extra)
        else:
            LOGGER.info('Skipping ks: %s' % company.symbol)


def get_quandl(companies):

    for i, company in enumerate(companies):
        
        q_codes ={
            "net_income" : "NET_INCOME_Q",
            "total_assets" : "TOTAL_ASSETS_Q",
            "shares_outstanding" : "TOTAL_COMMON_SHARES_OUTSTANDING_Q"
            }

        financials = {}
        
        LOGGER.info('Getting quandl income & assets for: %s' % company.symbol)                          
        
        for k, v in q_codes.iteritems():
            code = "RAYMOND/" + company.symbol + "_" + v

            try:
                stat = Quandl.get(code, rows="1", authtoken=QUAND_KEY)
                stat = decode_quandl(stat)
                stat = decode_float(stat)
                financials.update({k : stat})
                    
            except:
                stat = "N/A"
                stat = decode_float(stat)
                financials.update({k : stat})
            
        LOGGER.info('%s --- %s:' % (company.symbol, financials))                          
        timestamp = get_time()
        data.set_financial_data(
            company=company, 
            symbol=company.symbol,
            date=timestamp,
            **financials
            )
        

def yahoo_finance(sleep_time):
    
    companies = list(data.get_companies())
    companies = [companies[i:i+BATCH] for i in range(0, len(companies), BATCH)]

    for i, batch in enumerate(companies):
        if i > 0: time.sleep(sleep_time)

        batch = dict([(c.symbol, c) for c in batch])
        url = 'https://query.yahooapis.com/v1/public/yql'
        params = {
            'q': 'select * from yahoo.finance.quotes where symbol IN ("%s")' % '", "'.join(batch.keys()),
            'format': 'json',
            'env': 'http://datatables.org/alltables.env',
        }
        response = requests.get(url, params=params)
        body = response.json()

        LOGGER.info('Getting quotes: %s' % ', '.join(batch.keys()))

        for item in body['query']['results']['quote']:
            company = batch[item['symbol']]
            timestamp = get_time()
            data.set_financial_data(
                company=company,
                symbol=company.symbol,
                date=timestamp,
                ask=decode_money(item.get('Ask')),
                market_cap=decode_money(item.get('MarketCapitalization')),
                ebitda=decode_money(item.get('EBITDA')),
                pe_ratio_ttm=decode_float(item.get('PERatio')),
                peg_ratio=decode_float(item.get('PEGRatio')),
                DividendYield = decode_float(item.get('DividendYield')),
                OneyrTargetPrice = decode_float(item.get('OneyrTargetPrice')),
                EPSEstimateCurrentYear = decode_float(item.get('EPSEstimateCurrentYear')),
                EPSEstimateNextYear = decode_float(item.get('EPSEstimateNextYear')),
                EPSEstimateNextQuarter = decode_float(item.get('EPSEstimateNextQuarter')),
            )


def quandl(sleep_time):
    companies = list(data.get_companies())

    companies = chunks(companies, BATCH)

    work = []
    
    for c in companies:
        t = threading.Thread(target=get_quandl(c))
        work.append(t)
    
    t.start()

def yahoo_roa(sleep_time):
    companies = list(data.get_companies())

    companies = chunks(companies, BATCH)

    work = []
    
    for c in companies:
        t = threading.Thread(target=get_yahoo_roa(c))
        work.append(t)
    
    t.start()


def main():
    common.setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('--sleep-time', dest='sleep_time', type=float, default=1)

    subparsers = parser.add_subparsers()

    parser_yahoo_finance = subparsers.add_parser('yahoo_finance')
    parser_yahoo_finance.set_defaults(func=yahoo_finance)
    
    parser_quandl = subparsers.add_parser('quandl')
    parser_quandl.set_defaults(func=quandl)


    parser_yahoo_roa = subparsers.add_parser('yahoo_roa')
    parser_yahoo_roa.set_defaults(func=yahoo_roa)
    
    args = parser.parse_args()
    args.func(sleep_time=args.sleep_time)


if __name__ == '__main__':
    main()
