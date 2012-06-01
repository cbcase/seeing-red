from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNetConnections

from multiprocessing import Process
from util.monitor import monitor_qlen

import sys, os, shutil
from time import sleep, time
from subprocess import Popen, PIPE
import termcolor as T
from argparse import ArgumentParser

from red_topo import *


#Path to patched iperf
CUSTOM_IPERF_PATH = '~/iperf-patched/src/iperf'

#Congestion control algorithm
CONG = 'bic'

#Size of a simulation packet in bytes
PKT_SZ_BYTES = 1000

#Path to FTP server executable
FTP_SERVER = './quote-ftp/server'

#Path to FTP client executable
FTP_CLIENT = './quote-ftp/client'


"Simulation 1 constants"

#Maximum window size for Simulation 1 flows
SIM1_MAX_WINDOW = 240

#Length of each flow in Simulation 1
SIM1_LEN_SEC = 5.0

#Number of servers in Simulation 1
SIM1_N_SENDERS = 2

#Directory to save Simulation 1 results into
SIM1_DIR = 'sim1'

#The queue lengths measured during sim1
QLENS_DIR = 'qlens'


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
    print '\n'
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

def show_tc(net):
    for i in range(1, net.topo.numSources() + 1):
        host = net.getNodeByName('h%d' % i)
        result = host.cmd('tc -s qdisc show')
        print ('h%d tc:' % i)
        print result
    sink = net.getNodeByName('sink')
    result = sink.cmd('tc -s qdisc show')
    print ('sink:')
    print result
    s1 = net.getNodeByName('s1')
    result = s1.cmd('tc -s qdisc show')
    print ('s1:')
    print result

def verify_throughput(net):
    print 'throughput at s1 s1-eth0: ' + str(get_rates('s1-eth0')) + ' Mbps'

def start_senders(net, n_senders):
    for i in range(1, n_senders+1):
        print 'starting server %d......' % i
        h = net.getNodeByName('h%d' % i)
        c = '%s &' % FTP_SERVER
        h.cmd(c)
        #h.sendCmd('tcpdump -s 65535 -w tcp_logdt%d-%d.pcap' % (i, j))

def start_receiver(net, n_senders, sim_duration, max_window_list):
    recvr = net.getNodeByName('sink')
    for i in range(1, n_senders+1):
        print 'receiver initiating connection to h%d' % i
        sender = net.getNodeByName('h%d' % i)
        c = '%s %s %s %s &' % \
            (FTP_CLIENT, sender.IP(), max_window_list[i-1], sim_duration)
        print c
        recvr.cmd(c) 

def start_tcpprobe():
    """Install tcp_pobe module and dump to file"""
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

def write_to_log(logfile, wstring):
    f = open(logfile, 'a')
    f.write(wstring)
    f.close()

def init_log(logfile, wstring=None):
    if os.path.exists(logfile):
        os.remove(logfile)
    if wstring != None:
        write_to_log(logfile, wstring)

def list_mean(lst):
    return sum(lst)/float(len(lst))

def get_avg_qlen(filename):
    f = open(filename, 'r')
    l = []
    for line in f:
        l.append(int(line.strip().split(',')[1]))
    f.close()
    return list_mean(l)

