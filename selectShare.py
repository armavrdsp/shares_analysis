#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 22:56:22 2017

@author: jiaqiu
"""

import time
import re
import json
import sys
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
zhfont = matplotlib.font_manager.FontProperties(fname="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

reload(sys)
sys.setdefaultencoding("utf-8")

all_updowns = []
results = {}

def load_updowns_data(filename):
    with open(filename) as f:
        for line in f:
            all_updowns.append(json.loads(line.strip('\n')))

##calc updwons entropy, entropy more large more better
def updown_ratio_analyse(id, updown, part_split):
    up_index = [i for i in range(len(updown)) if updown[i] >= 0]
    down_index = [i for i in range(len(updown)) if updown[i] < 0]
    up_num = len(up_index)
    down_num = len(down_index)
    p_up = float(up_num) / len(updown)
    p_down = float(down_num) / len(updown)
    p_k = [p_up, p_down]
    e1 = sum([-p_k[i] * math.log(p_k[i]) for i in range(len(p_k))]) \
        if p_up > 0 and p_down > 0 else 0.0
    index = [i for i in range(len(updown))]
    perm = np.random.permutation(len(updown) - part_split + 1)
    #index_split = [index[k:k+part_split] for k in range(0, len(index), part_split)]
    index_split = [index[k:k+part_split] for k in perm]
    es = []
    for i in range(part_split):
        part_up_index = [up_index[k] for k in range(up_num) if up_index[k] in index_split[i]]
        part_down_index = [down_index[k] for k in range(down_num) if down_index[k] in index_split[i]]
        p_up = len(part_up_index)
        p_down = len(part_down_index)
        p_k = [float(len(part_up_index)) / len(index_split[i]), float(len(part_down_index)) / len(index_split[i])]
        part_e = sum([-p_k[i] * math.log(p_k[i]) for i in range(len(p_k))]) if p_up > 0 and p_down > 0 else 0.0
        es.append(part_e)
#    print up_index
#    print down_index
#    print "up_num:%s" % up_num
#    print "down_num:%s" % down_num
#    print "e1:%s" % (e1)
#    print ("es:", es)
#    print "%s---part entropy:%s" % (id, es)
    return e1 * (sum(es) / len(es))

##write by math
def linefit(x , y):
    N = float(len(x))
    sx,sy,sxx,syy,sxy=0,0,0,0,0
    for i in range(0,int(N)):
        sx += x[i]
        sy += y[i]
        sxx += x[i]*x[i]
        syy += y[i]*y[i]
        sxy += x[i]*y[i]
    a = (sy*sx/N -sxy)/( sx*sx/N -sxx)
    b = (sy - a*sx)/N
    r = abs(sy*sx/N-sxy)/math.sqrt((sxx-sx*sx/N)*(syy-sy*sy/N))
    return a,b,r

##calc prices trend, trend is upper then score is higher
## y = ax + b
def price_trend_analyse(prices):
    x = [i for i in range(len(prices))]
    y = prices
    z1 = np.polyfit(x, y, 1)
    p1 = np.poly1d(z1)
    return p1[1]

def display_calc(rank, share, prices, updowns, save_folder):
    print "display--"
    x = [i for i in range(len(prices))]
    zero_y = [0 for i in range(len(prices))]
    plt.figure(1)
    ax1 = plt.subplot(212) 
    ax2 = plt.subplot(211)
    ##figure 1
    plt.plot(x, prices)
    title = "NO.%s--%s's prices and updowns" % (rank, share)
    plt.title(title)
    plt.ylabel('prices')
    #xmajorLocator = MultipleLocator(1)
    #ax1.xaxis.set_major_locator(xmajorLocator)
    plt.sca(ax1)
    ##figure 2
    plt.bar(x, updowns)
    plt.plot(x, zero_y, 'r--')
    plt.xlabel('day')
    plt.ylabel('updowns')
    #ax2.xaxis.set_major_locator(xmajorLocator)
    plt.sca(ax2)
    ##show
    #plt.show()
    ##savae
    save_file = "%s/NO.%s--%s.png" % (save_folder, rank, share)
    plt.savefig(save_file)
    plt.close()

def write_result(filename, result):
    with open(filename, 'w') as f:
        for i in result:
            f.write(i + "\n")
            
def share_analyse(recommend_num):
    shares_infos = {}
    num = 0
    result = []
    for info in all_updowns:
        id = info["id"]
        name = info["name"]
        updowns = info["updowns"]
        prices = info["prices"]
        shares_infos.setdefault("%s@%s" % (name, id), {"prices":prices, "updowns":updowns})
        updown_distribution = updown_ratio_analyse(id, updowns, 5)
        prices_trend = price_trend_analyse(prices[-len(prices) / 2:])
        #buy_p = 0.1 if updowns[-1] < 0 and updowns[-2] < 0 else -0.1
        score = (updown_distribution * 1 + prices_trend * 0) 
        results.setdefault("%s@%s" % (name, id), score)
        print "%s analyse done" % name
        if num > 100000:break
        num += 1
    results_sorted = sorted(results.iteritems(), key = lambda asd:asd[1], reverse = True)
    rank = 1
    print "display the top shares..."
    for name_id, score in results_sorted:
        tag = "NO.%s " % rank
        print tag
        result.append(tag + name_id)
        try:
            display_calc(rank, name_id, shares_infos[name_id]["prices"], shares_infos[name_id]["updowns"], "rank")
        except Exception, e:
            print e
            continue
        if rank >= recommend_num:break
        rank += 1
    write_result("recommend_shares.txt", result)
        
    
if __name__ == "__main__":
    print "begin to load share data..."
    load_updowns_data("shares_updowns_infos.txt")
    print "begin to analyse shares..."
    share_analyse(30)
    print "done"