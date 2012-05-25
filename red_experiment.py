from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNetConnections

import sys
import os
from time import sleep, time
from subprocess import Popen, PIPE
import termcolor as T
from argparse import ArgumentParser

from red_topo import *

def get_txbytes(iface):
    f = open('/proc/net/dev', 'r')
    lines = f.readlines()
    for line in lines:
        if iface in line:
            break
    f.close()
    if not line:
        raise Exception("could not find iface %s in /proc/net/dev:%s" %
                        (iface, lines))
    # Extract TX bytes from:
    #Inter-|   Receive                                                |  Transmit
    # face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    # lo: 6175728   53444    0    0    0     0          0         0  6175728   53444    0    0    0     0       0          0
    return float(line.split()[9])


def get_rates(iface, nsamples=3, period=1.0,
              wait=3.0):
    """Returns rate in Mbps"""
    # Returning nsamples requires one extra to start the timer.
    nsamples += 1
    last_time = 0
    last_txbytes = 0
    ret = []
    sleep(wait)
    while nsamples:
        nsamples -= 1
        txbytes = get_txbytes(iface)
        now = time()
        elapsed = now - last_time
        #if last_time:
        #    print "elapsed: %0.4f" % (now - last_time)
        last_time = now
        # Get rate in Mbps; correct for elapsed time.
        rate = (txbytes - last_txbytes) * 8.0 / 1e6 / elapsed
        if last_txbytes != 0:
            # Wait for 1 second sample
            ret.append(rate)
        last_txbytes = txbytes
        print '.',
        sys.stdout.flush()
        sleep(period)
    return ret

def verify_latency(net):
    sink = net.getNodeByName('sink');
    for i in range(1, net.topo.numSources() + 1):
        host = net.getNodeByName('h%d' % i)
        for j in range(i + 1, net.topo.numSources() + 1):
            other_host = net.getNodeByName('h%d' % j)
            result = host.cmd('ping -c 3 %s' % other_host.IP())
            print 'h%d --> h%d' % (i, j)
            print result
        result = host.cmd('ping -c 3 %s' % sink.IP())
        print 'h%d --> sink' % i
        print result

def verify_bandwidth(net):
    sink = net.getNodeByName('sink')
    for i in range(1, net.topo.numSources() + 1):
        host = net.getNodeByName('h%d' % i)
        for j in range(i + 1, net.topo.numSources() + 1):
            other_host = net.getNodeByName('h%d' % j)
            net.iperf([host, other_host])
        net.iperf([host, sink])

def verify_throughput(net):
    print 'throughput at s1 s1-eth0: ' + str(get_rates('s1-eth0')) + ' Mbps'

CUSTOM_IPERF_PATH = '~/iperf-patched/src/iperf'
CONG = 'bic'
def start_senders(net):
    # Seconds to run iperf; keep this very high
    recvr = net.getNodeByName('sink')
    seconds = 3600
    for i in range (1, 3):
        h = net.getNodeByName('h%s' % i)
        for j in range (0, 1): #args.nflows=1
            h.cmd('%s -c %s -p %s -t %d -i 1 -yc -Z %s > %s/h%s.txt &' %
                  (CUSTOM_IPERF_PATH, recvr.IP(), 5001, seconds, CONG, os.getcwd(), i))

def start_receiver(net):
    recvr = net.getNodeByName('sink')
    recvr.cmd('%s -s -p %s > %s/iperf_server.txt &' %
              (CUSTOM_IPERF_PATH, 5001, os.getcwd()))

def start_tcpprobe():
    "Instal tcp_pobe module and dump to file"
    os.system("rmmod tcp_probe; modprobe tcp_probe;")
    Popen("cat /proc/net/tcpprobe > %s/tcp_probe.txt" %
          os.getcwd(), shell=True)

def stop_tcpprobe():
    os.system("killall -9 cat; rmmod tcp_probe &>/dev/null;")

def run_debug():
    topo = Fig6Topo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNetConnections(net)
    net.pingAll()

    verify_latency(net)
    verify_bandwidth(net)
    start_receiver(net)
    start_tcpprobe()
    start_senders(net)
    verify_throughput(net)
    net.stop()

def run_experiment_one():
    #set up Fig6Topo
    topo = Fig6Topo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNetConnections(net)
    net.pingAll()

    #open up TCP connections with max windows of 240 packets (roughly bw-delay product)
    #    NOTE: packets are 1000 bytes
    #    QUESTION: do I need to start_server/recvr?
    #get maximum possible throughput on link
    #run five 5-sec simulations for each of 11 sets of params for each DT and RED
    #    drop tail: 15 to 140 packets (15, 30, 45, 60, 75, 90, 100, 110, 120, 130, 140)
    #    RED: max buffer size of  100 packets,
    #         min_th ranging from 3 to 50 packets
    #         max_th := 3*min_th
    #         w_q := 0.002
    #         max_p := 1/50
    #
    #get average queue size over this interval (HOW?????)
    #compute throughput (can just say total_bytes/5sec)
    pass

def run_experiment_two():
    pass

def main():
    parser = ArgumentParser(description="RED experiments")
    parser.add_argument('--exp1',
                        action='store_true',
                        help='Run Experiment 1')
    parser.add_argument('--exp2',
                        action='store_true',
                        help='Run Experiment 2')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Run test')

    args = parser.parse_args()


    if not args.exp1 and not args.exp2 and not args.debug:
        print T.colored('You forgot to specify an experiment to run.\n' +
                        'Usage: red_experiment.py [-h] [--exp1] [--exp2]',
			'green')
    if args.exp1:
        run_experiment_one()
    if args.exp2:
        run_experiment_two()
    if args.debug:
        run_debug()

if __name__ =='__main__':
    main()
