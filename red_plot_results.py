#!/usr/bin/env python



from util.helper import *
import glob
import sys
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--out',
                    help="Save plot to output file, e.g.: --out plot.png",
                    dest="out",
                    default=None)

parser.add_argument('--dir',
                    dest="dir",
                    help="Directory from which outputs of the sweep are read.",
                    required=True)

args = parser.parse_args()
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

redlog = 'sim1/redlog'
dtlog = 'sim1/dtlog'

red_throughput, red_qlen = parse_two_column_data(redlog)
dt_throughput, dt_qlen = parse_two_column_data(dtlog)

plt.figure(num=None, figsize=(8,4))
plt.scatter(red_throughput, red_qlen, s=40, c='r', marker='^', label='RED')
plt.scatter(dt_throughput, dt_qlen, s=40, c='b', marker='s', label='DropTail')
#first(plot_quido), second(plot_quido), lw=2, label="RTT*C/$\sqrt{n}$")
"""
# Should you want the BDP plot
plt.plot(first(plot_bdp), second(plot_bdp), lw=2, label="RTT*C")

# Plot results from Neda's experiment
parse_nedata2('nedata2.txt')
median_yneda = []
keys = list(sorted(nedata.keys()))
for k in keys:
    median_yneda.append(median(nedata[k]))
plt.plot(keys, median_yneda, lw=2, label="Hardware-Median",
         color="black", ls='--', marker='d', markersize=10)


keys = list(sorted(data.keys()))

for i in xrange(nruns):
    try:
        values = [mndata[k][i] for k in keys]
    except:
        break

    if i == 0:
        label = "Mininet"
    else:
        label = ''
    plt.plot(keys, values,
             lw=1, label=label, color="red")

avg_mn = []
for k in keys:
    avg_mn.append(avg(data[k]))

plt.plot(keys, avg_mn, lw=2, label="Mininet", color="red", marker='s', markersize=10)

#plt.xscale('log')
#plt.yscale('log')
"""

plt.xlim((0, 1))
plt.legend(loc=2)
plt.xlabel("Throughput")
plt.ylabel("Average queue length (pkts)")

if args.out:
    print "Saving to %s" % args.out
    plt.savefig(args.out)
else:
    plt.show()


