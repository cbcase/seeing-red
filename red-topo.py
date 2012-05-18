from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNetConnections

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

def verify_latency(net):
    sink = net.getNodeByName('sink');
    for i in range(1, 5):
        host = net.getNodeByName('h%d' % i)
        result = host.cmd('ping -c 3 %s' % sink.IP())
        print 'h%d --> sink' % i
        print result

def verify_bandwidth(net):
    sink = net.getNodeByName('sink')
    for i in range(1, 5):
        host = net.getNodeByName('h%d' % i)
        net.iperf([host, sink])

def main():
    topo = Fig4Topo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNetConnections(net)
    net.pingAll()

    verify_latency(net)
    verify_bandwidth(net)

    net.stop()

if __name__ =='__main__':
    main()
