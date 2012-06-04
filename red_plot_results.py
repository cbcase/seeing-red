#!/usr/bin/env python



from util.helper import *
import glob
import sys
from collections import defaultdict

nruns = 10 # Number of runs for your experiment
nfiles = 0

def first(lst):
    return map(lambda e: e[0], lst)

def second(lst):
    return map(lambda e: e[1], lst)

def avg(lst):
    return sum(lst)/len(lst)

def median(lst):
    l = len(lst)
    lst.sort()
    return lst[l/2]

def parse_two_column_data(filename):
    l1 = []
    l2 = []
    lines = open(filename).read().split("\n")
    for l in lines:
        k = l[0:3]
        if l.strip() == "" or k.isalpha():
            continue
        l1.append(float(l.split(',')[0]))
        l2 .append(float(l.split(',')[1]))
    return l1, l2

def parse_four_column_data(filename):
    l1 = []
    l2 = []
    l3 = []
    l4 = []
    lines = open(filename).read().split("\n")
    for l in lines:
        k = l[0:3]
        if l.strip() == "" or k.isalpha():
            continue
        l1.append(float(l.split(',')[0]))
        l2.append(float(l.split(',')[1]))
        l3.append(float(l.split(',')[2]))
        l4.append(float(l.split(',')[3]))
    return l1, l2, l3, l4

def plot_sim1():
    redlog = 'sim1/redlog'
    dtlog = 'sim1/dtlog'

    red_throughput, red_qlen = parse_two_column_data(redlog)
    dt_throughput, dt_qlen = parse_two_column_data(dtlog)

    plt.figure(num=None, figsize=(8,4))
    plt.scatter(red_throughput, red_qlen, s=60, c='r', marker='^', label='RED')
    plt.scatter(dt_throughput, dt_qlen, s=60, c='b', marker='s', label='DropTail')
    #first(plot_quido), second(plot_quido), lw=2, label="RTT*C/$\sqrt{n}$")

    plt.xlim((0, 1))
    plt.legend(loc=2)
    plt.xlabel("Throughput")
    plt.ylabel("Average queue length (pkts)")

    print "Saving to sim1/sim1plot"
    plt.savefig('sim1/sim1plot')

def plot_sim2():
    redlog = 'sim2/redlog'
    dtlog = 'sim2/dtlog'
    
    dt_bufsize, dt_tp, dt_n5_tp, dt_qlen = parse_four_column_data(dtlog)
    dt_n5_tp = [z*100 for z in dt_n5_tp]
    plt.figure(1, figsize=(8, 24))
    
    plt.subplot(3, 1, 1)
    plt.plot(dt_bufsize, dt_n5_tp)
    plt.ylim(0, 4)
    plt.xlabel('Buffer Size')
    plt.ylabel('Node 5 Throughput (%)')
    
    plt.subplot(3, 1, 2)
    plt.plot(dt_bufsize, dt_qlen)
    plt.ylim(0, 15)
    plt.xlabel('Buffer Size')
    plt.ylabel('Average Queue (in packets)')

    
    plt.subplot(3, 1, 3)
    plt.plot(dt_bufsize, dt_tp)
    plt.ylim(0, 1)
    plt.xlabel('Buffer Size')
    plt.ylabel('Average Link Utilization')

    print 'Saving to sim2/sim2plot'
    plt.savefig('sim2/sim2plot')
    


