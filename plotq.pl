#!/usr/bin/perl

for my $i (0..10) {
    for my $type ("red", "dt") {
	`python util/plot_queue.py -f qlens/$type$i.txt -o qplots/$type$i.png`
    }
}