def run_simulation_one():
    if not os.path.exists(SIM1_DIR):
        os.mkdir(SIM1_DIR)

    if not os.path.exists(QLENS_DIR):
        os.mkdir(QLENS_DIR)

    print T.colored('---------- Simulation 1 ----------', 'green')
    red_min_thresh = [PKT_SZ_BYTES*k for k in [3, 5, 7, 10, 15, 20, 25, 30, 35, 40, 50]]
    #dt_max_qlen = [k for k in [3, 5, 7, 10, 15, 20, 25, 30, 35, 40, 50]]
    dt_max_qlen = [k for k in [15, 30, 45, 60, 75, 90, 100, 110, 120, 130, 140]]
    #dt_max_qlen = [PKT_SZ_BYTES*k for k in [15, 30, 45, 60, 75, 90, 100, 110, 120, 130, 140]]
    nrun = 11
    """
    "Run RED simulation"
    logfile = '%s/redlog' % SIM1_DIR
    init_log(logfile, 'Throughput (Mbps), Avg. queue length\n')
    for i in range(0, nrun):
        print T.colored('Beginning RED run %d/%d' % (i+1, nrun), 'blue')
        max_buffer = 100*PKT_SZ_BYTES
        red_params = {'enable_red': True,
                      'red_limit': max_buffer,
                      'red_min': red_min_thresh[i],
                      'red_max': 3*red_min_thresh[i],
                      'red_avpkt': 1000,
                      'red_burst': (2*red_min_thresh[i]+3*red_min_thresh[i])/3000,
                      'red_prob': 1.0/50}
        topo = Fig6Topo(red_params=red_params)

        net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
        net.start()
        #dumpNetConnections(net)
        #net.pingAll()
        #verify_latency(net)

        monitor = Process(target=monitor_qlen,
                          args=('s1-eth0', 0.01, '%s/red%d.txt' % (QLENS_DIR, i)))
        monitor.start()

        start_senders(net, SIM1_N_SENDERS)
        start_receiver(net, SIM1_N_SENDERS, SIM1_LEN_SEC,
                       [SIM1_MAX_WINDOW]*SIM1_N_SENDERS)

        throughput = get_rates('s1-eth0', 4, period=1.0, wait=1.0)
        avg_qlen = get_avg_qlen('%s/red%d.txt' % (QLENS_DIR, i))
        write_to_log(logfile, str(list_mean(throughput)) + ',' +
                     str(avg_qlen) + '\n')
        monitor.terminate()
        net.stop()
    """
    "Run DropTail simulation"
    logfile = '%s/dtlog' % SIM1_DIR
    init_log(logfile, 'Throughput (Mbps), Avg. queue length\n')
    for i in range(0, nrun):
        print T.colored('Beginning DropTail run %d/%d' % (i+1, nrun), 'blue')
        red_params = {'enable_red': False,
                      'max_queue_size': dt_max_qlen[i]}
        topo = Fig6Topo(red_params=red_params)
        
        net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
        net.start()
        #dumpNetConnections(net)
        #net.pingAll()
        #verify_latency(net)

        monitor = Process(target=monitor_qlen,
                          args=('s1-eth0', 0.01, '%s/dt%d.txt' % (QLENS_DIR, i)))
        monitor.start()

        start_senders(net, SIM1_N_SENDERS)
        start_receiver(net, SIM1_N_SENDERS, SIM1_LEN_SEC,
                       [SIM1_MAX_WINDOW]*SIM1_N_SENDERS)


        throughput = get_rates('s1-eth0', 4, period=1.0, wait=1.0)
        avg_qlen = get_avg_qlen('%s/dt%d.txt' % (QLENS_DIR, i))
        write_to_log(logfile, str(list_mean(throughput)) + ',' +
                     str(avg_qlen) + '\n')
        monitor.terminate()
        net.stop()

    #    RED: max buffer size of  100 packets,
    #         min_th ranging from 3 to 50 packets
    #         max_th := 3*min_th
    #         w_q := 0.002
    #         max_p := 1/50

def run_simulation_two():
    pass

def main():
    "Parse command line args"
    parser = ArgumentParser(description='RED experiments')
    parser.add_argument('--sim1',
                        action='store_true',
                        help='Run Simulation 1')
    parser.add_argument('--sim2',
                        action='store_true',
                        help='Run Simulation 2')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Run debugging test')
    args = parser.parse_args()

    if not args.sim1 and not args.sim2 and not args.debug:
        print T.colored('You forgot to specify a simulation to run.\n' +
                        'Usage: red_simulation.py [-h] [--sim1] [--sim2]',
			'green')

    if not os.path.exists(FTP_SERVER) or not os.path.exists(FTP_CLIENT):
        sys.exit('Error: Executable %s missing' % FTP_SERVER)

    "Run simulations"
    if args.debug:
        run_debug()
    if args.sim1:
        run_simulation_one()
    if args.sim2:
        run_simulation_two()

if __name__ =='__main__':
    main()
