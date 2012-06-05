from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink, TCIntf, Link
from mininet.util import dumpNetConnections

import sys
import os
from time import sleep, time
from subprocess import Popen, PIPE

#High simulation bandwdith, in Mbps
BW_HIGH = 100

#Low simulation bandwidth, in Mbps
BW_LOW = 45

#Default options to pass to tc-red; as specified originally in link.py
DEFAULT_RED_PARAMS = {'enable_red': True, 'red_limit': 1000000,
		      'red_min': 20000, 'red_max': 25000, 'red_avpkt': 1000,
		      'red_burst': 20, 'red_prob': 1.0}


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

class BurstTestTopo(Topo):
    "Topology to test our bursty traffic generator"
    def __init__(self, red_params=DEFAULT_RED_PARAMS):
        Topo.__init__(self)
	src_lconfig = {'bw': BW_LOW, 'delay': '16ms', 'max_queue_size': None}
	dst_lconfig = {'bw': BW_LOW, 'delay': '2ms', 'max_queue_size': None}
        switch_lconfig = dst_lconfig.copy()
        switch_lconfig.update(red_params)
        hconfig = {'cpu': None}

        s1 = self.add_switch('s1')

        host = self.add_host('h1', **hconfig)
        self.add_link(host, s1, port1=0, port2=1, **src_lconfig)

        sink = self.add_host('sink', **hconfig)
        self.add_link(s1, sink, cls=Link, port1=0, port2=0,
                      cls1=TCIntf, cls2=TCIntf,
                      params1=switch_lconfig, params2=dst_lconfig)
    def numSources(self):
        return 1

class Fig6Topo(Topo):
    def __init__(self, red_params=DEFAULT_RED_PARAMS):
        Topo.__init__(self)
	
	src_lconfig = {'bw': BW_HIGH, 'delay': '1ms', 'max_queue_size': None}

	dst_lconfig = {'bw': BW_LOW, 'delay': '20ms', 'max_queue_size': None}
        switch_lconfig = dst_lconfig.copy()
        switch_lconfig.update(red_params)

        hconfig = {'cpu': None}

        s1 = self.add_switch('s1')
        # hosts 1..2
        for i in range(1, 3):
            host = self.add_host('h%d' % i, **hconfig)
            self.add_link(host, s1, port1=0, port2=i, **src_lconfig)

        sink = self.add_host('sink', **hconfig)
        self.add_link(s1, sink, cls=Link, port1=0, port2=0,
                      cls1=TCIntf, cls2=TCIntf,
                      params1=switch_lconfig, params2=dst_lconfig)
                      

    def numSources(self):
        return 2

class Fig11Topo(Topo):
    def __init__(self, red_params=DEFAULT_RED_PARAMS):
        Topo.__init__(self)

        l1config = {'bw': BW_HIGH, 'delay': '1ms', 'max_queue_size': None }

        l2config = {'bw': BW_LOW, 'delay': '16ms', 'max_queue_size': None }

        dst_lconfig = {'bw': BW_LOW, 'delay': '2ms', 'max_queue_size': None }
        switch_lconfig = dst_lconfig.copy()
        switch_lconfig.update(red_params)

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
        self.add_link(s1, sink, cls=Link, port1=0, port2=0,
                      cls1=TCIntf, cls2=TCIntf,
                      params1=switch_lconfig, params2=dst_lconfig)

        #self.add_link(s1, sink, port1=0, port2=0, **l3config)

    def numSources(self):
        return 5

