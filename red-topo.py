from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNetConnections

import sys
import os
from time import sleep, time
from subprocess import Popen, PIPE

class Fig4Topo(Topo):
    "Topology from figure 4 of RED paper"

    def __init__(self):
        Topo.__init__(self);

        l1config = {'bw': 100, 'delay': '1ms', 'max_queue_size': None }
        l2config = {'bw': 100, 'delay': '4ms', 'max_queue_size': None }
        l3config = {'bw': 100, 'delay': '8ms', 'max_queue_size': None }
        l4config = {'bw': 100, 'delay': '5ms', 'max_queue_size': None }
        l6config = {'bw': 45, 'delay': '2ms', 'max_queue_size': None }

        hconfig = {'cpu': None}

        s1 = self.add_switch('s1')
        h1 = self.add_host('h1', **hconfig);
        h2 = self.add_host('h2', **hconfig);
        h3 = self.add_host('h3', **hconfig);
        h4 = self.add_host('h4', **hconfig);
        sink = self.add_host('sink', **hconfig);

        self.add_link(h1, s1,
                      port1=0, port2=1, **l1config);
        self.add_link(h2, s1,
                      port1=0, port2=2, **l2config);
        self.add_link(h3, s1,
                      port1=0, port2=3, **l3config);
        self.add_link(h4, s1,
                      port1=0, port2=4, **l4config);
        self.add_link(s1, sink,
                       port1=0, port2=0, **l6config);

    def numSources(self):
        return 4

class Fig6Topo(Topo):
    def __init__(self):
        Topo.__init__(self)
        src_lconfig = {'bw': 100, 'delay': '1ms', 'max_queue_size': None,
		       'enable_red': True, 'red_min': 20000, 'red_max': 25000,
		       'red_avpkt': 1000, 'red_burst': 20, 'red_prob': 1}
        dst_lconfig = {'bw': 45, 'delay': '20ms', 'max_queue_size': None,
		       'enable_red': True, 'red_min': 20000, 'red_max': 25000,
		       'red_avpkt': 1000, 'red_burst': 20, 'red_prob': 1}

        hconfig = {'cpu': None, 'enable_red': True}

        s1 = self.add_switch('s1')
        # hosts 1..2
        for i in range(1, 3):
            host = self.add_host('h%d' % i, **hconfig)
            self.add_link(host, s1, port1=0, port2=i, **src_lconfig)

        sink = self.add_host('sink', **hconfig)
        self.add_link(s1, sink, port1=0, port2=0, **dst_lconfig)

    def numSources(self):
        return 2

class Fig11Topo(Topo):
    def __init__(self):
        Topo.__init__(self)
        l1config = {'bw': 100, 'delay': '1ms', 'max_queue_size': None }
        l2config = {'bw': 45, 'delay': '16ms', 'max_queue_size': None }
        l3config = {'bw': 45, 'delay': '2ms', 'max_queue_size': None }

        hconfig = {'cpu': None }
        s1 = self.add_switch('s1')
        # hosts 1..4
        for i in range(1, 5):
            host = self.add_host('h%d' % i, **hconfig)
            self.add_link(host, s1, port1=0,
                          port2=i, **l1config)
        # host 5
        h5 = self.add_host('h5', **hconfig)
        self.add_link(h5, s1, port1=0, port2=5, **l2config)

        # sink
        sink = self.add_host('sink', **hconfig)
        self.add_link(s1, sink, port1=0, port2=0, **l3config)

    def numSources(self):
        return 5

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


def main():
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
    #Popen("killall -9 top bwm-ng tcpdump cat", shell=True).wait()
    #stop_tcpprobe()
    #os.system('killall -9 ' + CUSTOM_IPERF_PATH)
    #os.system("tc qdisc change dev s1-eth0 root red limit 1000000 min 10000 max 100000 avpkt 1000 burst 15 probability 0.01")
    #os.system("tc qdisc show")

    net.stop()

if __name__ =='__main__':
    main()
