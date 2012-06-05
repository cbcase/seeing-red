#!/usr/bin/env python



from util.helper import *
import glob
import sys
from collections import defaultdict

nruns = 10 # Number of runs for your experiment
nfiles = 0

font = {'size'   : 20}

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

def parse_one_column_data(filename):
    l1 = []
    lines = open(filename).read().split('\n')
    for l in lines:
        k = l[0:3]
        if l.strip() == "" or k.isalpha():
            continue
        l1.append(float(l.split(',')[0]))
    return l1

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

def plot_debug():
    testlog = 'test/tp_log'
    tp = parse_one_column_data(testlog)
    plt.figure(num=None, figsize=(12,4))
    plt.plot(range(0,len(tp)), tp, lw=1, c='black')
    plt.xlabel('Interval (10ms)')
    plt.ylabel('Throughput (bytes)')
    plt.title('Bursty traffic generation')
    print 'Saving to test/bursty_plot'
    plt.savefig('test/bursty_plot', dpi=300)
    plt.close()

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
    plt.close()

def plot_sim2():
    redlog = 'sim2/redlog'
    dtlog = 'sim2/dtlog'

    m.rc('font', **font)  # set font size for all plots

    """ Plot RED data """
    red_bufsize, red_tp, red_n5_tp, red_qlen = parse_four_column_data(redlog)
    red_n5_tp = [z*100 for z in red_n5_tp]
    plt.figure(1, figsize=(12, 24))
    
    plt.subplot2grid((4,1), (0,0), rowspan=2)
    plt.plot(red_bufsize, red_n5_tp, lw=6, c='black')
    f = open(redlog + 'tp', 'r')
    lines = f.readlines()
    f.close()
    i = 0
    for line in lines:
        plt.scatter([red_bufsize[i]]*10,
                    [100*float(line.split(',')[z]) for z in range(0,10)],
                    c='black')
        i += 1
    
    plt.ylim(0, 4)
    plt.xlim(2, 15)
    plt.xlabel('Minimum Threshold')
    plt.ylabel('Node 5 Throughput (%)')
    
    plt.subplot2grid((4,1), (2,0))
    plt.plot(red_bufsize, red_qlen, lw=6, c='black')
    plt.ylim(0, 15)
    plt.xlim(2, 15)
    plt.xlabel('Minimum Threshold')
    plt.ylabel('Average Queue (in packets)')
 
    plt.subplot2grid((4,1), (3,0))
    plt.plot(red_bufsize, red_tp, lw=6, c='black')
    plt.ylim(0, 1)
    plt.xlim(2, 15)
    plt.xlabel('Minimum Threshold')
    plt.ylabel('Average Link Utilization')

    print 'Saving to sim2/redplot'
    plt.savefig('sim2/redplot')
    plt.close()

    

    """ Plot DropTail data """
    dt_bufsize, dt_tp, dt_n5_tp, dt_qlen = parse_four_column_data(dtlog)
    dt_n5_tp = [z*100 for z in dt_n5_tp]

    plt.figure(1, figsize=(12, 24))
    
    plt.subplot2grid((4,1), (0,0), rowspan=2)
    plt.plot(dt_bufsize, dt_n5_tp, lw=6, c='black')
    f = open(dtlog + 'tp', 'r')
    lines = f.readlines()
    f.close()
    i = 0
    for line in lines:
        plt.scatter([dt_bufsize[i]]*10,
                    [100*float(line.split(',')[z]) for z in range(0,10)],
                    c='black')
        i += 1

    plt.ylim(0, 4)
    plt.xlim(7, 23)
    plt.xlabel('Buffer Size')
    plt.ylabel('Node 5 Throughput (%)')
    
    plt.subplot2grid((4,1), (2,0))
    plt.plot(dt_bufsize, dt_qlen, lw=6, c='black')
    plt.ylim(0, 15)
    plt.xlim(7, 23)
    plt.xlabel('Buffer Size')
    plt.ylabel('Average Queue (in packets)')
 
    plt.subplot2grid((4,1), (3,0))
    plt.plot(dt_bufsize, dt_tp, lw=6, c='black')
    plt.ylim(0, 1)
    plt.xlim(7, 23)
    plt.xlabel('Buffer Size')
    plt.ylabel('Average Link Utilization')

    print 'Saving to sim2/sim2plot'
    plt.savefig('sim2/dtplot')
    plt.close()
    


