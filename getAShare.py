# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 15:13:54 2017
@author: hzxieshukun
"""

import requests
import time
import re
import json
import sys
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding("utf-8")

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
'Accept':'text/html;q=0.9,*/*;q=0.8',
'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
'Connection':'close',
}

cookie={'TrackID':'1u75REUv6kEgYtLCd7-YlAUseP0GD9sIjoF671jkay9iCE-Jbs9luTWc9ieN9fzsr80PMIrlL1rU8De4Ko9FIPQ',
'__jda':'122270672.1490696078674303481197.1490696079.1490696079.1490771194.2',
'__jdb':'122270672.9.1490696078674303481197|2.1490771194',
'__jdc':'122270672',
'__jdu':'1490696078674303481197',
'__jdv':'122270672|www.huihui.cn|-|referral|-|1490696078675',
'pinId':'qMsxAnxs5SU'}

all_url = 'http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/'
ss_url = 'http://q.10jqka.com.cn/index/index/board/ss/field/zdf/order/desc/page/'
hs_url = 'http://q.10jqka.com.cn/index/index/board/hs/field/zdf/order/desc/page/'
end_url = '/ajax/1/'

updown_url = ''
##base info
ids = []
names = []
now_prices = []
up_down_rates = []
up_downs = []
up_rates = []
turnover_rates = []
volume_ratios = []
amplitudes = []
turnovers = []
tradable_shares = []
market_values = []
pe_ratios = []

ids_names = {}

##date to calc
long_term = 30

##up down data
##updowns = [{'id':id, 'prices':[], 'updowns':[]}, ...]
all_shares_updowns = []

def write_base_infos(file_name):
    with open(file_name, 'a') as f:
        f.write("id\tname\tnow_prices\tup_down_rates\tup_downs\tup_rates\tturnover_rates\t" + \
                "volume_ratios\tamplitudes\tturnovers\ttradable_shares\tmarket_values\tpe_ratios\n")
        for i in range(len(ids)):
            info = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (ids[i], names[i], now_prices[i], \
                    up_down_rates[i], up_downs[i], up_rates[i], turnover_rates[i], volume_ratios[i], \
                    amplitudes[i], turnovers[i], tradable_shares[i], market_values[i], pe_ratios[i])
            f.write(info)

def write_updown_infos(file_name):
    with open(file_name, 'w') as f:
        for i in range(len(all_shares_updowns)):
            info = "%s\n" % json.dumps(all_shares_updowns[i])
            f.write(info)
            
def write_html(file_name, html):
    with open(file_name, 'w') as f:
        if html != "":
            f.write(html)
            f.write("\n")
            
def get_base_data(base_url, page_num):
    url = base_url+ str(page_num) + end_url
    print url
    r = requests.get(url=url,headers=headers)
    html = r.content
    soup = BeautifulSoup(html)
    trs = soup.find_all("tr")
    line = 0
    if len(trs) == 1:
        return 0
    for tr in trs:
        try:
            line += 1
            if line == 1:continue
            tds = tr.find_all('td')
            if len(tds) < 15:
                continue
            ids.append(tds[1].text)
            names.append(tds[2].text)
            now_prices.append(tds[3].text)
            up_down_rates.append(tds[4].text)
            up_downs.append(tds[5].text)
            up_rates.append(tds[6].text)
            turnover_rates.append(tds[7].text)
            volume_ratios.append(tds[8].text)
            amplitudes.append(tds[9].text)
            turnovers.append(tds[10].text)
            tradable_shares.append(tds[11].text)
            market_values.append(tds[12].text)
            pe_ratios.append(tds[13].text)
        except:
            print "error at %s" % (tr)
    time.sleep(2)
    return 1

def get_updown_data():
    url1 = 'http://d.10jqka.com.cn/v2/line/hs_'
    url2 = '/00/last.js'
    print "begin to hanle shares up and updow"
    num = 0
    for id in ids:
        url = url1 + str(id) + url2
        print url
        r = requests.get(url=url,headers=headers)
        html = r.content
        data = re.findall(r'"data":"(.*?)","issuePrice', html)[0].split(';')
        prices = []
        updowns = []
        if len(data) < long_term + 1:continue
        for i in range(len(data) - 1, len(data) - long_term - 2, -1):
            date, open_price, high_price, low_price, final_price, t1, t2, t3 = data[i].split(',')
            prices.append(float(final_price))
        prices.reverse()
        for i in range(1, len(prices)):
            updowns.append((prices[i] - prices[i - 1]) / prices[i - 1])
        prices.pop(0)
        info = {'prices':prices, 'updowns':updowns, 'id':str(id), 'name':ids_names[id]}
        all_shares_updowns.append(info)
        num += 1
        time.sleep(0.5)
        
def load_base_data(filename):
    with open(filename) as f:
        f.readline()
        for line in f:
            id, name = line.split('\t')[0:2]
            ids.append(id)
            ids_names.setdefault(id, name)
        
if __name__ == "__main__":
#    for i in range(500):
#        result = get_base_data(ss_url, i+1)
#        if result == 0:
#            break
#    for i in range(500):
#        result = get_base_data(hs_url, i+1)
#        if result == 0:
#            break
#    begin = 1
#    end = 150
#    for i in range(begin, end + 1):
#        result = get_base_data(all_url, i)
#        if result == 0:
#            break
#    write_base_infos('shares_base_infos.txt')
    load_base_data('shares_base_infos.txt')
    get_updown_data()
    write_updown_infos("shares_updowns_infos.txt")