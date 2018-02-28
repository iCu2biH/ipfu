#!/usr/bin/python

import logging, time, os, sys, inspect, socket, nfqueue, ipcalc, struct
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)	# prevent scapy warnings for ipv6
sys.path.append("./libs")
from mixins import *

from scapy import all as scapy
from netaddr import IPAddress

scapy.conf.verb = 0


# gwscan module
class gwscan(GetMacsMixin, loggerMixin):
	def __init__(self, params):
		if len(params) != 2:
			self.usage()
			exit(1)

		self.net = params[0]
		self.ip = params[1]

	def usage(self):
		print "Usage:"
		print "\t%s ether.gwscan <local_subnet> <target_ip/net>" % sys.argv[0]
		print "examples:"
		print "\t%s gwscan 192.168.1.0/24 8.8.8.8" % sys.argv[0]
		print "\t%s gwscan 192.168.1.0/24 10.0.0.0/24" % sys.argv[0]

	def start(self):
		ret = self.gwscan_icmp(self.net, self.ip)
		for x in ret:
			print "%18s %16s %16s" % (x['gw_mac'], x['gw_ip'], x['r_ip'])

	def gwscan_icmp(self, net, ip):
		self.msg('gwscan for net %s, searching gw for %s' %(net, ip))
		lt = self.getmacs(net)
		#ans,unans = scapy.srp(scapy.Ether(dst='ff:ff:ff:ff:ff:ff') / scapy.IP(dst=ip) / scapy.ICMP(), timeout=5)
		pkt = scapy.Ether(dst=lt['mac_ip'].keys())
		pkt/= scapy.IP(dst=ip)
		pkt/= scapy.ICMP()
		ans,unans = scapy.srp( pkt, timeout=5)
		ret = []
		for b in ans:
			for a in b[1]:
				if a[scapy.ICMP].type == 0 and a[scapy.ICMP].code == 0:
					mac = a[scapy.Ether].src
					r_ip = a[scapy.IP].src
					ip = lt['mac_ip'][mac]
					ret.append({
						'ttype':	'ping',
						'gw_mac':	mac,
						'gw_ip':	ip,
						'r_ip':		r_ip
					})
		self.msg('gwscan finished')
		return ret